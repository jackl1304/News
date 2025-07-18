from .extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    # ... (Rest der User-Klasse bleibt gleich)

# ... (alle anderen Modell-Klassen bleiben gleich)
