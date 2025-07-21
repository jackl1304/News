import os
from functools import wraps
from datetime import datetime

from loguru import logger
from sqlalchemy import text

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS

# Importiere die zentralen Erweiterungen
from .extensions import db

# Importiere andere Module
from .config import config
from .models import User, Document, DocumentChange, Newsletter
from .scheduler import TaskScheduler
from .email_service import EmailService
from .newsletter_generator import NewsletterGenerator
from .analyzer import DocumentAnalyzer


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))  # Korrigiert: 'login'
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('login'))  # Korrigiert: 'login'
        return f(*args, **kwargs)
    return decorated_function


def create_app(config_name='development'):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])

    db.init_app(app)
    CORS(app)

    email_service = EmailService(app)
    scheduler = TaskScheduler(app)

    with app.app_context():
        db.create_all()
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_pass = os.environ.get('ADMIN_PASSWORD')
        if admin_email and admin_pass and not User.query.filter_by(email=admin_email).first():
            admin_user = User(email=admin_email, is_admin=True)
            admin_user.set_password(admin_pass)
            db.session.add(admin_user)
            db.session.commit()
            logger.info("Admin-Benutzer erstellt.")

    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])  # Wichtig: Hier ist der 'login' Endpoint korrekt definiert.
    def login():
        if request.method == 'POST':
            # ... (deine Login Logik)
            pass  # Platzhalter für die Login-Logik
        return render_template('login.html')
    
    # ... (restliche Routen)

    return app
