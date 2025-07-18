from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Wir erstellen hier KEIN db-Objekt mehr. Es wird von __init__.py bereitgestellt.
# Die Modelle benötigen es aber zur Definition, was zu einem Henne-Ei-Problem führt.
# Wir lassen es vorerst so, wie es war, und korrigieren die __init__.py, um das Problem zu lösen.
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    street = db.Column(db.String(200))
    street_number = db.Column(db.String(20))
    postal_code = db.Column(db.String(20))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    company = db.Column(db.String(100))
    position = db.Column(db.String(100))
    
    # ... (Rest der User-Klasse bleibt gleich)

class Document(db.Model):
    # ... (Rest der Document-Klasse bleibt gleich)

class DocumentChange(db.Model):
    # ... (Rest der DocumentChange-Klasse bleibt gleich)

class Newsletter(db.Model):
    # ... (Rest der Newsletter-Klasse bleibt gleich)
