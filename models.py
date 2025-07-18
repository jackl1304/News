from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=True)
    company = db.Column(db.String(120), nullable=True)
    interests = db.Column(db.JSON, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'company': self.company,
            'interests': self.interests,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(512), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=True)
    content_hash = db.Column(db.String(64), nullable=True)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'url': self.url,
            'title': self.title,
            'last_checked': self.last_checked.isoformat()
        }

class DocumentChange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    change_summary = db.Column(db.Text, nullable=False)
    importance_score = db.Column(db.Integer, default=0)
    processed = db.Column(db.Boolean, default=False, nullable=False)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    document = db.relationship('Document', backref=db.backref('changes', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'change_summary': self.change_summary,
            'importance_score': self.importance_score,
            'processed': self.processed,
            'detected_at': self.detected_at.isoformat()
        }

class Newsletter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content_html = db.Column(db.Text, nullable=False)
    content_text = db.Column(db.Text, nullable=False)
    recipient_count = db.Column(db.Integer, default=0)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'recipient_count': self.recipient_count,
            'generated_at': self.generated_at.isoformat(),
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }
