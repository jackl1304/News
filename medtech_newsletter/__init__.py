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
        
        try:
            data = request.get_json() if request.is_json else request.form
            email = data.get('email', '').strip().lower()
            
            if not email:
                return jsonify
