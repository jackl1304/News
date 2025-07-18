from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from datetime import datetime
import os
from loguru import logger
from sqlalchemy import text

# Importiere lokale Module RELATIV zum Paket
from .config import config
from .models import db, Subscriber, Document, DocumentChange, Newsletter
from .scheduler import TaskScheduler
from .email_service import EmailService
from .newsletter_generator import NewsletterGenerator
from .analyzer import DocumentAnalyzer

def create_app(config_name='development'):
    """Factory-Funktion zur Erstellung der Flask-App"""

    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Konfiguration laden
    app.config.from_object(config[config_name])

    # CORS aktivieren
    CORS(app)

    # Datenbank initialisieren
    db.init_app(app)

    # Services initialisieren
    email_service = EmailService(app)
    scheduler = TaskScheduler(app)
    newsletter_generator = NewsletterGenerator()
    analyzer = DocumentAnalyzer()

    # Logging konfigurieren
    logger.add(
        app.config.get('LOG_FILE', 'medtech_newsletter.log'),
        level=app.config.get('LOG_LEVEL', 'INFO'),
        rotation="1 week",
        retention="1 month"
    )

    with app.app_context():
        """Erstellt Datenbanktabellen beim ersten Start"""
        db.create_all()
        logger.info("Datenbanktabellen erstellt")

    # Routen definieren

    @app.route('/')
    def index():
        """Leitet zur Login-Seite weiter"""
        return redirect(url_for('login'))

    @app.route('/login')
    def login():
        """Zeigt die Login-Seite an"""
        return render_template('login.html')

    @app.route('/registrieren')
    def register_page():
        """Zeigt die Registrierungsseite an"""
        return render_template('index.html')

    @app.route('/subscribe', methods=['POST'])
    def subscribe():
        """Neue Abonnenten registrieren"""
        try:
            data = request.get_json() if request.is_json else request.form
            
            email = data.get('email', '').strip().lower()
            name = data.get('name', '').strip()
            company = data.get('company', '').strip()
            interests = data.get('interests', [])
            
            if not email:
                return jsonify({'error': 'E-Mail-Adresse ist erforderlich'}), 400
            
            existing_subscriber = Subscriber.query.filter_by(email=email).first()
            if existing_subscriber:
                if existing_subscriber.is_active:
                    return jsonify({'error': 'Diese E-Mail-Adresse ist bereits registriert'}), 400
                else:
                    existing_subscriber.is_active = True
                    existing_subscriber.name = name
                    existing_subscriber.company = company
                    existing_subscriber.interests = interests
                    existing_subscriber.updated_at = datetime.utcnow()
                    db.session.commit()
                    email_service.send_welcome_email(email, name)
                    return jsonify({'message': 'Erfolgreich wieder angemeldet!'}), 200
            
            subscriber = Subscriber(
                email=email,
                name=name,
                company=company,
                interests=interests
            )
            
            db.session.add(subscriber)
            db.session.commit()
            
            email_service.send_welcome_email(email, name)
            
            logger.info(f"Neuer Abonnent registriert: {email}")
            
            return jsonify({'message': 'Erfolgreich angemeldet! Sie erhalten eine Bestätigungs-E-Mail.'}), 201
            
        except Exception as e:
            logger.error(f"Fehler bei Anmeldung: {e}")
            return jsonify({'error': 'Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.'}), 500

    @app.route('/unsubscribe', methods=['GET', 'POST'])
    def unsubscribe():
        """Abonnenten abmelden"""
        if request.method == 'GET':
            return render_template('unsubscribe.html')
        
        # HIER WAR DER FEHLER - JETZT KORRIGIERT
        try:
            data = request.get_json() if request.is_json else request.form
            email = data.get('email', '').strip().lower()
            
            if not email:
                return jsonify({'error': 'E-Mail-Adresse ist erforderlich'}), 400
            
            subscriber = Subscriber.query.filter_by(email=email).first()
            if not subscriber:
                return jsonify({'error': 'E-Mail-Adresse nicht gefunden'}), 404
            
            if not subscriber.is_active:
                return jsonify({'error': 'Sie sind bereits abgemeldet'}), 400
            
            subscriber.is_active = False
            subscriber.updated_at = datetime.utcnow()
            db.session.commit()
            
            email_service.send_unsubscribe_confirmation(email, subscriber.name)
            
            logger.info(f"Abonnent abgemeldet: {email}")
            
            return jsonify({'message': 'Erfolgreich abgemeldet!'}), 200
            
        except Exception as e:
            logger.error(f"Fehler bei Abmeldung: {e}")
            return jsonify({'error': 'Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.'}), 500

    @app.route('/admin')
    def admin_dashboard():
        """Admin-Dashboard"""
        total_subscribers = Subscriber.query.filter_by(is_active=True).count()
        total_documents = Document.query.count()
        recent_changes = DocumentChange.query.filter_by(processed=False).count()
        recent_newsletters = Newsletter.query.order_by(Newsletter.generated_at.desc()).limit(5).all()
        
        job_status = scheduler.get_job_status()
        
        stats = {
            'total_subscribers': total_subscribers,
            'total_documents': total_documents,
            'pending_changes': recent_changes,
            'recent_newsletters': [nl.to_dict() for nl in recent_newsletters],
            'scheduler_status': job_status
        }
        
        return render_template('admin.html', stats=stats)
    
    @app.route('/admin/subscriber/delete/<int:subscriber_id>', methods=['POST'])
    def delete_subscriber(subscriber_id):
        """Löscht einen Abonnenten aus der Datenbank."""
        try:
            subscriber = Subscriber.query.get(subscriber_id)
            if subscriber:
                db.session.delete(subscriber)
                db.session.commit()
                logger.info(f"Abonnent mit ID {subscriber_id} gelöscht.")
                return jsonify({'message': 'Abonnent erfolgreich gelöscht'}), 200
            return jsonify({'error': 'Abonnent nicht gefunden'}), 404
        except Exception as e:
            logger.error(f"Fehler beim Löschen von Abonnent {subscriber_id}: {e}")
            return jsonify({'error': 'Ein interner Fehler ist aufgetreten'}), 500


    @app.route('/admin/manual-scraping', methods=['POST'])
    def manual_scraping():
        """Manuelles Scraping auslösen"""
        try:
            scheduler.run_manual_scraping()
            return jsonify({'message': 'Scraping gestartet'}), 200
        except Exception as e:
            logger.error(f"Fehler beim manuellen Scraping: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/admin/manual-newsletter', methods=['POST'])
    def manual_newsletter():
        """Manuelle Newsletter-Generierung auslösen"""
        try:
            scheduler.run_manual_newsletter_generation()
            return jsonify({'message': 'Newsletter-Generierung gestartet'}), 200
        except Exception as e:
            logger.error(f"Fehler bei manueller Newsletter-Generierung: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/admin/subscribers')
    def admin_subscribers():
        """Liste aller Abonnenten"""
        subscribers = Subscriber.query.order_by(Subscriber.created_at.desc()).all()
        return jsonify([sub.to_dict() for sub in subscribers])

    @app.route('/admin/documents')
    def admin_documents():
        """Liste aller überwachten Dokumente"""
        documents = Document.query.order_by(Document.last_checked.desc()).limit(100).all()
        return jsonify([doc.to_dict() for doc in documents])

    @app.route('/admin/changes')
    def admin_changes():
        """Liste aller erkannten Änderungen"""
        changes = DocumentChange.query.order_by(DocumentChange.detected_at.desc()).limit(50).all()
        return jsonify([change.to_dict() for change in changes])

    @app.route('/admin/newsletters')
    def admin_newsletters():
        """Liste aller generierten Newsletter"""
        newsletters = Newsletter.query.order_by(Newsletter.generated_at.desc()).limit(20).all()
        return jsonify([nl.to_dict() for nl in newsletters])

    @app.route('/newsletter/<int:newsletter_id>')
    def view_newsletter(newsletter_id):
        """Zeigt einen spezifischen Newsletter an"""
        newsletter = Newsletter.query.get_or_404(newsletter_id)
        return newsletter.content_html

    @app.route('/api/status')
    def api_status():
        """API-Status-Endpoint"""
        return jsonify({
            'status': 'running',
            'timestamp': datetime.utcnow().isoformat(),
            'scheduler_running': scheduler.scheduler.running if scheduler else False
        })

    @app.route('/health')
    def health_check():
        """Health-Check-Endpoint"""
        try:
            db.session.execute(text('SELECT 1'))
            email_configured = email_service.test_email_configuration()
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'email': 'configured' if email_configured else 'not_configured',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"Health-Check fehlgeschlagen: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Seite nicht gefunden'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Interner Serverfehler: {error}")
        return jsonify({'error': 'Interner Serverfehler'}), 500

    # Scheduler starten (nur in Produktionsumgebung)
    if config_name == 'production' or os.environ.get('START_SCHEDULER', 'false').lower() == 'true':
        scheduler.start_scheduler()
        logger.info("Scheduler gestartet")

    return app
