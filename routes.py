"""Definiert die Routen für die Webanwendung."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from .models import db, User

bp = Blueprint(\'main\', __name__)

@bp.route(\'/\')
def index():
    """Leitet den Benutzer je nach Anmeldestatus zum Dashboard oder zur Anmeldeseite weiter."""
    if \'user_id\' in session:
        return redirect(url_for(\'main.dashboard\'))
    return redirect(url_for(\'main.login\'))

@bp.route(\'/login\', methods=[\'GET\', \'POST\'])
def login():
    """Verarbeitet die Benutzeranmeldung."""
    if request.method == \'POST\':
        email = request.form.get(\'email\')
        password = request.form.get(\'password\')
        user = User.query.filter_by(email=email, is_active=True).first()

        if user and user.check_password(password):
            session[\'user_id\'] = user.id
            session[\'user_email\'] = user.email
            session[\'is_admin\'] = user.is_admin
            return redirect(url_for(\'main.dashboard\'))
        
        flash(\'E-Mail oder Passwort falsch.\', \'danger\')
    return render_template(\'login.html\')

@bp.route(\'/registrieren\', methods=[\'GET\', \'POST\'])
def register():
    """Verarbeitet die Benutzerregistrierung."""
    if request.method == \'POST\':
        email = request.form.get(\'email\')
        password = request.form.get(\'password\')

        if User.query.filter_by(email=email).first():
            flash(\'E-Mail-Adresse bereits registriert.\', \'warning\')
            return redirect(url_for(\'main.register\'))

        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash(\'Registrierung erfolgreich! Bitte anmelden.\', \'success\')
        return redirect(url_for(\'main.login\'))
    
    return render_template(\'register.html\')

@bp.route(\'/logout\')
def logout():
    """Meldet den Benutzer ab."""
    session.clear()
    return redirect(url_for(\'main.login\'))

@bp.route(\'/dashboard\')
def dashboard():
    """Zeigt das Benutzer-Dashboard an."""
    if \'user_id\' not in session:
        return redirect(url_for(\'main.login\'))
    return render_template(\'dashboard.html\')

# Fügen Sie hier weitere Routen hinzu (z.B. für Admin)
