from flask_mail import Mail, Message
from typing import List, Dict, Optional
from loguru import logger
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from flask import current_app

class EmailService:
    """Service für den Versand von E-Mails und Newslettern"""
    
    def __init__(self, app=None):
        self.mail = None
        self.config = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialisiert den E-Mail-Service mit der Flask-App"""
        if not self.mail:
            self.mail = Mail(app)
        self.config = app.config
    
    # ... (send_newsletter und send_newsletters_batch bleiben unverändert) ...

    def send_welcome_email(self, subscriber_email: str, subscriber_name: Optional[str] = None) -> bool:
        """Sendet eine Willkommens-E-Mail an neue Abonnenten"""
        if not self.mail:
            self.init_app(current_app._get_current_object())

        try:
            subject = "Willkommen beim Medizintechnik Newsletter"
            
            # HIER IST DIE ÄNDERUNG: Dynamische Anrede
            greeting_name = subscriber_name if subscriber_name else subscriber_email
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="de">
            <body>
                <div class="header">
                    <h1>Willkommen!</h1>
                    <p>Medizintechnik & Healthcare Newsletter</p>
                </div>
                <div class="content">
                    <p>Hallo {greeting_name},</p>
                    
                    <p>vielen Dank für Ihr Interesse an unserem Medizintechnik Newsletter! Sie haben sich erfolgreich angemeldet...</p>
                    
                    </div>
            </body>
            </html>
            """
            
            text_content = f"""
Willkommen beim Medizintechnik Newsletter!

Hallo {greeting_name},

vielen Dank für Ihr Interesse an unserem Medizintechnik Newsletter! Sie haben sich erfolgreich angemeldet...
            """
            
            msg = Message(
                subject=subject,
                sender=self.config.get('MAIL_DEFAULT_SENDER'),
                recipients=[subscriber_email]
            )
            
            msg.html = html_content
            msg.body = text_content
            
            self.mail.send(msg)
            logger.info(f"Willkommens-E-Mail erfolgreich an {subscriber_email} gesendet")
            return True
                
        except Exception as e:
            logger.error(f"Fehler beim Senden der Willkommens-E-Mail an {subscriber_email}: {e}")
            return False
    
    # ... (restliche Funktionen der Klasse bleiben unverändert) ...
