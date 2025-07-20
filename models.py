"""Definiert die Datenbankmodelle für die Anwendung."""
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """Benutzermodell für die Authentifizierung."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    company = db.Column(db.String(100))

    def set_password(self, password):
        """Setzt das Passwort des Benutzers."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Überprüft das Passwort des Benutzers."""
        return check_password_hash(self.password_hash, password)

class Document(db.Model):
    """Dokumentenmodell für gescrapte Inhalte."""
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(512), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=True)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
