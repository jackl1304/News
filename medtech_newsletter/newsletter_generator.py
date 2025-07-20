"""Modul zur Generierung von personalisierten Newslettern."""
from datetime import datetime
from typing import Dict, List, Optional

from loguru import logger
from jinja2 import Template


class NewsletterGenerator:
    """Klasse für die Generierung von personalisierten Newslettern"""
    
    def __init__(self):
        self.html_template = self._create_html_template()
        self.text_template = self._create_text_template()
    
    def _create_html_template(self) -> Template:
        """Erstellt das HTML-Template für den Newsletter"""
        html_content = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ newsletter_title }}</title>
    <style>
        body {
            font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .container {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 300;
        }
        .header .subtitle {
            margin: 10px 0 0 0;
            font-size: 16px;
            opacity: 0.9;
        }
        .content {
            padding: 30px;
        }
        .greeting {
            font-size: 18px;
            margin-bottom: 25px;
            color: #555;
        }
        .summary {
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 20px;
            margin: 25px 0;
            border-radius: 0 5px 5px 0;
        }
        .summary h3 {
            margin-top: 0;
            color: #1976d2;
        }
        .change-item {
            background-color: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin: 20px 0;
            overflow: hidden;
            transition: box-shadow 0.3s ease;
        }
        .change-item:hover {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        .change-header {
            background-color: #f5f5f5;
            padding: 15px 20px;
            border-bottom: 1px solid #e0e0e0;
        }
        .change-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin: 0;
        }
        .change-meta {
            font-size: 14px;
            color: #666;
            margin: 5px 0 0 0;
        }
        .change-content {
            padding: 20px;
        }
        .change-summary {
            font-size: 16px;
            margin-bottom: 15px;
            color: #555;
        }
        .change-details {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .change-details h4 {
            margin: 0 0 10px 0;
            color: #333;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .change-details ul {
            margin: 0;
            padding-left: 20px;
        }
        .change-details li {
            margin: 5px 0;
            color: #666;
        }
        .importance-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .importance-high {
            background-color: #ffebee;
            color: #c62828;
        }
        .importance-medium {
            background-color: #fff3e0;
            color: #ef6c00;
        }
        .importance-low {
            background-color: #e8f5e8;
            color: #2e7d32;
        }
        .source-badge {
            display: inline-block;
            padding: 4px 8px;
            background-color: #e3f2fd;
            color: #1976d2;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            margin-left: 10px;
        }
        .icon-placeholder {
            width: 24px;
            height: 24px;
            background-color: #ddd;
            border-radius: 50%;
            display: inline-block;
            margin-right: 10px;
            vertical-align: middle;
        }
        .footer {
            background-color: #f5f5f5;
            padding: 25px;
            text-align: center;
            border-top: 1px solid #e0e0e0;
        }
        .footer p {
            margin: 5px 0;
            color: #666;
            font-size: 14px;
        }
        .footer a {
            color: #667eea;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .no-changes {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .no-changes .icon-placeholder {
            width: 64px;
            height: 64px;
            margin: 0 auto 20px auto;
            display: block;
        }
        @media (max-width: 600px) {
            body {
                padding: 10px;
            }
            .header {
                padding: 20px;
            }
            .header h1 {
                font-size: 24px;
            }
            .content {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ newsletter_title }}</h1>
            <p class="subtitle">Medizintechnik & Healthcare Regulierungen</p>
        </div>
        
        <div class="content">
            <div class="greeting">
                <span class="icon-placeholder"></span>
                Hallo{% if subscriber_name %} {{ subscriber_name }}{% endif %},
            </div>
            
            {% if changes|length > 0 %}
                <div class="summary">
                    <h3>Zusammenfassung</h3>
                    <p>In diesem Newsletter informieren wir Sie über {{ changes|length }} wichtige 
                    Änderung{% if changes|length != 1 %}en{% endif %} in den Medizintechnik- und 
                    Healthcare-Regulierungen. Die Informationen stammen aus vertrauenswürdigen 
                    Quellen wie FDA, BfArM, ISO und TÜV.</p>
                </div>
                
                {% for change in changes %}
                <div class="change-item">
                    <div class="change-header">
                        <h2 class="change-title">
                            <span class="icon-placeholder"></span>
                            {{ change.title }}
                        </h2>
                        <p class="change-meta">
                            <span class="source-badge">{{ change.source }}</span>
                            {% if change.importance_level %}
                                <span class="importance-badge 
                                importance-{{ change.importance_level }}">
                                    {{ change.importance_level|title }} Priorität
                                </span>
                            {% endif %}
                            {% if change.detected_at %}
                                <span style="color: #999; margin-left: 10px;">
                                    Erkannt am {{ change.detected_at }}
                                </span>
                            {% endif %}
                        </p>
                    </div>
                    
                    <div class="change-content">
                        <div class="change-summary">
                            {{ change.summary }}
                        </div>
                        
                        {% if change.key_topics %}
                        <div class="change-details">
                            <h4>Betroffene Bereiche</h4>
                            <ul>
                                {% for topic in change.key_topics %}
                                <li>{{ topic }}</li>
                                {% endfor %}
                            </ul>
                        </div>
                        {% endif %}
                        
                        {% if change.regulations or change.standards %}
                        <div class="change-details">
                            <h4>Relevante Normen und Regulierungen</h4>
                            <ul>
                                {% for regulation in change.regulations %}
                                <li>{{ regulation }}</li>
                                {% endfor %}
                                {% for standard in change.standards %}
                                <li>{{ standard }}</li>
                                {% endfor %}
                            </ul>
                        </div>
                        {% endif %}
                        
                        {% if change.dates %}
                        <div class="change-details">
                            <h4>Wichtige Termine</h4>
                            <ul>
                                {% for date in change.dates %}
                                <li>{{ date }}</li>
                                {% endfor %}
                            </ul>
                        </div>
                        {% endif %}
                        
                        {% if change.url %}
                        <p style="margin-top: 20px;">
                            <a href="{{ change.url }}" style="color: #667eea; 
                            text-decoration: none; font-weight: 500;">
                                → Vollständiges Dokument anzeigen
                            </a>
                        </p>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-changes">
                    <div class="icon-placeholder"></div>
                    <h3>Keine neuen Änderungen</h3>
                    <p>In diesem Zeitraum wurden keine signifikanten Änderungen in den überwachten 
                    Regulierungen und Standards erkannt.</p>
                </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p><strong>Medizintechnik Newsletter</strong></p>
            <p>Automatisch generiert am {{ generation_date }}</p>
            <p>
                <a href="#">Newsletter abbestellen</a> | 
                <a href="#">Einstellungen ändern</a> | 
                <a href="#">Archiv anzeigen</a>
            </p>
            <p style="font-size: 12px; margin-top: 15px;">
                Dieser Newsletter wird automatisch generiert und überwacht Änderungen in 
                Medizintechnik-Regulierungen. Die Informationen dienen nur zur Information 
                und ersetzen keine rechtliche Beratung.
            </p>
        </div>
    </div>
</body>
</html>
        """
        return Template(html_content)
    
    def _create_text_template(self) -> Template:
        """Erstellt das Text-Template für den Newsletter"""
        text_content = """
{{ newsletter_title }}
Medizintechnik & Healthcare Regulierungen
{{ "=" * 60 }}

Hallo{% if subscriber_name %} {{ subscriber_name }}{% endif %},

{% if changes|length > 0 %}
ZUSAMMENFASSUNG
{{ "-" * 15 }}
In diesem Newsletter informieren wir Sie über {{ changes|length }} wichtige 
Änderung{% if changes|length != 1 %}en{% endif %} in den Medizintechnik- und 
Healthcare-Regulierungen. Die Informationen stammen aus vertrauenswürdigen 
Quellen wie FDA, BfArM, ISO und TÜV.

{% for change in changes %}
{{ loop.index }}. {{ change.title }}
{{ "-" * (change.title|length + 3) }}

Quelle: {{ change.source }}
{% if change.importance_level %}Priorität: {{ change.importance_level|title }}{% endif %}
{% if change.detected_at %}Erkannt am: {{ change.detected_at }}{% endif %}

{{ change.summary }}

{% if change.key_topics %}
Betroffene Bereiche:
{% for topic in change.key_topics %}
- {{ topic }}
{% endfor %}
{% endif %}

{% if change.regulations or change.standards %}
Relevante Normen und Regulierungen:
{% for regulation in change.regulations %}
- {{ regulation }}
{% endfor %}
{% for standard in change.standards %}
- {{ standard }}
{% endfor %}
{% endif %}

{% if change.dates %}
Wichtige Termine:
{% for date in change.dates %}
- {{ date }}
{% endfor %}
{% endif %}

{% if change.url %}
Vollständiges Dokument: {{ change.url }}
{% endif %}

{% endfor %}
{% else %}
KEINE NEUEN ÄNDERUNGEN
{{ "-" * 25 }}
In diesem Zeitraum wurden keine signifikanten Änderungen in den überwachten 
Regulierungen und Standards erkannt.
{% endif %}

{{ "=" * 60 }}
Medizintechnik Newsletter
Automatisch generiert am {{ generation_date }}

Newsletter abbestellen: [Link]
Einstellungen ändern: [Link]
Archiv anzeigen: [Link]

Dieser Newsletter wird automatisch generiert und überwacht Änderungen in 
Medizintechnik-Regulierungen. Die Informationen dienen nur zur Information 
und ersetzen keine rechtliche Beratung.
        """
        return Template(text_content)
    
    def generate_newsletter(self, changes: List[Dict], subscriber: Optional[Dict] = None) -> Dict:
        """Generiert einen personalisierten Newsletter"""
        
        # Sortiere Änderungen nach Wichtigkeit
        sorted_changes = sorted(changes, key=lambda x: x.get(
            \'importance_score\', 0), reverse=True)
        
        # Bereite Daten für Template vor
        template_data = {
            \'newsletter_title\': self._generate_title(sorted_changes),
            \'subscriber_name\': subscriber.get(\'name\') if subscriber else None,
            \'changes\': self._prepare_changes_for_template(sorted_changes, subscriber),
            \'generation_date\': datetime.now().strftime(\'%d.%m.%Y um %H:%M Uhr\')
        }
        
        # Generiere HTML und Text Versionen
        html_content = self.html_template.render(**template_data)
        text_content = self.text_template.render(**template_data)
        
        return {
            \'title\': template_data[\'newsletter_title\'],
            \'html_content\': html_content,
            \'text_content\': text_content,
            \'changes_count\': len(sorted_changes),
            \'subscriber_id\': subscriber.get(\'id\') if subscriber else None
        }
    
    def _generate_title(self, changes: List[Dict]) -> str:
        """Generiert einen aussagekräftigen Titel für den Newsletter"""
        if not changes:
            return f"Medizintechnik Newsletter - {datetime.now().strftime(\'%B %Y\')}"
        
        change_count = len(changes)
        current_date = datetime.now().strftime(\'%B %Y\')
        
        if change_count == 1:
            return f"Wichtige Regulierungsänderung - {current_date}"
        
        if change_count <= 3:
            return f"{change_count} neue Regulierungsänderungen - {current_date}"
        
        return f"Umfassende Regulierungsupdate - {current_date}"
    
    def _prepare_changes_for_template(self, changes: List[Dict], 
                                       subscriber: Optional[Dict] = None) -> List[Dict]:
        """Bereitet Änderungen für das Template vor und personalisiert sie"""
        prepared_changes = []
        
        for change in changes:
            # Bestimme Wichtigkeitslevel
            importance_score = change.get(\'importance_score\', 0)
            if importance_score >= 70:
                importance_level = \'high\'
            elif importance_score >= 40:
                importance_level = \'medium\'
            else:
                importance_level = \'low\'
            
            # Personalisierung basierend auf Abonnenten-Interessen
            if subscriber and subscriber.get(\'interests\'):
                relevance = self._calculate_relevance(change, subscriber[\'interests\'])
                if relevance < 0.3:  # Mindest-Relevanz-Schwelle
                    continue
            
            prepared_change = {
                \'title\': change.get(\'title\', \'Unbekannte Änderung\'),
                \'source\': change.get(\'source\', \'Unbekannt\'),
                \'summary\': self._create_change_summary(change),
                \'importance_level\': importance_level,
                \'importance_score\': importance_score,
                \'detected_at\': self._format_date(change.get(\'detected_at\')),
                \'url\': change.get(\'url\'),
                \'key_topics\': change.get(\'key_topics\', []),
                \'regulations\': change.get(\'regulations\', []),
                \'standards\': change.get(\'standards\', []),
                \'dates\': change.get(\'dates\', [])
            }
            
            prepared_changes.append(prepared_change)
        
        return prepared_changes
    
    def _create_change_summary(self, change: Dict) -> str:
        """Erstellt eine aussagekräftige Zusammenfassung der Änderung"""
        summary = change.get(\'change_summary\', \'\')
        
        if not summary:
            # Fallback: Erstelle Zusammenfassung aus verfügbaren Daten
            change_type = change.get(\'change_type\', \'update\')
            source = change.get(\'source\', \'einer Quelle\')
            
            if change_type == \'new\':
                summary = f"Ein neues Dokument wurde von {source} veröffentlicht."
            elif change_type == \'major_update\':
                summary = f"Ein wichtiges Dokument von {source} wurde erheblich überarbeitet."
            elif change_type == \'moderate_update\':
                summary = f"Ein Dokument von {source} wurde aktualisiert."
            else:
                summary = f"Änderungen in einem Dokument von {source} wurden erkannt."
        
        # Erweitere Zusammenfassung mit wichtigen Details
        if change.get(\'key_topics\'):
            topics = \', \'.join(change[\'key_topics\'][:3])  # Erste 3 Themen
            summary += f" Betroffene Bereiche: {topics}."
        
        if change.get(\'change_indicators\'):
            indicators = change[\'change_indicators\'][:2]  # Erste 2 Indikatoren
            summary += f" Wichtige Änderungen: {\', \'.join(indicators)}."
        
        return summary
    
    def _calculate_relevance(self, change: Dict, interests: List[str]) -> float:
        """Berechnet die Relevanz einer Änderung für die Interessen des Abonnenten"""
        if not interests:
            return 1.0  # Wenn keine Interessen definiert, ist alles relevant
        
        relevance_score = 0.0
        total_weight = 0
        
        # Prüfe Übereinstimmung mit Themen
        change_topics = [topic.lower() for topic in change.get(\'key_topics\', [])]
        for interest in interests:
            interest_lower = interest.lower()
            weight = 1.0
            
            # Direkte Übereinstimmung
            if interest_lower in change_topics:
                relevance_score += weight
            
            # Teilweise Übereinstimmung
            for topic in change_topics:
                if interest_lower in topic or topic in interest_lower:
                    relevance_score += weight * 0.5
            
            total_weight += weight
        
        # Prüfe Übereinstimmung mit Regulierungen und Standards
        regulations_standards = change.get(\'regulations\', []) + change.get(\'standards\', [])
        for item in regulations_standards:
            for interest in interests:
                if interest.lower() in item.lower():
                    relevance_score += 0.5
                    total_weight += 0.5
        
        return min(relevance_score / max(total_weight, 1), 1.0) if total_weight > 0 else 0.5
    
    def _format_date(self, date_input: Optional[str]) -> Optional[str]:
        """Formatiert ein Datum für die Anzeige"""
        if date_input is None:
            return None
        
        if isinstance(date_input, datetime):
            return date_input.strftime(\'%d.%m.%Y\')
        
        if isinstance(date_input, str):
            # Versuche verschiedene Datumsformate zu parsen
            for fmt in [\' %Y-%m-%d %H:%M:%S\', \'%Y-%m-%d\', \'%d.%m.%Y\', \'%d/%m/%Y\']:
                try:
                    dt = datetime.strptime(date_input, fmt)
                    return dt.strftime(\'%d.%m.%Y\')
                except ValueError:
                    continue
        
        return str(date_input) # Fallback für unbekannte Typen oder Formate
    
    def generate_personalized_newsletters(self, changes: List[Dict], 
                                          subscribers: List[Dict]) -> List[Dict]:
        """Generiert personalisierte Newsletter für alle Abonnenten"""
        newsletters = []
        
        for subscriber in subscribers:
            if not subscriber.get(\'is_active\', True):
                continue
            
            # Filtere Änderungen basierend auf Abonnenten-Interessen
            relevant_changes = []
            for change in changes:
                if subscriber.get(\'interests\'):
                    relevance = self._calculate_relevance(change, subscriber[\'interests\'])
                    if relevance < 0.3:  # Mindest-Relevanz-Schwelle
                        relevant_changes.append(change)
                else:
                    relevant_changes.append(change)  # Alle Änderungen wenn keine Interessen definiert
            
            # Generiere Newsletter nur wenn relevante Änderungen vorhanden
            if relevant_changes or not changes:  # Sende auch leere Newsletter
                newsletter = self.generate_newsletter(relevant_changes, subscriber)
                newsletter[\'subscriber\'] = subscriber
                newsletters.append(newsletter)
        
        logger.info(f"Generierte {len(newsletters)} personalisierte Newsletter für "
                    f"{len(subscribers)} Abonnenten")
        return newsletters
