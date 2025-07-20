"""Modul für die Aufgabenplanung und -ausführung."""
import atexit
import hashlib
from datetime import datetime, timedelta

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

# Lokale Module importieren
from .analyzer import DocumentAnalyzer
from .email_service import EmailService
from .models import Document, DocumentChange, Newsletter, User, db
from .newsletter_generator import NewsletterGenerator
from .scraper import DocumentScraper


class TaskScheduler:
    """Verwaltet die Planung und Ausführung von Hintergrundaufgaben wie Scraping und Newsletter-Generierung."""

    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler(daemon=True)
        self.app = app
        self.scraper = None
        self.newsletter_generator = None
        self.email_service = None
        self.document_analyzer = DocumentAnalyzer()  # Initialisiere den Analyzer einmal
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialisiert den Scheduler mit der Flask-Anwendung."""
        self.app = app
        with app.app_context():
            self.scraper = DocumentScraper(app.config["SOURCES"])
            self.newsletter_generator = NewsletterGenerator()
            self.email_service = EmailService(app)

            self._add_scraping_job()
            self._add_newsletter_generation_job()
            self._add_cleanup_job()

    def start_scheduler(self):
        """Startet den APScheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Task Scheduler gestartet")
            atexit.register(self.scheduler.shutdown)

    def get_job_status(self):
        """Gibt den Status der geplanten Jobs zurück."""
        jobs_info = []
        if self.scheduler.running:
            for job in self.scheduler.get_jobs():
                jobs_info.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.strftime("%Y-%m-%d %H:%M:%S %Z") 
                    if job.next_run_time else "N/A",
                    "trigger": str(job.trigger)
                })
        return {
            "scheduler_running": self.scheduler.running,
            "jobs": jobs_info
        }

    def _add_scraping_job(self):
        """Fügt den regelmäßigen Scraping-Job hinzu."""
        interval = self.app.config.get("SCRAPING_INTERVAL_HOURS", 24)
        self.scheduler.add_job(
            self._run_scraping_task,
            "interval",
            hours=interval,
            id="scraping_job",
            name="Regelmäßiges Scraping",
            replace_existing=True
        )
        logger.info(f"Scraping-Job hinzugefügt (alle {interval} Stunden)")

    def _add_newsletter_generation_job(self):
        """Fügt den regelmäßigen Newsletter-Generierungs-Job hinzu."""
        interval = self.app.config.get("NEWSLETTER_GENERATION_INTERVAL_HOURS", 168)
        self.scheduler.add_job(
            self._run_newsletter_generation_task,
            "interval",
            hours=interval,
            id="newsletter_job",
            name="Regelmäßige Newsletter-Generierung",
            replace_existing=True
        )
        logger.info(f"Newsletter-Job hinzugefügt (alle {interval} Stunden)")

    def _add_cleanup_job(self):
        """Fügt den täglichen Datenbereinigungs-Job hinzu."""
        self.scheduler.add_job(
            self._run_cleanup_task,
            CronTrigger(hour=2, minute=0),
            id="cleanup_job",
            name="Tägliche Datenbereinigung",
            replace_existing=True
        )
        logger.info("Cleanup-Job hinzugefügt (täglich um 2:00 Uhr)")

    def _process_single_document(self, doc_data, existing_docs):
        url = doc_data["url"]
        title = doc_data["title"]
        source = doc_data["source"]
        
        new_doc_added = False
        doc_changed = False

        try:
            response = requests.get(url, headers=self.scraper.session.headers, timeout=30)
            response.raise_for_status()
            content = response.text
            new_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

            if url not in existing_docs:
                new_doc = Document(source=source, url=url, title=title, 
                                   content_hash=new_hash, last_checked=datetime.utcnow())
                db.session.add(new_doc)
                new_doc_added = True
                logger.info(f"Neues Dokument gefunden: {title}")

            elif existing_docs[url] != new_hash:
                existing_doc = Document.query.filter_by(url=url).first()
                if existing_doc:
                    change_info = self.document_analyzer.compare_documents("", content)  

                    new_change = DocumentChange(document_id=existing_doc.id, 
                                                change_summary=change_info["diff_summary"], 
                                                importance_score=change_info["importance_score"])
                    db.session.add(new_change)

                    existing_doc.content_hash = new_hash
                    existing_doc.last_checked = datetime.utcnow()
                    doc_changed = True
                    logger.info(f"Änderung im Dokument gefunden: {title}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Netzwerk- oder HTTP-Fehler bei {url}: {e}")
        except Exception as e:
            logger.error(f"Allgemeiner Fehler bei der Verarbeitung von {url}: {e}")
        
        return new_doc_added, doc_changed

    def _run_scraping_task(self):
        """Führt die Scraping-Aufgabe aus, um neue Dokumente zu finden und Änderungen zu erkennen."""
        with self.app.app_context():
            logger.info("Starte Scraping-Aufgabe...")
            existing_docs = {doc.url: doc.content_hash for doc in Document.query.all()}
            scraped_docs = self.scraper.scrape_all_sources()

            new_docs_count = 0
            changed_docs_count = 0

            for doc_data in scraped_docs:
                new_added, changed = self._process_single_document(doc_data, existing_docs)
                if new_added:
                    new_docs_count += 1
                if changed:
                    changed_docs_count += 1

            db.session.commit()
            logger.info(f"Scraping abgeschlossen: {new_docs_count} neue Dokumente, "
                        f"{changed_docs_count} Änderungen erkannt")

    def _run_newsletter_generation_task(self):
        """Generiert und versendet Newsletter an Abonnenten."""
        with self.app.app_context():
            logger.info("Starte Newsletter-Generierung...")
            unprocessed_changes = DocumentChange.query.filter_by(processed=False).all()
            if not unprocessed_changes:
                logger.info("Keine neuen Änderungen für Newsletter vorhanden")
                return

            try:
                # Abonnenten abrufen
                active_users = User.query.filter_by(is_admin=False).all()  
                if not active_users:
                    logger.info("Keine aktiven Empfänger für den Newsletter gefunden.")
                    return

                # Generiere personalisierte Newsletter für jeden Abonnenten
                generated_newsletters = self.newsletter_generator.generate_personalized_newsletters(
                    unprocessed_changes,
                    [{
                        "id": user.id,
                        "email": user.email,
                        "name": user.first_name,
                        "interests": []  # Vereinfacht, Interessen müssten aus User-Modell kommen
                    } for user in active_users]
                )

                for nl_data in generated_newsletters:
                    new_newsletter = Newsletter(
                        title=nl_data["title"],
                        content_html=nl_data["html_content"],
                        content_text=nl_data["text_content"],
                        recipient_count=1  # Da es ein personalisierter Newsletter ist
                    )
                    db.session.add(new_newsletter)
                    db.session.flush()  # Stellt sicher, dass die ID verfügbar ist

                    # Sende den Newsletter an den jeweiligen Abonnenten
                    self.email_service.send_newsletter(
                        newsletter=nl_data,
                        recipient_email=nl_data["subscriber"]["email"],
                        recipient_name=nl_data["subscriber"]["name"]
                    )

                for change in unprocessed_changes:
                    change.processed = True

                db.session.commit()
                logger.info(f"Newsletter erfolgreich an {len(generated_newsletters)} Empfänger gesendet.")

            except Exception as e:
                db.session.rollback()
                logger.error(f"Fehler bei Newsletter-Generierung: {e}")
                # Hier müsste eine Admin-Benachrichtigung implementiert werden, falls gewünscht
                # self.email_service.send_admin_notification(
                #     subject="Newsletter-Generierung fehlgeschlagen",
                #     message=f"Ein Fehler ist aufgetreten: {e}"
                # )

    def _run_cleanup_task(self):
        """Bereinigt alte, verarbeitete Dokumentenänderungen aus der Datenbank."""
        with self.app.app_context():
            try:
                one_month_ago = datetime.utcnow() - timedelta(days=30)
                old_changes = DocumentChange.query.filter(
                    DocumentChange.processed is True,
                    DocumentChange.detected_at < one_month_ago
                ).delete()
                db.session.commit()
                if old_changes > 0:
                    logger.info(f"{old_changes} alte Änderungen wurden bereinigt.")
            except Exception as e:
                logger.error(f"Fehler bei der Datenbereinigung: {e}")

    # Manuelle Trigger
    def run_manual_scraping(self):
        """Löst ein manuelles Scraping aus."""
        logger.info("Starte manuelles Scraping...")
        self.scheduler.add_job(self._run_scraping_task, "date", 
                               run_date=datetime.now(), id="manual_scraping_now", 
                               replace_existing=True)

    def run_manual_newsletter_generation(self):
        """Löst eine manuelle Newsletter-Generierung aus."""
        logger.info("Starte manuelle Newsletter-Generierung...")
        self.scheduler.add_job(self._run_newsletter_generation_task, "date", 
                               run_date=datetime.now(), id="manual_newsletter_now", 
                               replace_existing=True)
