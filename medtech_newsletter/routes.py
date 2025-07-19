from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import db, User
from .extensions import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
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
            return redirect(url_for('main.dashboard'))
        
        flash('E-Mail oder Passwort falsch.', 'danger')
    return render_template('login.html')

@bp.route('/registrieren', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('E-Mail-Adresse bereits registriert.', 'warning')
            return redirect(url_for('main.register'))

        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registrierung erfolgreich! Bitte melden Sie sich an.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    # Hier können Sie später die Dashboard-Logik hinzufügen
    return render_template('dashboard.html') 

# Fügen Sie hier Ihre anderen Routen (Profil, Admin etc.) ein
