from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps
from flask_cors import CORS
from datetime import datetime
import os
from loguru import logger
from sqlalchemy import text

# Importiere lokale Module RELATIV zum Paket
from .config import config
from .models import db, User, Document, DocumentChange, Newsletter
from .scheduler import TaskScheduler
from .email_service import EmailService
from .newsletter_generator import NewsletterGenerator
from .analyzer import DocumentAnalyzer

# Decorators zum Schutz von Routen
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def create_app(config_name='development'):
    """Factory-Funktion zur Erstellung der Flask-App"""

    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])

    CORS(app)
    db.init_app(app)

    email_service = EmailService(app)
    scheduler = TaskScheduler(app)
    
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email=os.environ.get('ADMIN_EMAIL')).first():
            admin_user = User(
                email=os.environ.get('ADMIN_EMAIL'),
                is_admin=True
            )
            admin_user.set_password(os.environ.get('ADMIN_PASSWORD'))
            db.session.add(admin_user)
            db.session.commit()
            logger.info("Admin-Benutzer erstellt.")

    # ========== AUTHENTICATION ROUTEN ==========
    @app.route('/')
    def index():
        if 'user_id' in session:
            # Wenn eingeloggt, leite zum Dashboard weiter
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()

            if user and user.check_password(password):
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['is_admin'] = user.is_admin
                return redirect(url_for('admin_dashboard'))
            
            flash('Falsche E-Mail oder falsches Passwort.', 'danger')
        return render_template('login.html')

    @app.route('/registrieren', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            if User.query.filter_by(email=email).first():
                flash('Diese E-Mail-Adresse ist bereits registriert.', 'warning')
                return redirect(url_for('register'))

            new_user = User(email=email, is_admin=False)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registrierung erfolgreich! Sie können sich jetzt anmelden.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    # ========== ADMIN ROUTEN (GESCHÜTZT) ==========
    
    # HIER IST DIE KORREKTUR
    @app.route('/admin/dashboard')
    @login_required
    @admin_required
    def admin_dashboard():
        """Admin-Dashboard"""
        total_users = User.query.count()
        total_documents = Document.query.count()
        recent_changes = DocumentChange.query.filter_by(processed=False).count()
        recent_newsletters = Newsletter.query.order_by(Newsletter.generated_at.desc()).limit(5).all()
        
        job_status = scheduler.get_job_status()
        
        stats = {
            'total_subscribers': total_users, # Angepasst an das User-Modell
            'total_documents': total_documents,
            'pending_changes': recent_changes,
            'recent_newsletters': [nl.to_dict() for nl in recent_newsletters],
            'scheduler_status': job_status
        }
        
        return render_template('admin.html', stats=stats)

    @app.route('/admin/verify_password', methods=['POST'])
    @login_required
    @admin_required
    def verify_admin_password():
        password = request.json.get('password')
        user = User.query.get(session['user_id'])
        if user and user.check_password(password):
            return jsonify({'success': True}), 200
        return jsonify({'success': False}), 401
    
    @app.route('/admin/subscribers')
    @login_required
    @admin_required
    def admin_subscribers():
        # Diese Route liefert jetzt User-Daten statt Subscriber
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify([user.to_dict() for user in users])

    # ... (alle anderen /admin/... Routen benötigen @login_required und @admin_required)
    
    # ... (restliche App-Logik und Fehler-Handler)
    @app.route('/admin/manual-scraping', methods=['POST'])
    @login_required
    @admin_required
    def manual_scraping():
        try:
            scheduler.run_manual_scraping()
            return jsonify({'message': 'Scraping gestartet'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/admin/manual-newsletter', methods=['POST'])
    @login_required
    @admin_required
    def manual_newsletter():
        try:
            scheduler.run_manual_newsletter_generation()
            return jsonify({'message': 'Newsletter-Generierung gestartet'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/admin/documents')
    @login_required
    @admin_required
    def admin_documents():
        documents = Document.query.order_by(Document.last_checked.desc()).limit(100).all()
        return jsonify([doc.to_dict() for doc in documents])

    @app.route('/admin/changes')
    @login_required
    @admin_required
    def admin_changes():
        changes = DocumentChange.query.order_by(DocumentChange.detected_at.desc()).limit(50).all()
        return jsonify([change.to_dict() for change in changes])

    @app.route('/admin/newsletters')
    @login_required
    @admin_required
    def admin_newsletters():
        newsletters = Newsletter.query.order_by(Newsletter.generated_at.desc()).limit(20).all()
        return jsonify([nl.to_dict() for nl in newsletters])
    
    @app.route('/newsletter/<int:newsletter_id>')
    def view_newsletter(newsletter_id):
        newsletter = Newsletter.query.get_or_404(newsletter_id)
        return newsletter.content_html
        
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
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    if config_name == 'production' or os.environ.get('START_SCHEDULER', 'false').lower() == 'true':
        scheduler.start_scheduler()

    return app
