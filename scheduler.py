from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
import atexit

from scraper import DocumentScraper
from analyzer import DocumentAnalyzer
from newsletter_generator import NewsletterGenerator
from email_service import EmailService
from models import db, Document, DocumentChange, Newsletter, Subscriber

class TaskScheduler:
    """Scheduler für automatisierte Aufgaben des Newsletter-Systems"""
    
    def __init__(self, app=None, config=None):
        self.app = app
        self.config = config
        self.scheduler = BackgroundScheduler()
        self.scraper = None
        self.analyzer = None
        self.newsletter_generator = None
        self.email_service = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialisiert den Scheduler mit der Flask-App"""
        self.app = app
        self.config = app.config
        
        # Initialisiere Services
        self.scraper = DocumentScraper(self.config)
        self.analyzer = DocumentAnalyzer()
        self.newsletter_generator = NewsletterGenerator()
        self.email_service = EmailService(app, self.config)
        
        # Registriere Shutdown-Handler
        atexit.register(self._safe_shutdown)
    
    def _safe_shutdown(self):
        """Sicheres Herunterfahren des Schedulers"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
        except Exception:
            pass  # Ignoriere Fehler beim Shutdown
    
    def start_scheduler(self):
        """Startet den Scheduler mit allen konfigurierten Jobs"""
        if self.scheduler.running:
            logger.warning("Scheduler läuft bereits")
            return
        
        # Füge Jobs hinzu
        self._add_scraping_job()
        self._add_newsletter_generation_job()
        self._add_cleanup_job()
        
        # Starte Scheduler
        self.scheduler.start()
        logger.info("Task Scheduler gestartet")
    
    def stop_scheduler(self):
        """Stoppt den Scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Task Scheduler gestoppt")
    
    def _add_scraping_job(self):
        """Fügt den Scraping-Job hinzu"""
        interval_hours = self.config.get('SCRAPING_INTERVAL_HOURS', 24)
        
        self.scheduler.add_job(
            func=self._run_scraping_task,
            trigger=IntervalTrigger(hours=interval_hours),
            id='scraping_job',
            name='Document Scraping',
            replace_existing=True,
            max_instances=1
        )
        
        logger.info(f"Scraping-Job hinzugefügt (alle {interval_hours} Stunden)")
    
    def _add_newsletter_generation_job(self):
        """Fügt den Newsletter-Generierungs-Job hinzu"""
        interval_hours = self.config.get('NEWSLETTER_GENERATION_INTERVAL_HOURS', 168)  # Wöchentlich
        
        self.scheduler.add_job(
            func=self._run_newsletter_generation_task,
            trigger=IntervalTrigger(hours=interval_hours),
            id='newsletter_job',
            name='Newsletter Generation',
            replace_existing=True,
            max_instances=1
        )
        
        logger.info(f"Newsletter-Job hinzugefügt (alle {interval_hours} Stunden)")
    
    def _add_cleanup_job(self):
        """Fügt den Cleanup-Job hinzu"""
        # Läuft täglich um 2:00 Uhr
        self.scheduler.add_job(
            func=self._run_cleanup_task,
            trigger=CronTrigger(hour=2, minute=0),
            id='cleanup_job',
            name='Database Cleanup',
            replace_existing=True,
            max_instances=1
        )
        
        logger.info("Cleanup-Job hinzugefügt (täglich um 2:00 Uhr)")
    
    def _run_scraping_task(self):
        """Führt die Scraping-Aufgabe aus"""
        logger.info("Starte Scraping-Aufgabe...")
        
        try:
            with self.app.app_context():
                # Scrape alle Quellen
                scraped_documents = self.scraper.scrape_all_sources()
                
                changes_detected = 0
                new_documents = 0
                
                for doc_data in scraped_documents:
                    # Prüfe ob Dokument bereits existiert
                    existing_doc = Document.query.filter_by(url=doc_data['url']).first()
                    
                    if existing_doc:
                        # Prüfe auf Änderungen
                        if existing_doc.content_hash != doc_data['content_hash']:
                            # Analysiere Änderungen
                            change_analysis = self.analyzer.compare_documents(
                                existing_doc.content,
                                doc_data['content']
                            )
                            
                            # Erstelle DocumentChange Eintrag
                            doc_change = DocumentChange(
                                document_id=existing_doc.id,
                                change_type=change_analysis['change_type'],
                                change_summary=change_analysis['diff_summary'],
                                old_content_hash=existing_doc.content_hash,
                                new_content_hash=doc_data['content_hash'],
                                diff_data=change_analysis['detailed_changes']
                            )
                            
                            # Aktualisiere Dokument
                            existing_doc.content = doc_data['content']
                            existing_doc.content_hash = doc_data['content_hash']
                            existing_doc.last_checked = datetime.utcnow()
                            existing_doc.last_modified = datetime.utcnow()
                            existing_doc.doc_metadata = doc_data['metadata']
                            
                            db.session.add(doc_change)
                            changes_detected += 1
                        else:
                            # Nur last_checked aktualisieren
                            existing_doc.last_checked = datetime.utcnow()
                    else:
                        # Neues Dokument
                        new_doc = Document(
                            source=doc_data['source'],
                            title=doc_data['title'],
                            url=doc_data['url'],
                            content=doc_data['content'],
                            content_hash=doc_data['content_hash'],
                            doc_metadata=doc_data['metadata']
                        )
                        
                        db.session.add(new_doc)
                        new_documents += 1
                
                # Speichere Änderungen
                db.session.commit()
                
                logger.info(f"Scraping abgeschlossen: {new_documents} neue Dokumente, {changes_detected} Änderungen erkannt")
                
                # Sende Admin-Benachrichtigung bei wichtigen Änderungen
                if changes_detected > 0:
                    self.email_service.send_admin_notification(
                        "Neue Regulierungsänderungen erkannt",
                        f"Das System hat {changes_detected} Änderungen in überwachten Dokumenten erkannt. "
                        f"Zusätzlich wurden {new_documents} neue Dokumente gefunden."
                    )
                
        except Exception as e:
            logger.error(f"Fehler bei Scraping-Aufgabe: {e}")
            self.email_service.send_admin_notification(
                "Fehler beim Scraping",
                f"Bei der automatischen Datenerfassung ist ein Fehler aufgetreten: {str(e)}"
            )
    
    def _run_newsletter_generation_task(self):
        """Führt die Newsletter-Generierungs-Aufgabe aus"""
        logger.info("Starte Newsletter-Generierung...")
        
        try:
            with self.app.app_context():
                # Hole unverarbeitete Änderungen
                unprocessed_changes = DocumentChange.query.filter_by(processed=False).all()
                
                if not unprocessed_changes:
                    logger.info("Keine neuen Änderungen für Newsletter vorhanden")
                    return
                
                # Bereite Änderungsdaten für Newsletter vor
                changes_data = []
                for change in unprocessed_changes:
                    document = change.document
                    
                    # Analysiere Dokument-Inhalt
                    key_info = self.analyzer.extract_key_information(
                        document.content,
                        document.doc_metadata
                    )
                    
                    change_data = {
                        'id': change.id,
                        'title': document.title,
                        'source': document.source,
                        'url': document.url,
                        'change_type': change.change_type,
                        'change_summary': change.change_summary,
                        'detected_at': change.detected_at.isoformat(),
                        'importance_score': key_info['importance_score'],
                        'key_topics': key_info['key_topics'],
                        'regulations': key_info['regulations'],
                        'standards': key_info['standards'],
                        'dates': key_info['dates'],
                        'change_indicators': key_info['change_indicators']
                    }
                    
                    changes_data.append(change_data)
                
                # Hole aktive Abonnenten
                active_subscribers = Subscriber.query.filter_by(is_active=True).all()
                
                if not active_subscribers:
                    logger.warning("Keine aktiven Abonnenten vorhanden")
                    return
                
                # Generiere personalisierte Newsletter
                newsletters = self.newsletter_generator.generate_personalized_newsletters(
                    changes_data,
                    [sub.to_dict() for sub in active_subscribers]
                )
                
                # Sende Newsletter
                send_results = self.email_service.send_newsletters_batch(newsletters)
                
                # Speichere Newsletter in Datenbank
                for newsletter in newsletters:
                    db_newsletter = Newsletter(
                        title=newsletter['title'],
                        content_html=newsletter['html_content'],
                        content_text=newsletter['text_content'],
                        changes_included=[change['id'] for change in changes_data],
                        sent_at=datetime.utcnow(),
                        recipient_count=1
                    )
                    db.session.add(db_newsletter)
                
                # Markiere Änderungen als verarbeitet
                for change in unprocessed_changes:
                    change.processed = True
                
                db.session.commit()
                
                logger.info(f"Newsletter-Generierung abgeschlossen: {send_results['sent']} gesendet, {send_results['failed']} fehlgeschlagen")
                
                # Sende Admin-Benachrichtigung
                self.email_service.send_admin_notification(
                    "Newsletter versendet",
                    f"Newsletter wurden erfolgreich generiert und versendet.\n"
                    f"Erfolgreich: {send_results['sent']}\n"
                    f"Fehlgeschlagen: {send_results['failed']}\n"
                    f"Änderungen verarbeitet: {len(unprocessed_changes)}"
                )
                
        except Exception as e:
            logger.error(f"Fehler bei Newsletter-Generierung: {e}")
            self.email_service.send_admin_notification(
                "Fehler bei Newsletter-Generierung",
                f"Bei der Newsletter-Generierung ist ein Fehler aufgetreten: {str(e)}"
            )
    
    def _run_cleanup_task(self):
        """Führt Cleanup-Aufgaben aus"""
        logger.info("Starte Cleanup-Aufgabe...")
        
        try:
            with self.app.app_context():
                # Lösche alte Newsletter (älter als 6 Monate)
                six_months_ago = datetime.utcnow() - timedelta(days=180)
                old_newsletters = Newsletter.query.filter(
                    Newsletter.generated_at < six_months_ago
                ).all()
                
                for newsletter in old_newsletters:
                    db.session.delete(newsletter)
                
                # Lösche verarbeitete Änderungen (älter als 3 Monate)
                three_months_ago = datetime.utcnow() - timedelta(days=90)
                old_changes = DocumentChange.query.filter(
                    DocumentChange.detected_at < three_months_ago,
                    DocumentChange.processed == True
                ).all()
                
                for change in old_changes:
                    db.session.delete(change)
                
                # Lösche inaktive Abonnenten (älter als 1 Jahr)
                one_year_ago = datetime.utcnow() - timedelta(days=365)
                inactive_subscribers = Subscriber.query.filter(
                    Subscriber.updated_at < one_year_ago,
                    Subscriber.is_active == False
                ).all()
                
                for subscriber in inactive_subscribers:
                    db.session.delete(subscriber)
                
                db.session.commit()
                
                logger.info(f"Cleanup abgeschlossen: {len(old_newsletters)} Newsletter, {len(old_changes)} Änderungen, {len(inactive_subscribers)} Abonnenten gelöscht")
                
        except Exception as e:
            logger.error(f"Fehler bei Cleanup-Aufgabe: {e}")
    
    def run_manual_scraping(self):
        """Führt manuelles Scraping aus"""
        logger.info("Starte manuelles Scraping...")
        self._run_scraping_task()
    
    def run_manual_newsletter_generation(self):
        """Führt manuelle Newsletter-Generierung aus"""
        logger.info("Starte manuelle Newsletter-Generierung...")
        self._run_newsletter_generation_task()
    
    def get_job_status(self) -> Dict:
        """Gibt den Status aller Jobs zurück"""
        jobs = self.scheduler.get_jobs()
        
        status = {
            'scheduler_running': self.scheduler.running,
            'jobs': []
        }
        
        for job in jobs:
            job_info = {
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            }
            status['jobs'].append(job_info)
        
        return status

