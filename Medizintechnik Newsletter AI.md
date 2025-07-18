# Medizintechnik Newsletter AI

Ein intelligentes KI-basiertes System zur automatischen Überwachung von Regulierungsänderungen in der Medizintechnik und Healthcare-Branche.

## 🎯 Funktionen

- **Automatische Datenerfassung**: Überwacht kontinuierlich offizielle Quellen (FDA, BfArM, ISO, TÜV)
- **KI-basierte Textanalyse**: Erkennt automatisch relevante Änderungen in Normen und Gesetzen
- **Personalisierte Newsletter**: Generiert maßgeschneiderte Inhalte basierend auf Abonnenten-Interessen
- **Web-Interface**: Benutzerfreundliche Anmeldung und Admin-Dashboard
- **Automatisierte Zeitplanung**: Regelmäßige Ausführung aller Aufgaben
- **E-Mail-Versand**: Professionelle Newsletter mit HTML und Text-Versionen

## 🏗️ Architektur

### Komponenten

1. **Datenerfassung (Data Acquisition)**
   - Web Scraping mit BeautifulSoup und Selenium
   - Überwachung von FDA, BfArM, ISO, TÜV Websites
   - Automatische Erkennung neuer Dokumente

2. **Datenverarbeitung (Data Processing)**
   - NLP-basierte Textanalyse mit spaCy
   - Änderungsdetektion durch Dokumentvergleich
   - Extraktion von Schlüsselinformationen

3. **Newsletter-Generierung**
   - Personalisierte Inhalte mit Jinja2 Templates
   - HTML und Text-Versionen
   - Responsive Design mit Bootstrap

4. **Web-Anwendung**
   - Flask-basierte REST API
   - Admin-Dashboard für Überwachung
   - Abonnenten-Verwaltung

5. **Automatisierung**
   - APScheduler für zeitgesteuerte Aufgaben
   - Konfigurierbare Intervalle
   - Fehlerbehandlung und Logging

## 🚀 Installation

### Voraussetzungen

- Python 3.11+
- Chrome/Chromium Browser (für Selenium)
- SMTP-Server für E-Mail-Versand

### Setup

1. **Repository klonen**
```bash
git clone <repository-url>
cd medtech_newsletter_ai
```

2. **Virtuelle Umgebung erstellen**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows
```

3. **Abhängigkeiten installieren**
```bash
pip install -r requirements.txt
```

4. **spaCy Modelle herunterladen**
```bash
python -m spacy download de_core_news_sm
python -m spacy download en_core_web_sm
```

5. **Chrome WebDriver installieren**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install chromium-browser chromium-chromedriver

# Oder manuell von https://chromedriver.chromium.org/
```

6. **Umgebungsvariablen konfigurieren**
```bash
cp .env.example .env
# Bearbeiten Sie .env mit Ihren Einstellungen
```

7. **Datenbank initialisieren**
```bash
python -c "from app import create_app; from src.models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

## ⚙️ Konfiguration

### E-Mail-Setup

Für Gmail:
1. App-Passwort erstellen: https://support.google.com/accounts/answer/185833
2. In `.env` eintragen:
```
MAIL_USERNAME=ihre-email@gmail.com
MAIL_PASSWORD=ihr-app-passwort
```

### Scraping-Intervalle

```
SCRAPING_INTERVAL_HOURS=24          # Täglich
NEWSLETTER_GENERATION_INTERVAL_HOURS=168  # Wöchentlich
```

## 🏃‍♂️ Verwendung

### Entwicklungsserver starten

```bash
python app.py
```

Die Anwendung ist dann unter `http://localhost:5000` verfügbar.

### Produktionsserver

```bash
export FLASK_ENV=production
export START_SCHEDULER=true
python app.py
```

### Admin-Dashboard

Besuchen Sie `http://localhost:5000/admin` für:
- Überwachung des System-Status
- Manuelles Auslösen von Scraping und Newsletter-Generierung
- Verwaltung von Abonnenten und Dokumenten
- Anzeige von erkannten Änderungen

