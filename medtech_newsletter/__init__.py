from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps
from flask_cors import CORS
from datetime import datetime
import os
from loguru import logger
from sqlalchemy import text

# ... (restliche Imports bleiben gleich)
from .config import config
from .models import db, User, Document, DocumentChange, Newsletter
from .scheduler import TaskScheduler
from .email_service import EmailService
from .newsletter_generator import NewsletterGenerator
from .analyzer import DocumentAnalyzer

# ... (Decorators 'login_required' und 'admin_required' bleiben gleich)

def create_app(config_name='development'):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])
    # ... (restliche Initialisierungen bleiben gleich)
    
    with app.app_context():
        db.create_all()
        # ... (Admin-User Erstellung bleibt gleich)

    # ========== AUTHENTICATION & PROFILE ROUTEN ==========
    
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('edit_profile'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # ... (Login-Logik bleibt gleich)
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email, is_active=True).first()

            if user and user.check_password(password):
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['is_admin'] = user.is_admin
                # Leite zur Profilseite, wenn noch keine Basisdaten vorhanden sind
                if not user.first_name or not user.country:
                    return redirect(url_for('edit_profile'))
                return redirect(url_for('user_dashboard')) # Platzhalter für ein User-Dashboard
            
            flash('Falsche E-Mail, falsches Passwort oder Konto inaktiv.', 'danger')
        return render_template('login.html')


    @app.route('/registrieren', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            if User.query.filter_by(email=email).first():
                flash('Diese E-Mail-Adresse ist bereits registriert.', 'warning')
                return redirect(url_for('register'))

            new_user = User(email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            # NEU: Sende Bestätigungs-E-Mail
            email_service.send_welcome_email(email, email) # Name ist noch nicht bekannt

            flash('Registrierung erfolgreich! Bitte loggen Sie sich ein und vervollständigen Sie Ihr Profil.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')

    @app.route('/profil', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        user = User.query.get(session['user_id'])
        if request.method == 'POST':
            # Daten aus dem Formular übernehmen und in der DB speichern
            user.first_name = request.form.get('first_name')
            user.last_name = request.form.get('last_name')
            user.street = request.form.get('street')
            user.street_number = request.form.get('street_number')
            user.postal_code = request.form.get('postal_code')
            user.city = request.form.get('city')
            user.country = request.form.get('country')
            user.company = request.form.get('company')
            user.position = request.form.get('position')
            db.session.commit()
            flash('Profil erfolgreich aktualisiert!', 'success')
            return redirect(url_for('user_dashboard')) # Weiterleitung zum User-Dashboard

        return render_template('edit_profile.html', user=user, countries=get_countries())

    @app.route('/konto_loeschen', methods=['POST'])
    @login_required
    def delete_account():
        user = User.query.get(session['user_id'])
        # 1. Stufe: Konto deaktivieren
        user.is_active = False
        db.session.commit()
        # Hier E-Mail mit Bestätigungslink senden (Token-Logik für Produktion nötig)
        flash('Ihr Konto wurde deaktiviert. Sie erhalten eine E-Mail, um die Löschung endgültig zu bestätigen.', 'warning')
        session.clear()
        return redirect(url_for('login'))

    # Platzhalter für ein User-Dashboard
    @app.route('/dashboard')
    @login_required
    def user_dashboard():
        return f"<h1>Willkommen {session.get('user_email')}</h1><p>Dies ist Ihr persönliches Dashboard.</p>"


    # ========== ADMIN ROUTEN ( bleiben größtenteils gleich) ==========
    # ...

    # Hilfsfunktion für Länderliste
    def get_countries():
        # In einer echten App würde man diese Liste aus einer Datei oder Datenbank laden
        return ['Deutschland', 'Österreich', 'Schweiz', 'USA', 'Großbritannien', 'Frankreich', 'Italien', 'Spanien']

    return app
