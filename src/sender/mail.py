# src/sender/mail.py

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(html_content: str, subject: str = "News-Update") -> None:
    """
    Versendet eine HTML-Mail an alle Empfänger aus RECIPIENTS (Komma-getrennt).
    SMTP-Konfiguration aus Umgebungsvariablen:
      SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, RECIPIENTS
    """
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', 465))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    recipients = os.getenv('RECIPIENTS', '')

    if not all([smtp_host, smtp_user, smtp_pass, recipients]):
        raise RuntimeError("SMTP-Umgebungsvariablen nicht vollständig gesetzt")

    # MIME-Message zusammenbauen
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = recipients

    part = MIMEText(html_content, 'html')
    msg.attach(part)

    # Verbindung herstellen und senden
    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, recipients.split(','), msg.as_string())
