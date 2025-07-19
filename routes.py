from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from .models import db, User, Document, DocumentChange
from .extensions import db
# ... (andere Imports bleiben gleich)

bp = Blueprint('main', __name__)

# Hilfsfunktion für Länderliste
def get_countries():
    return ['Deutschland', 'Österreich', 'Schweiz', 'USA', 'Großbritannien', 'Frankreich', 'Italien', 'Spanien']

# ... (Route '/' bleibt gleich)

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
        # NEUE FELDER AUS DEM FORMULAR LESEN
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        company = request.form.get('company')

        if User.query.filter_by(email=email).first():
            flash('Diese E-Mail-Adresse ist bereits registriert.', 'warning')
            return redirect(url_for('main.register'))

        # NEUEN BENUTZER MIT MEHR DATEN ERSTELLEN
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            company=company
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # Optional: Bestätigungs-E-Mail senden
        # email_service.send_welcome_email(email, first_name)

        flash('Registrierung erfolgreich! Sie können sich jetzt anmelden.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

# ... (Route '/logout' bleibt gleich)

@bp.route('/dashboard')
def user_dashboard():
    documents = Document.query.order_by(Document.last_checked.desc()).limit(20).all()
    changes = DocumentChange.query.order_by(DocumentChange.detected_at.desc()).limit(20).all()
    return render_template('user_dashboard.html', documents=documents, changes=changes)

@bp.route('/profil', methods=['GET', 'POST'])
def edit_profile():
    user = User.query.get_or_404(session['user_id'])
    if request.method == 'POST':
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.company = request.form.get('company')
        user.position = request.form.get('position')
        user.street = request.form.get('street')
        user.street_number = request.form.get('street_number')
        user.postal_code = request.form.get('postal_code')
        user.city = request.form.get('city')
        user.country = request.form.get('country')
        user.phone_number = request.form.get('phone_number') # NEUES FELD SPEICHERN
        db.session.commit()
        flash('Profil erfolgreich aktualisiert!', 'success')
        return redirect(url_for('main.user_dashboard'))

    return render_template('edit_profile.html', user=user, countries=get_countries())

# ... (restliche Routen wie '/abmelden' und alle Admin-Routen bleiben gleich)
