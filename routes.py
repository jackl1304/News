from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from .models import db, User, Document, DocumentChange
from .extensions import db
import os
from loguru import logger

bp = Blueprint('main', __name__)

# Hilfsfunktion für Länderliste
def get_countries():
    return ['Deutschland', 'Österreich', 'Schweiz', 'USA', 'Großbritannien', 'Frankreich', 'Italien', 'Spanien']

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
            
            if not user.first_name:
                flash('Willkommen! Bitte vervollständigen Sie Ihr Profil.', 'info')
                return redirect(url_for('main.edit_profile'))
            
            return redirect(url_for('main.user_dashboard'))
        
        flash('Falsche E-Mail, falsches Passwort oder Konto inaktiv.', 'danger')
    return render_template('login.html')

@bp.route('/registrieren', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Diese E-Mail-Adresse ist bereits registriert.', 'warning')
            return redirect(url_for('main.register'))

        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # Hier könnte man eine Bestätigungs-E-Mail senden
        # email_service.send_welcome_email(email)

        flash('Registrierung erfolgreich! Bitte melden Sie sich an.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Sie wurden erfolgreich abgemeldet.', 'success')
    return redirect(url_for('main.login'))

@bp.route('/dashboard')
def user_dashboard():
    # Zeigt dem Benutzer eine Übersicht der neuesten Dokumente
    documents = Document.query.order_by(Document.last_checked.desc()).limit(20).all()
    changes = DocumentChange.query.order_by(DocumentChange.detected_at.desc()).limit(20).all()
    return render_template('user_dashboard.html', documents=documents, changes=changes)

@bp.route('/profil', methods=['GET', 'POST'])
def edit_profile():
    user = User.query.get_or_404(session['user_id'])
    if request.method == 'POST':
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
        return redirect(url_for('main.user_dashboard'))

    return render_template('edit_profile.html', user=user, countries=get_countries())

@bp.route('/abmelden', methods=['GET', 'POST'])
def unsubscribe():
    if request.method == 'POST':
        user = User.query.get(session.get('user_id'))
        if user:
            user.is_active = False
            db.session.commit()
            # Hier E-Mail mit endgültigem Lösch-Link senden (erfordert Token-System)
            flash('Ihr Konto wurde deaktiviert und Sie erhalten keine Newsletter mehr.', 'warning')
            session.clear()
            return redirect(url_for('main.login'))
    return render_template('unsubscribe.html')


# ... (alle Admin-Routen gehören auch hierher, geschützt mit Decorators)
