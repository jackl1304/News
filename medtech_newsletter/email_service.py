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

class EmailService:
    """Service für den Versand von E-Mails und Newslettern"""
    
    def __init__(self, app=None, config=None):
        self.mail = None
        self.config = config
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialisiert den E-Mail-Service mit der Flask-App"""
        self.mail = Mail(app)
        self.config = app.config
    
    def send_newsletter(self, newsletter: Dict, recipient_email: str, recipient_name: Optional[str] = None) -> bool:
        """Sendet einen Newsletter an einen Empfänger"""
        try:
            # Erstelle E-Mail-Nachricht
            msg = Message(
                subject=newsletter['title'],
                sender=self.config.get('MAIL_DEFAULT_SENDER'),
                recipients=[recipient_email]
            )
            
            # Setze HTML und Text Inhalt
            msg.html = newsletter['html_content']
            msg.body = newsletter['text_content']
            
            # Personalisierte Betreffzeile
            if recipient_name:
                msg.subject = f"{newsletter['title']} - {recipient_name}"
            
            # Sende E-Mail
            if self.mail:
                self.mail.send(msg)
                logger.info(f"Newsletter erfolgreich an {recipient_email} gesendet")
                return True
            else:
                logger.error("E-Mail-Service nicht initialisiert")
                return False
                
        except Exception as e:
            logger.error(f"Fehler beim Senden des Newsletters an {recipient_email}: {e}")
            return False
    
    def send_newsletters_batch(self, newsletters: List[Dict]) -> Dict:
        """Sendet Newsletter an mehrere Empfänger"""
        results = {
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        for newsletter in newsletters:
            subscriber = newsletter.get('subscriber')
            if not subscriber:
                results['failed'] += 1
                results['errors'].append("Kein Abonnent-Information verfügbar")
                continue
            
            recipient_email = subscriber.get('email')
            recipient_name = subscriber.get('name')
            
            if not recipient_email:
                results['failed'] += 1
                results['errors'].append(f"Keine E-Mail-Adresse für Abonnent {subscriber.get('id', 'unbekannt')}")
                continue
            
            success = self.send_newsletter(newsletter, recipient_email, recipient_name)
            
            if success:
                results['sent'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"Fehler beim Senden an {recipient_email}")
        
        logger.info(f"Newsletter-Versand abgeschlossen: {results['sent']} erfolgreich, {results['failed']} fehlgeschlagen")
        return results
    
    def send_welcome_email(self, subscriber_email: str, subscriber_name: Optional[str] = None) -> bool:
        """Sendet eine Willkommens-E-Mail an neue Abonnenten"""
        try:
            subject = "Willkommen beim Medizintechnik Newsletter"
            
            # HTML-Inhalt
            html_content = f"""
            <!DOCTYPE html>
            <html lang="de">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Willkommen</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background-color: white;
                        padding: 30px;
                        border: 1px solid #e0e0e0;
                        border-radius: 0 0 10px 10px;
                    }}
                    .highlight {{
                        background-color: #e3f2fd;
                        padding: 20px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Willkommen!</h1>
                    <p>Medizintechnik & Healthcare Newsletter</p>
                </div>
                <div class="content">
                    <p>Hallo{' ' + subscriber_name if subscriber_name else ''},</p>
                    
                    <p>vielen Dank für Ihr Interesse an unserem Medizintechnik Newsletter! Sie haben sich erfolgreich angemeldet und werden ab sofort über wichtige Änderungen in Normen, Gesetzen und Regulierungen im Bereich Medizintechnik und Healthcare informiert.</p>
                    
                    <div class="highlight">
                        <h3>Was Sie erwarten können:</h3>
                        <ul>
                            <li>Aktuelle Informationen zu Regulierungsänderungen</li>
                            <li>Updates von FDA, BfArM, ISO und TÜV</li>
                            <li>Personalisierte Inhalte basierend auf Ihren Interessen</li>
                            <li>Übersichtliche Zusammenfassungen wichtiger Änderungen</li>
                        </ul>
                    </div>
                    
                    <p>Unser KI-System überwacht kontinuierlich offizielle Quellen und informiert Sie automatisch über relevante Änderungen. Sie erhalten nur dann einen Newsletter, wenn tatsächlich wichtige Neuigkeiten vorliegen.</p>
                    
                    <p>Falls Sie Fragen haben oder Ihre Einstellungen ändern möchten, können Sie jederzeit antworten oder den Newsletter abbestellen.</p>
                    
                    <p>Vielen Dank für Ihr Vertrauen!</p>
                    
                    <p>Ihr Medizintechnik Newsletter Team</p>
                </div>
            </body>
            </html>
            """
            
            # Text-Inhalt
            text_content = f"""
Willkommen beim Medizintechnik Newsletter!

Hallo{' ' + subscriber_name if subscriber_name else ''},

vielen Dank für Ihr Interesse an unserem Medizintechnik Newsletter! Sie haben sich erfolgreich angemeldet und werden ab sofort über wichtige Änderungen in Normen, Gesetzen und Regulierungen im Bereich Medizintechnik und Healthcare informiert.

Was Sie erwarten können:
- Aktuelle Informationen zu Regulierungsänderungen
- Updates von FDA, BfArM, ISO und TÜV
- Personalisierte Inhalte basierend auf Ihren Interessen
- Übersichtliche Zusammenfassungen wichtiger Änderungen

Unser KI-System überwacht kontinuierlich offizielle Quellen und informiert Sie automatisch über relevante Änderungen. Sie erhalten nur dann einen Newsletter, wenn tatsächlich wichtige Neuigkeiten vorliegen.

Falls Sie Fragen haben oder Ihre Einstellungen ändern möchten, können Sie jederzeit antworten oder den Newsletter abbestellen.

Vielen Dank für Ihr Vertrauen!

Ihr Medizintechnik Newsletter Team
            """
            
            # Erstelle und sende E-Mail
            msg = Message(
                subject=subject,
                sender=self.config.get('MAIL_DEFAULT_SENDER'),
                recipients=[subscriber_email]
            )
            
            msg.html = html_content
            msg.body = text_content
            
            if self.mail:
                self.mail.send(msg)
                logger.info(f"Willkommens-E-Mail erfolgreich an {subscriber_email} gesendet")
                return True
            else:
                logger.error("E-Mail-Service nicht initialisiert")
                return False
                
        except Exception as e:
            logger.error(f"Fehler beim Senden der Willkommens-E-Mail an {subscriber_email}: {e}")
            return False
    
    def send_unsubscribe_confirmation(self, subscriber_email: str, subscriber_name: Optional[str] = None) -> bool:
        """Sendet eine Bestätigung für die Abmeldung"""
        try:
            subject = "Abmeldung bestätigt - Medizintechnik Newsletter"
            
            # HTML-Inhalt
            html_content = f"""
            <!DOCTYPE html>
            <html lang="de">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Abmeldung bestätigt</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #f5f5f5;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background-color: white;
                        padding: 30px;
                        border: 1px solid #e0e0e0;
                        border-radius: 0 0 10px 10px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Abmeldung bestätigt</h1>
                </div>
                <div class="content">
                    <p>Hallo{' ' + subscriber_name if subscriber_name else ''},</p>
                    
                    <p>Ihre Abmeldung vom Medizintechnik Newsletter wurde erfolgreich verarbeitet. Sie erhalten ab sofort keine weiteren Newsletter von uns.</p>
                    
                    <p>Falls Sie sich in Zukunft wieder anmelden möchten, können Sie dies jederzeit über unsere Website tun.</p>
                    
                    <p>Vielen Dank für Ihr Interesse und Ihre Zeit!</p>
                    
                    <p>Ihr Medizintechnik Newsletter Team</p>
                </div>
            </body>
            </html>
            """
            
            # Text-Inhalt
            text_content = f"""
Abmeldung bestätigt - Medizintechnik Newsletter

Hallo{' ' + subscriber_name if subscriber_name else ''},

Ihre Abmeldung vom Medizintechnik Newsletter wurde erfolgreich verarbeitet. Sie erhalten ab sofort keine weiteren Newsletter von uns.

Falls Sie sich in Zukunft wieder anmelden möchten, können Sie dies jederzeit über unsere Website tun.

Vielen Dank für Ihr Interesse und Ihre Zeit!

Ihr Medizintechnik Newsletter Team
            """
            
            # Erstelle und sende E-Mail
            msg = Message(
                subject=subject,
                sender=self.config.get('MAIL_DEFAULT_SENDER'),
                recipients=[subscriber_email]
            )
            
            msg.html = html_content
            msg.body = text_content
            
            if self.mail:
                self.mail.send(msg)
                logger.info(f"Abmelde-Bestätigung erfolgreich an {subscriber_email} gesendet")
                return True
            else:
                logger.error("E-Mail-Service nicht initialisiert")
                return False
                
        except Exception as e:
            logger.error(f"Fehler beim Senden der Abmelde-Bestätigung an {subscriber_email}: {e}")
            return False
    
    def test_email_configuration(self) -> bool:
        """Testet die E-Mail-Konfiguration"""
        try:
            # Teste SMTP-Verbindung
            server = smtplib.SMTP(
                self.config.get('MAIL_SERVER'),
                self.config.get('MAIL_PORT')
            )
            
            if self.config.get('MAIL_USE_TLS'):
                server.starttls()
            
            if self.config.get('MAIL_USERNAME') and self.config.get('MAIL_PASSWORD'):
                server.login(
                    self.config.get('MAIL_USERNAME'),
                    self.config.get('MAIL_PASSWORD')
                )
            
            server.quit()
            logger.info("E-Mail-Konfiguration erfolgreich getestet")
            return True
            
        except Exception as e:
            logger.error(f"E-Mail-Konfiguration fehlgeschlagen: {e}")
            return False
    
    def send_admin_notification(self, subject: str, message: str) -> bool:
        """Sendet eine Benachrichtigung an den Administrator"""
        try:
            admin_email = self.config.get('MAIL_DEFAULT_SENDER')
            if not admin_email:
                logger.warning("Keine Administrator-E-Mail konfiguriert")
                return False
            
            msg = Message(
                subject=f"[Medizintechnik Newsletter] {subject}",
                sender=admin_email,
                recipients=[admin_email]
            )
            
            msg.body = f"""
Automatische Benachrichtigung vom Medizintechnik Newsletter System

Zeit: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
Betreff: {subject}

Nachricht:
{message}

---
Diese Nachricht wurde automatisch generiert.
            """
            
            if self.mail:
                self.mail.send(msg)
                logger.info(f"Administrator-Benachrichtigung gesendet: {subject}")
                return True
            else:
                logger.error("E-Mail-Service nicht initialisiert")
                return False
                
        except Exception as e:
            logger.error(f"Fehler beim Senden der Administrator-Benachrichtigung: {e}")
            return False

