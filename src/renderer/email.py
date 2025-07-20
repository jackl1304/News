# src/renderer/email.py

from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import os

# Jinja2-Umgebung einrichten
templates_path = os.path.join(os.path.dirname(__file__), os.pardir, 'templates')
env = Environment(
    loader=FileSystemLoader(templates_path),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('newsletter.html')

def render_newsletter(articles: list[dict]) -> str:
    """
    Rendert das HTML für den Newsletter.
    Erwartet eine Liste von Dicts mit keys: title, link, published, source
    """
    # Datum für den Header
    today = datetime.utcnow().date()
    # Rendern und zurückgeben
    return template.render(articles=articles, date=today)
