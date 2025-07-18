from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps
from flask_cors import CORS
from datetime import datetime
import os
from loguru import logger
from sqlalchemy import text

# Importiere lokale Module RELATIV zum Paket
from .config import config
from .models import db, User, Document, DocumentChange, Newsletter # User statt Subscriber importieren
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
            # Optional: Hier könnte man auf eine "Kein Zugriff"-Seite leiten
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def create_app(config_name='development'):
    """Factory-Funktion zur Erstellung der Flask-App"""

    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])

    CORS(app)
    db.init_app(app)

    # ... Services initialisieren ...
    email_service = EmailService(app)
    scheduler = TaskScheduler(app)
    
    with app.app_context():
        db.create_all()
        # Admin-User erstellen, falls nicht vorhanden
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
            return redirect(url_for('admin_dashboard')) # Oder eine andere User-Startseite
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
                return redirect(url_for('admin_dashboard')) # Oder eine User-Startseite
            
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
            
            # Optional: Willkommens-E-Mail senden
            # email_service.send_welcome_email(email)

            flash('Registrierung erfolgreich! Sie können sich jetzt anmelden.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    # ========== ADMIN ROUTEN (GESCHÜTZT) ==========
    @app.route('/admin/dashboard')
    @login_required
    @admin_required
    def admin_dashboard():
        """Admin-Dashboard"""
        # ... (der Code hier bleibt größtenteils gleich, aber statt Subscriber wird User gezählt)
        total_users = User.query.count()
        total_documents = Document.query.count()
        # ...
        stats = {
            'total_subscribers': total_users, # Angepasst auf User-Modell
            'total_documents': total_documents,
            # ...
        }
        return render_template('admin.html', stats=stats)

    # Platzhalter für die Admin-Passwort-Bestätigung
    @app.route('/admin/verify_password', methods=['POST'])
    @login_required
    @admin_required
    def verify_admin_password():
        password = request.json.get('password')
        user = User.query.get(session['user_id'])
        if user and user.check_password(password):
            return jsonify({'success': True}), 200
        return jsonify({'success': False}), 401
    
    # ... (alle anderen /admin/... Routen müssen @login_required und @admin_required bekommen)
    
    # ... (restliche App-Logik)
    
    if config_name == 'production' or os.environ.get('START_SCHEDULER', 'false').lower() == 'true':
        scheduler.start_scheduler()

    return app
