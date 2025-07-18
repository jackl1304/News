from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Text, JSON

db = SQLAlchemy()

class Subscriber(db.Model):
    """Modell für Newsletter-Abonnenten"""
    __tablename__ = 'subscribers'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=True)
    company = db.Column(db.String(200), nullable=True)
    interests = db.Column(JSON, nullable=True)  # Liste von Interessensgebieten
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Subscriber {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'company': self.company,
            'interests': self.interests,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Document(db.Model):
    """Modell für überwachte Dokumente"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False, index=True)  # FDA, BfArM, ISO, TUV
    title = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(1000), nullable=False, unique=True)
    content_hash = db.Column(db.String(64), nullable=False)  # SHA-256 Hash des Inhalts
    content = db.Column(Text, nullable=True)
    doc_metadata = db.Column(JSON, nullable=True)  # Zusätzliche Metadaten
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Beziehung zu Änderungen
    changes = db.relationship('DocumentChange', backref='document', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Document {self.source}: {self.title[:50]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'title': self.title,
            'url': self.url,
            'content_hash': self.content_hash,
            'metadata': self.doc_metadata,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DocumentChange(db.Model):
    """Modell für erkannte Änderungen in Dokumenten"""
    __tablename__ = 'document_changes'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    change_type = db.Column(db.String(50), nullable=False)  # 'new', 'modified', 'deleted'
    change_summary = db.Column(Text, nullable=True)
    old_content_hash = db.Column(db.String(64), nullable=True)
    new_content_hash = db.Column(db.String(64), nullable=True)
    diff_data = db.Column(JSON, nullable=True)  # Detaillierte Diff-Informationen
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)  # Ob die Änderung bereits in einem Newsletter verarbeitet wurde
    
    def __repr__(self):
        return f'<DocumentChange {self.change_type} for Document {self.document_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'change_type': self.change_type,
            'change_summary': self.change_summary,
            'old_content_hash': self.old_content_hash,
            'new_content_hash': self.new_content_hash,
            'diff_data': self.diff_data,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'processed': self.processed
        }

class Newsletter(db.Model):
    """Modell für generierte Newsletter"""
    __tablename__ = 'newsletters'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content_html = db.Column(Text, nullable=False)
    content_text = db.Column(Text, nullable=False)
    changes_included = db.Column(JSON, nullable=True)  # IDs der enthaltenen Änderungen
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
    recipient_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Newsletter {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content_html': self.content_html,
            'content_text': self.content_text,
            'changes_included': self.changes_included,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'recipient_count': self.recipient_count
        }

