"""Modul für den E-Mail-Versanddienst."""
import os

from flask import current_app
from flask_mail import Mail, Message
from loguru import logger


class EmailService:
    """Verwaltet den Versand von E-Mails für die Anwendung."""
    def __init__(self, app=None):
        self.mail = Mail()
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialisiert den Mail-Service mit der Flask-Anwendung."""
        self.mail.init_app(app)
        self.config = app.config

    def send_welcome_email(self, subscriber_email: str, subscriber_name: str) -> bool:
        """Sendet eine Willkommens-E-Mail an neue Abonnenten mit einem Header-Bild."""
        if not hasattr(self, 'mail') or not self.mail:
            # Stellt sicher, dass der Mail-Service initialisiert ist
            self.init_app(current_app._get_current_object())

        try:
            subject = "Willkommen beim Medizintechnik Newsletter"
            greeting_name = subscriber_name if subscriber_name else subscriber_email
            
            # Das Bild wird direkt von einer URL geladen
            header_image_url = "https://i.imgur.com/your-image-id.jpg" # HINWEIS: Laden Sie Ihr Bild bei einem Hoster wie imgur.com hoch und fügen Sie hier den direkten Link ein.

            html_content = f"""
            <!DOCTYPE html>
            <html lang=\"de\">
            <head>
                <meta charset=\"UTF-8\">
                <style>
                    body {{ font-family: sans-serif; max-width: 600px; margin: auto; color: #333; }}
                    .header img {{ max-width: 100%; }}
                    .content {{ padding: 20px; }}
                </style>
            </head>
            <body>
                <div class=\"header\">
                    <h2>Willkommen, {greeting_name}!</h2>
                    <p>Vielen Dank für Ihre Anmeldung. Sie werden ab sofort über wichtige Änderungen in Normen, Gesetzen und Regulierungen im Bereich Medizintechnik und Healthcare informiert.</p>
                    <p>Ihr Medizintechnik Newsletter Team</p>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                sender=self.config.get(\'MAIL_DEFAULT_SENDER\', \'noreply@example.com\' ),
                recipients=[subscriber_email],
                html=html_content
            )
            self.mail.send(msg)
            logger.info(f"Willkommens-E-Mail an {subscriber_email} gesendet.")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Senden der Willkommens-E-Mail an {subscriber_email}: {e}")
            return False

    def send_newsletter(self, recipient_email: str, subject: str, html_content: str) -> bool:
        """Sendet den generierten Newsletter an einen Empfänger."""
        if not hasattr(self, 'mail') or not self.mail:
            self.init_app(current_app._get_current_object())

        try:
            msg = Message(
                subject=subject,
                sender=self.config.get(\'MAIL_DEFAULT_SENDER\', \'noreply@example.com\'),
                recipients=[recipient_email],
                html=html_content
            )
            self.mail.send(msg)
            logger.info(f"Newsletter an {recipient_email} gesendet.")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Senden des Newsletters an {recipient_email}: {e}")
            return False

    def send_test_email(self, recipient_email: str) -> bool:
        """Sendet eine Test-E-Mail."""
        if not hasattr(self, 'mail') or not self.mail:
            self.init_app(current_app._get_current_object())

        try:
            msg = Message(
                subject="Test-E-Mail vom Medizintechnik Newsletter",
                sender=self.config.get(\'MAIL_DEFAULT_SENDER\', \'noreply@example.com\'),
                recipients=[recipient_email],
                body="Dies ist eine Test-E-Mail von Ihrem Medizintechnik Newsletter Service."
            )
            self.mail.send(msg)
            logger.info(f"Test-E-Mail an {recipient_email} gesendet.")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Senden der Test-E-Mail an {recipient_email}: {e}")
            return False
