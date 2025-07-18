from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps
from flask_cors import CORS
from datetime import datetime
import os
from loguru import logger
from sqlalchemy import text
from .models import db # WICHTIG: Wir importieren das db-Objekt aus models.py

def create_app(config_name='development'):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])

    # HIER verbinden wir die App mit dem db-Objekt
    db.init_app(app)

    # Importiere Module, die db benötigen, erst NACH init_app
    from . import models, scheduler, email_service, newsletter_generator, analyzer
    
    CORS(app)
    
    # Services initialisieren
    email_service_instance = email_service.EmailService(app)
    scheduler_instance = scheduler.TaskScheduler(app)

    with app.app_context():
        db.create_all()
        # Admin-User erstellen, falls nicht vorhanden
        if not models.User.query.filter_by(email=os.environ.get('ADMIN_EMAIL')).first():
            admin_user = models.User(
                email=os.environ.get('ADMIN_EMAIL'),
                is_admin=True
            )
            admin_user.set_password(os.environ.get('ADMIN_PASSWORD'))
            db.session.add(admin_user)
            db.session.commit()
            logger.info("Admin-Benutzer erstellt.")

    # Decorators
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('is_admin'):
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

    # Routen
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('login'))
        
    # ... (alle anderen Routen bleiben gleich)

    if app.config['ENV'] != 'testing':
        if config_name == 'production' or os.environ.get('START_SCHEDULER', 'false').lower() == 'true':
            scheduler_instance.start_scheduler()

    return app
