from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from .models import db, User, Document, DocumentChange
from .extensions import db
from .email_service import EmailService # Importieren Sie den Service
import os
from loguru import logger

bp = Blueprint('main', __name__)

# Hilfsfunktion für Länderliste
def get_countries():
    return ['Deutschland', 'Österreich', 'Schweiz', 'USA', 'Großbritannien', 'Frankreich', 'Italien', 'Spanien']

# ... (andere Routen wie '/', '/login' bleiben unverändert) ...
@bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.user_dashboard'))
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, is_active=True).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['is_admin'] = user.is_admin
            
            return redirect(url_for('main.user_dashboard'))
        
        flash('Falsche E-Mail, falsches Passwort oder Konto inaktiv.', 'danger')
    return render_template('login.html')

@bp.route('/registrieren', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        company = request.form.get('company')

        if User.query.filter_by(email=email).first():
            flash('Diese E-Mail-Adresse ist bereits registriert.', 'warning')
            return redirect(url_for('main.register'))

        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            company=company
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # HIER IST DIE ÄNDERUNG: Wir übergeben den Vornamen
        email_service = EmailService()
        email_service.init_app(current_app) # Initialisieren, falls noch nicht geschehen
        email_service.send_welcome_email(email, first_name)

        flash('Registrierung erfolgreich! Sie können sich jetzt anmelden.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

# ... (alle anderen Routen bleiben gleich)
