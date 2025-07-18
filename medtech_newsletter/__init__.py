from flask import Flask
from .extensions import db
from .config import config

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # WICHTIG: Erweiterungen mit der App initialisieren
    db.init_app(app)

    # Modelle und Routen importieren, NACHDEM db initialisiert wurde
    from . import models
    from .main import main as main_blueprint # Annahme: Routen sind in main.py
    app.register_blueprint(main_blueprint)
    
    with app.app_context():
        db.create_all()

    return app
