from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from loguru import logger
import atexit
import requests
import hashlib

# Lokale Module importieren
from .scraper import DocumentScraper
from .newsletter_generator import NewsletterGenerator
from .analyzer import DocumentAnalyzer
from .models import db, Document, DocumentChange, Newsletter, User 
from .email_service import EmailService
from .config import Config

class TaskScheduler:
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler(daemon=True)
        self.app = app
        self.scraper = None
        self.newsletter_generator = None
        self.email_service = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        with app.app_context():
            self.scraper = DocumentScraper(app.config['SOURCES'])
            # HIER IST DIE KORREKTUR:
            self.newsletter_generator = NewsletterGenerator()
            self.email_service = EmailService(app)

            self._add_scraping_job()
            self._add_newsletter_generation_job()
            self._add_cleanup_job()

    def start_scheduler(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Task Scheduler gestartet")
            atexit.register(lambda: self.scheduler.shutdown())

    def get_job_status(self):
        jobs_info = []
        if self.scheduler.running:
            for job in self.scheduler.get_jobs():
                jobs_info.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z') if job.next_run_time else 'N/A',
                    'trigger': str(job.trigger)
                })
        return {
            'scheduler_running': self.scheduler.running,
            'jobs': jobs_info
        }

    def _add_scraping_job(self):
        interval = self.app.config.get('SCRAPING_INTERVAL_HOURS', 24)
        self.scheduler.add_job(
            self._run_scraping_task,
            'interval',
            hours=interval,
            id='scraping_job',
            name='Regelmäßiges Scraping',
            replace_existing=True
        )
        logger.info(f"Scraping-Job hinzugefügt (alle {interval} Stunden)")

    def _add_newsletter_generation_job(self):
        interval = self.app.config.get('NEWSLETTER_GENERATION_INTERVAL_HOURS', 168)
        self.scheduler.add_job(
            self._run_newsletter_generation_task,
            'interval',
            hours=interval,
            id='newsletter_job',
            name='Regelmäßige Newsletter-Generierung',
            replace_existing=True
        )
        logger.info(f"Newsletter-Job hinzugefügt (alle {interval} Stunden)")
    
    def _add_cleanup_job(self):
        self.scheduler.add_job(
            self._run_cleanup_task,
            CronTrigger(hour=2, minute=0),
            id='cleanup_job',
            name='Tägliche Datenbereinigung',
            replace_existing=True
        )
        logger.info("Cleanup-Job hinzugefügt (täglich um 2:00 Uhr)")

    def _run_scraping_task(self):
        with self.app.app_context():
            logger.info("Starte Scraping-Aufgabe...")
            existing_docs = {doc.url: doc.content_hash for doc in Document.query.all()}
            scraped_docs = self.scraper.scrape_all_sources()
            
            new_docs_count = 0
            changed_docs_count = 0

            for doc_data in scraped_docs:
                url = doc_data['url']
                title = doc_data['title']
                source = doc_data['source']
                
                try:
                    response = requests.get(url, headers=self.scraper.session.headers, timeout=30)
                    response.raise_for_status()
                    content = response.text
                    new_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

                    if url not in existing_docs:
                        new_doc = Document(source=source, url=url, title=title, content_hash=new_hash, last_checked=datetime.utcnow())
                        db.session.add(new_doc)
                        new_docs_count += 1
                        logger.info(f"Neues Dokument gefunden: {title}")

                    elif existing_docs[url] != new_hash:
                        existing_doc = Document.query.filter_by(url=url).first()
                        if existing_doc:
                            # Simplifizierte Annahme für den alten Inhalt
                            old_content = "" # In einer echten App müsste man den alten Inhalt speichern/abrufen
                            analyzer = DocumentAnalyzer()
                            change_info = analyzer.compare_documents(old_content, content)
                            
                            new_change = DocumentChange(document_id=existing_doc.id, change_summary=change_info['diff_summary'], importance_score=change_info['importance_score'])
                            db.session.add(new_change)
                            
                            existing_doc.content_hash = new_hash
                            existing_doc.last_checked = datetime.utcnow()
                            changed_docs_count += 1
                            logger.info(f"Änderung im Dokument gefunden: {title}")

                except Exception as e:
                    logger.error(f"Fehler bei der Verarbeitung von {url}: {e}")

            db.session.commit()
            logger.info(f"Scraping abgeschlossen: {new_docs_count} neue Dokumente, {changed_docs_count} Änderungen erkannt")

    def _run_newsletter_generation_task(self):
        with self.app.app_context():
            logger.info("Starte Newsletter-Generierung...")
            unprocessed_changes = DocumentChange.query.filter_by(processed=False).all()
            if not unprocessed_changes:
                logger.info("Keine neuen Änderungen für Newsletter vorhanden")
                return

            try:
                newsletter_content = self.newsletter_generator.generate_html(unprocessed_changes)
                if not newsletter_content['html']:
                    logger.warning("Newsletter-Generierung hat leeren Inhalt erzeugt.")
                    return

                active_users = User.query.filter_by(is_admin=False).all() # Annahme: Nur Nicht-Admins sind Abonnenten
                if not active_users:
                    logger.info("Keine aktiven Empfänger für den Newsletter gefunden.")
                    return
                
                recipient_emails = [user.email for user in active_users]

                new_newsletter = Newsletter(
                    title=f"Medizintechnik Update - {datetime.now().strftime('%d.%m.%Y')}",
                    content_html=newsletter_content['html'],
                    content_text=newsletter_content['text'],
                    recipient_count=len(recipient_emails)
                )
                db.session.add(new_newsletter)

                for email in recipient_emails:
                    self.email_service.send_newsletter({
                        'title': new_newsletter.title,
                        'html_content': new_newsletter.content_html,
                        'text_content': new_newsletter.content_text
                    }, email)
                
                for change in unprocessed_changes:
                    change.processed = True

                new_newsletter.sent_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"Newsletter erfolgreich an {len(recipient_emails)} Empfänger gesendet.")

            except Exception as e:
                db.session.rollback()
                logger.error(f"Fehler bei Newsletter-Generierung: {e}")
                self.email_service.send_admin_notification(
                    subject="Newsletter-Generierung fehlgeschlagen",
                    message=f"Ein Fehler ist aufgetreten: {e}"
                )

    def _run_cleanup_task(self):
        with self.app.app_context():
            try:
                one_month_ago = datetime.utcnow() - timedelta(days=30)
                old_changes = DocumentChange.query.filter(
                    DocumentChange.processed == True,
                    DocumentChange.detected_at < one_month_ago
                ).delete()
                db.session.commit()
                if old_changes > 0:
                    logger.info(f"{old_changes} alte Änderungen wurden bereinigt.")
            except Exception as e:
                logger.error(f"Fehler bei der Datenbereinigung: {e}")

    # Manuelle Trigger
    def run_manual_scraping(self):
        logger.info("Starte manuelles Scraping...")
        self.scheduler.add_job(self._run_scraping_task, 'date', run_date=datetime.now(), id='manual_scraping_now', replace_existing=True)

    def run_manual_newsletter_generation(self):
        logger.info("Starte manuelle Newsletter-Generierung...")
        self.scheduler.add_job(self._run_newsletter_generation_task, 'date', run_date=datetime.now(), id='manual_newsletter_now', replace_existing=True)
