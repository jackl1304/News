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

    @app.route('/
