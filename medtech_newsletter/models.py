from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False) # Für die "sanfte" Löschung
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Neue Profilfelder
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    street = db.Column(db.String(200))
    street_number = db.Column(db.String(20))
    postal_code = db.Column(db.String(20))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    company = db.Column(db.String(100))
    position = db.Column(db.String(100))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat()
        }

# Die anderen Modelle (Document, DocumentChange, Newsletter) bleiben unverändert
# ...
