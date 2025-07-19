from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from .models import db, User # (und andere Modelle)
from .extensions import db
from . import admin_required, login_required # Annahme: Decorators sind in __init__.py

bp = Blueprint('main', __name__)

# ... (alle Ihre bestehenden Routen wie login, register, dashboard etc. bleiben unverändert)

# ========== ADMIN ROUTEN ==========

@bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # ... (Code für das Dashboard bleibt gleich)
    return render_template('admin.html', stats={})

@bp.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

# NEUE ROUTE ZUM LÖSCHEN VON BENUTZERN
@bp.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    # Verhindern, dass der Admin sich selbst löscht
    if user_id == session.get('user_id'):
        return jsonify({'error': 'Sie können sich nicht selbst löschen.'}), 400

    user_to_delete = User.query.get(user_id)
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        return jsonify({'message': f'Benutzer mit ID {user_id} wurde gelöscht.'}), 200
    return jsonify({'error': 'Benutzer nicht gefunden.'}), 404