## 📊 API-Endpunkte

### Öffentliche Endpunkte

- `GET /` - Hauptseite mit Anmeldeformular
- `POST /subscribe` - Neue Abonnenten registrieren
- `GET|POST /unsubscribe` - Abonnenten abmelden
- `GET /health` - System-Status prüfen

### Admin-Endpunkte

- `GET /admin` - Admin-Dashboard
- `POST /admin/manual-scraping` - Manuelles Scraping
- `POST /admin/manual-newsletter` - Manuelle Newsletter-Generierung
- `GET /admin/subscribers` - Abonnenten-Liste
- `GET /admin/documents` - Dokumente-Liste
- `GET /admin/changes` - Änderungen-Liste
- `GET /admin/newsletters` - Newsletter-Liste

## 🔧 Entwicklung

### Projektstruktur

```
medtech_newsletter_ai/
├── app.py                 # Haupt-Flask-Anwendung
├── config/
│   └── config.py         # Konfiguration
├── src/
│   ├── models.py         # Datenbankmodelle
│   ├── scraper.py        # Web Scraping
│   ├── analyzer.py       # Textanalyse
│   ├── newsletter_generator.py  # Newsletter-Generierung
│   ├── email_service.py  # E-Mail-Versand
│   └── scheduler.py      # Aufgabenplanung
├── templates/            # HTML-Templates
├── static/              # CSS, JS, Bilder
├── data/               # Datenverzeichnis
└── tests/              # Tests
```

### Tests ausführen

```bash
python -m pytest tests/
```

### Logging

Logs werden in `medtech_newsletter.log` gespeichert. Log-Level kann über `LOG_LEVEL` in `.env` konfiguriert werden.

## 🛡️ Sicherheit

- Sichere Passwort-Hashing für Admin-Zugang
- CSRF-Schutz für Formulare
- Rate Limiting für API-Endpunkte
- Validierung aller Eingaben
- Sichere E-Mail-Konfiguration

## 📈 Monitoring

### Metriken

- Anzahl aktiver Abonnenten
- Überwachte Dokumente
- Erkannte Änderungen
- Versendete Newsletter
- System-Performance

### Alerts

Das System sendet automatisch E-Mail-Benachrichtigungen bei:
- Erkannten wichtigen Änderungen
- Fehlern beim Scraping oder Newsletter-Versand
- System-Problemen

## 🔄 Wartung

### Regelmäßige Aufgaben

- **Datenbank-Cleanup**: Alte Newsletter und Änderungen werden automatisch gelöscht
- **Log-Rotation**: Logs werden wöchentlich rotiert
- **Backup**: Regelmäßige Sicherung der Datenbank empfohlen

### Updates

1. Repository aktualisieren
2. Abhängigkeiten prüfen: `pip install -r requirements.txt --upgrade`
3. Datenbankmigrationen ausführen (falls erforderlich)
4. Anwendung neu starten

## 🤝 Beitragen

1. Fork des Repositories erstellen
2. Feature-Branch erstellen: `git checkout -b feature/neue-funktion`
3. Änderungen committen: `git commit -am 'Neue Funktion hinzufügen'`
4. Branch pushen: `git push origin feature/neue-funktion`
5. Pull Request erstellen

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe `LICENSE` Datei für Details.

## 🆘 Support

Bei Fragen oder Problemen:

1. Prüfen Sie die Logs: `tail -f medtech_newsletter.log`
2. Überprüfen Sie die Konfiguration in `.env`
3. Testen Sie die E-Mail-Konfiguration: `GET /health`
4. Erstellen Sie ein Issue im Repository

## 🔮 Roadmap

- [ ] Integration weiterer Datenquellen (EMA, Health Canada)
- [ ] Machine Learning für bessere Relevanz-Bewertung
- [ ] Multi-Language Support
- [ ] Mobile App
- [ ] API für Drittanbieter-Integrationen
- [ ] Advanced Analytics Dashboard
- [ ] Webhook-Support für Echtzeit-Benachrichtigungen

