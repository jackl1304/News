# Wichtige neue Imports für Login-Funktionalität
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps
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

# HILFSFUNKTION ZUM SCHÜTZEN VON ROUTEN (Decorator)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def create_app(config_name='development'):
    """Factory-Funktion zur Erstellung der Flask-App"""

    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])

    # CORS & DB Initialisierung
    CORS(app)
    db.init_app(app)

    # Services
    email_service = EmailService(app)
    scheduler = TaskScheduler(app)
    # ... (restliche Initialisierungen bleiben gleich)

    with app.app_context():
        db.create_all()

    # Routen definieren
    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Zeigt die Login-Seite an und verarbeitet den Login"""
        error = None
        if request.method == 'POST':
            # Vergleiche das eingegebene Passwort mit dem sicheren Passwort aus der Umgebung
            if request.form.get('password') == os.environ.get('ADMIN_PASSWORD'):
                session['logged_in'] = True
                return redirect(url_for('admin_dashboard'))
            else:
                error = 'Falsches Passwort!'
        return render_template('login.html', error=error)
    
    @app.route('/logout')
    def logout():
        """Loggt den Benutzer aus"""
        session.pop('logged_in', None)
        return redirect(url_for('login'))

    @app.route('/registrieren')
    def register_page():
        return render_template('index.html')

    # ... (Die Route /subscribe bleibt unverändert) ...
    @app.route('/subscribe', methods=['POST'])
    def subscribe():
        # Kompletter Code für subscribe bleibt hier
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
        # Kompletter Code für unsubscribe bleibt hier
        if request.method == 'GET':
            return render_template('unsubscribe.html')
        
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

    # AB HIER WERDEN ALLE ADMIN-ROUTEN GESCHÜTZT
    @app.route('/admin')
    @login_required
    def admin_dashboard():
        """Admin-Dashboard"""
        total_subscribers = Subscriber.query.filter_by(is_active=True).count()
        # ... (restlicher Code der Funktion bleibt gleich)
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
    @login_required
    def delete_subscriber(subscriber_id):
        # ... (Code bleibt gleich)
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
    @login_required
    def manual_scraping():
        # ... (Code bleibt gleich)
        try:
            scheduler.run_manual_scraping()
            return jsonify({'message': 'Scraping gestartet'}), 200
        except Exception as e:
            logger.error(f"Fehler beim manuellen Scraping: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ... (schütze alle weiteren /admin/... Routen mit @login_required)
    @app.route('/admin/manual-newsletter', methods=['POST'])
    @login_required
    def manual_newsletter():
        # ...
        try:
            scheduler.run_manual_newsletter_generation()
            return jsonify({'message': 'Newsletter-Generierung gestartet'}), 200
        except Exception as e:
            logger.error(f"Fehler bei manueller Newsletter-Generierung: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/admin/subscribers')
    @login_required
    def admin_subscribers():
        # ...
        subscribers = Subscriber.query.order_by(Subscriber.created_at.desc()).all()
        return jsonify([sub.to_dict() for sub in subscribers])

    @app.route('/admin/documents')
    @login_required
    def admin_documents():
        # ...
        documents = Document.query.order_by(Document.last_checked.desc()).limit(100).all()
        return jsonify([doc.to_dict() for doc in documents])

    @app.route('/admin/changes')
    @login_required
    def admin_changes():
        # ...
        changes = DocumentChange.query.order_by(DocumentChange.detected_at.desc()).limit(50).all()
        return jsonify([change.to_dict() for change in changes])

    @app.route('/admin/newsletters')
    @login_required
    def admin_newsletters():
        # ...
        newsletters = Newsletter.query.order_by(Newsletter.generated_at.desc()).limit(20).all()
        return jsonify([nl.to_dict() for nl in newsletters])
    
    # ... (restliche Routen und Fehler-Handler bleiben gleich) ...
    @app.route('/newsletter/<int:newsletter_id>')
    def view_newsletter(newsletter_id):
        newsletter = Newsletter.query.get_or_404(newsletter_id)
        return newsletter.content_html

    @app.route('/api/status')
    def api_status():
        return jsonify({
            'status': 'running',
            'timestamp': datetime.utcnow().isoformat(),
            'scheduler_running': scheduler.scheduler.running if scheduler else False
        })

    @app.route('/health')
    def health_check():
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
        return jsonify({'error': 'Interner Serverfehler'}), 500

    if config_name == 'production' or os.environ.get('START_SCHEDULER', 'false').lower() == 'true':
        scheduler.start_scheduler()

    return app
