from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from .models import db, User, Document, DocumentChange, Newsletter
from .extensions import db
from . import admin_required, login_required

bp = Blueprint('main', __name__)

# ... (Ihre bestehenden Routen wie index, login, register bleiben unverändert) ...

@bp.route('/logout')
def logout():
    session.clear()
    flash('Sie wurden erfolgreich abgemeldet.', 'success')
    return redirect(url_for('main.login'))

@bp.route('/dashboard')
@login_required
def user_dashboard():
    return render_template('dashboard.html')

# ========== ADMIN ROUTEN ==========

@bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'total_subscribers': User.query.count(),
        'total_documents': Document.query.count(),
        'pending_changes': DocumentChange.query.filter_by(processed=False).count(),
        'recent_newsletters': Newsletter.query.order_by(Newsletter.generated_at.desc()).limit(5).all()
    }
    return render_template('admin.html', stats=stats)

@bp.route('/admin/users')
@login_required
@admin_required
def get_users():
    users = User.query.order_by(User.id).all()
    return jsonify([user.to_dict() for user in users])

# NEUE ROUTE ZUM BEARBEITEN
@bp.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.email = request.form['email']
        user.is_admin = 'is_admin' in request.form
        db.session.commit()
        flash(f'Benutzer {user.email} wurde aktualisiert.', 'success')
        return redirect(url_for('main.admin_dashboard'))
    return render_template('edit_user.html', user=user)

# NEUE ROUTE ZUM LÖSCHEN
@bp.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == session.get('user_id'):
        return jsonify({'error': 'Sie können sich nicht selbst löschen.'}), 400

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'Benutzer {user.email} wurde gelöscht.'}), 200

# ... (restliche Admin-Routen für Scraper etc. bleiben gleich)
