from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from .models import db, User, Document, DocumentChange, Newsletter
# (Weitere notwendige Imports hier hinzufügen)

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.admin_dashboard'))
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # ... (Ihre komplette Login-Logik hier)

# ... (ALLE ANDEREN ROUTEN HIER EINFÜGEN, und @app.route zu @bp.route ändern)
# ... und bei url_for immer 'main.routenname' verwenden, z.B. url_for('main.login')
