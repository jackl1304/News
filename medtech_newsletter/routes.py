from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import db, User
from .extensions import db

bp = Blueprint('main', __name__)

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
            # IMMER ZUM PROFIL weiterleiten nach dem Login
            return redirect(url_for('main.edit_profile'))
        
        flash('E-Mail oder Passwort falsch.', 'danger')
    return render_template('login.html')

@bp.route('/profil', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user = User.query.get_or_404(session['user_id'])
    # ... (Rest der Funktion bleibt gleich)
    return render_template('edit_profile.html', user=user)

# ... (alle anderen Routen bleiben unverändert)
