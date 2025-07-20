"""Initialisiert die Flask-Anwendung und konfiguriert sie."""
import os

from flask import Flask

from .config import config
from .models import db, User


def create_app(config_name=\'development\'):
    """Initialisiert die Flask-Anwendung."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    from .routes import bp as main_blueprint  # Import inside function to avoid circular imports
    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all()
        # Erstellt den Admin-User, falls nicht vorhanden
        admin_email = os.environ.get(\'ADMIN_EMAIL\')
        admin_pass = os.environ.get(\'ADMIN_PASSWORD\')
        if admin_email and admin_pass and not User.query.filter_by(email=admin_email).first():
            admin_user = User(email=admin_email, is_admin=True)
            admin_user.set_password(admin_pass)
            db.session.add(admin_user)
            db.session.commit()

    return app
