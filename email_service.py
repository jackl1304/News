from flask_mail import Mail, Message
from flask import current_app
# ... (andere Imports bleiben gleich)
from loguru import logger


class EmailService:
    # ... (init_app und andere Methoden bleiben unverändert) ...

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
            <html lang="de">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: sans-serif; max-width: 600px; margin: auto; color: #333; }}
                    .header img {{ max-width: 100%; }}
                    .content {{ padding: 20px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <img src="{header_image_url}" alt="Willkommen beim Medizintechnik Newsletter">
                </div>
                <div class="content">
                    <h2>Willkommen, {greeting_name}!</h2>
                    <p>Vielen Dank für Ihre Anmeldung. Sie werden ab sofort über wichtige Änderungen in Normen, Gesetzen und Regulierungen im Bereich Medizintechnik und Healthcare informiert.</p>
                    <p>Ihr Medizintechnik Newsletter Team</p>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                sender=self.config.get('MAIL_DEFAULT_S
