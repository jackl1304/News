from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps
from flask_cors import CORS
from datetime import datetime
import os
from loguru import logger
from sqlalchemy import text

# Importiere Erweiterungen und Modelle
from .extensions import db
from .models import User, Document, DocumentChange, Newsletter

# Importiere andere Module
from .config import config
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
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])

    # Erweiterungen initialisieren
    db.init_app(app)
    CORS(app)
    
    # Services initialisieren
    email_service = EmailService(app)
    scheduler = TaskScheduler(app)
    
    with app.app_context():
        db.create_all()
        # Admin-User erstellen, falls nicht vorhanden
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_pass = os.environ.get('ADMIN_PASSWORD')
        if admin_email and admin_pass and not User.query.filter_by(email=admin_email).first():
            admin_user = User(email=admin_email, is_admin=True)
            admin_user.set_password(admin_pass)
            db.session.add(admin_user)
            db.session.commit()
            logger.info("Admin-Benutzer erstellt.")

    # Routen definieren
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email, is_active=True).first()

            if user and user.check_password(password):
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['is_admin'] = user.is_admin
                if not user.first_name:
                     return redirect(url_for('edit_profile'))
                return redirect(url_for('admin_dashboard'))
            
            flash('Falsche E-Mail oder falsches Passwort.', 'danger')
        return render_template('login.html')

    # ... (fügen Sie hier alle Ihre anderen Routen wie /registrieren, /logout, /admin/dashboard, etc. ein) ...

    # Scheduler starten
    if config_name == 'production' or os.environ.get('START_SCHEDULER', 'false').lower() == 'true':
        scheduler.start_scheduler()

    return app
