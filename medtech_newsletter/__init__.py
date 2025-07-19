from flask import Flask
import os

# Importiere die zentralen Erweiterungen
from .extensions import db
from .config import config

def create_app(config_name='development'):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])

    # Initialisiere die Erweiterungen mit der App
    db.init_app(app)

    # Importiere die Modelle, damit die Tabellen erstellt werden können
    from . import models

    with app.app_context():
        db.create_all()
        # Admin-User erstellen, falls nicht vorhanden
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_pass = os.environ.get('ADMIN_PASSWORD')
        if admin_email and admin_pass and not models.User.query.filter_by(email=admin_email).first():
            admin_user = models.User(email=admin_email, is_admin=True)
            admin_user.set_password(admin_pass)
            db.session.add(admin_user)
            db.session.commit()

    # Importiere und registriere die Routen (Blueprints)
    # HINWEIS: Hier müssten die Routen in separate Dateien ausgelagert werden.
    # Um es einfach zu halten, definieren wir sie vorerst weiterhin hier,
    # aber importieren sie erst, nachdem alles initialisiert ist.
    from . import routes
    app.register_blueprint(routes.bp)

    return app
