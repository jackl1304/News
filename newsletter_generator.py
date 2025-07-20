from loguru import logger
from datetime import datetime

class NewsletterGenerator:
    """Erstellt den HTML- und Text-Inhalt für einen Newsletter."""

    def __init__(self):
        # Der DocumentAnalyzer wird bei Bedarf innerhalb der Methoden erstellt.
        pass

    def generate_html(self, changes: list) -> dict:
        """
        Generiert den HTML- und Text-Inhalt des Newsletters basierend auf den erkannten Änderungen.
        """
        if not changes:
            return {'html': '', 'text': ''}

        # Sortiere Änderungen nach Wichtigkeit (höchste zuerst)
        try:
            sorted_changes = sorted(changes, key=lambda c: c.importance_score, reverse=True)
        except Exception as e:
            logger.error(f"Fehler beim Sortieren der Änderungen: {e}")
            # Fallback, falls 'importance_score' fehlt
            sorted_changes = changes

        # Baue den HTML-Inhalt auf
        html_body = "<h1>Ihr Medizintechnik-Update</h1>"
        html_body += "<p>Hier sind die neuesten erkannten Änderungen und relevanten Dokumente:</p>"
        
        text_body = "Ihr Medizintechnik-Update\n\n"
        text_body += "Hier sind die neuesten erkannten Änderungen und relevanten Dokumente:\n\n"

        for change in sorted_changes:
            doc = change.document
            html_body += f"""
                <div style="border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
                    <h3><a href="{doc.url}">{doc.title or 'Unbekannter Titel'}</a></h3>
                    <p><strong>Quelle:</strong> {doc.source}</p>
                    <p><strong>Änderungszusammenfassung:</strong> {change.change_summary}</p>
                    <p><em>Wichtigkeit: {change.importance_score}/100</em></p>
                </div>
            """
            text_body += f"Titel: {doc.title or 'Unbekannter Titel'}\n"
            text_body += f"Quelle: {doc.source}\n"
            text_body += f"URL: {doc.url}\n"
            text_body += f"Zusammenfassung: {change.change_summary}\n"
            text_body += f"Wichtigkeit: {change.importance_score}/100\n"
            text_body += "---\n\n"

        # Komplette E-Mail-Vorlage
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; }}
                h1 {{ color: #0d6efd; }}
            </style>
        </head>
        <body>
            {html_body}
        </body>
        </html>
        """

        return {'html': full_html, 'text': text_body}
