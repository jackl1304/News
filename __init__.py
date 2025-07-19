from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps
from flask_cors import CORS
from datetime import datetime
import os
from loguru import logger
from sqlalchemy import text

# Importiere zentrale Instanzen und Modelle
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
            flash('Bitte melden Sie sich an, um diese Seite zu sehen.', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Für diese Aktion sind Administratorrechte erforderlich.', 'danger')
            return redirect(url_for('main.user_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def create_app(config_name='development'):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])

    db.init_app(app)
    CORS(app)
    
    # Blueprints für Routen registrieren
    from .routes import bp as main_blueprint
    app.register_blueprint(main_blueprint)

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

    # Scheduler starten
    if config_name == 'production' or os.environ.get('START_SCHEDULER', 'false').lower() == 'true':
        scheduler = TaskScheduler(app)
        scheduler.start_scheduler()

    return app
