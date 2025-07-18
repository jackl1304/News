# Benutzerhandbuch: Medizintechnik Newsletter AI

## 📖 Inhaltsverzeichnis

1. [Einführung](#einführung)
2. [Erste Schritte](#erste-schritte)
3. [Benutzeroberfläche](#benutzeroberfläche)
4. [Admin-Dashboard](#admin-dashboard)
5. [Newsletter-Verwaltung](#newsletter-verwaltung)
6. [Abonnenten-Verwaltung](#abonnenten-verwaltung)
7. [System-Überwachung](#system-überwachung)
8. [Fehlerbehebung](#fehlerbehebung)
9. [FAQ](#faq)

## 🎯 Einführung

Das Medizintechnik Newsletter AI-System ist eine intelligente Lösung zur automatischen Überwachung von Regulierungsänderungen in der Medizintechnik- und Healthcare-Branche. Das System überwacht kontinuierlich offizielle Quellen und benachrichtigt Abonnenten über relevante Änderungen.

### Hauptfunktionen

- **Automatische Datenerfassung** von FDA, BfArM, ISO, TÜV und anderen Quellen
- **KI-basierte Textanalyse** zur Erkennung relevanter Änderungen
- **Personalisierte Newsletter** basierend auf Interessensgebieten
- **Web-basierte Verwaltung** mit Admin-Dashboard
- **Automatisierte Zeitplanung** für regelmäßige Aufgaben

## 🚀 Erste Schritte

### Für Endnutzer (Newsletter-Abonnenten)

#### 1. Newsletter abonnieren

1. Besuchen Sie die Hauptseite: `https://ihr-domain.com`
2. Füllen Sie das Anmeldeformular aus:
   - **E-Mail-Adresse** (Pflichtfeld)
   - **Name** (optional, aber empfohlen)
   - **Unternehmen** (optional)
   - **Interessensgebiete** (optional, für Personalisierung)
3. Wählen Sie relevante Interessensgebiete aus:
   - Medical Device Regulation (MDR)
   - In Vitro Diagnostic (IVD)
   - Quality Management
   - Risk Management
   - Clinical Evaluation
   - Biocompatibility
   - Medical Device Software
   - Sterilization
4. Klicken Sie auf "Jetzt anmelden"
5. Sie erhalten eine Bestätigungs-E-Mail

#### 2. Newsletter erhalten

- Newsletter werden automatisch versendet, wenn relevante Änderungen erkannt werden
- Frequenz: Nur bei tatsächlichen Änderungen (kann von täglich bis monatlich variieren)
- Inhalt: Zusammenfassung der Änderungen, Links zu Originaldokumenten, relevante Abschnitte

#### 3. Newsletter abbestellen

1. Besuchen Sie: `https://ihr-domain.com/unsubscribe`
2. Geben Sie Ihre E-Mail-Adresse ein
3. Klicken Sie auf "Abmelden"
4. Sie erhalten eine Bestätigungs-E-Mail

### Für Administratoren

#### 1. Admin-Dashboard aufrufen

1. Besuchen Sie: `https://ihr-domain.com/admin`
2. Das Dashboard zeigt aktuelle Statistiken und System-Status

#### 2. Erste Konfiguration

1. Überprüfen Sie die System-Einstellungen
2. Testen Sie die E-Mail-Konfiguration
3. Starten Sie das erste manuelle Scraping
4. Überprüfen Sie die Scheduler-Einstellungen

## 🖥️ Benutzeroberfläche

### Hauptseite

Die Hauptseite bietet eine übersichtliche Darstellung der Funktionen:

#### Header-Navigation
- **Home**: Zurück zur Hauptseite
- **Abmelden**: Newsletter-Abmeldung
- **Admin**: Admin-Dashboard (nur für Administratoren)

#### Anmeldebereich
- **Anmeldeformular**: Zentral platziert mit allen erforderlichen Feldern
- **Interessensgebiete**: Checkboxen für Personalisierung
- **Bestätigungsmodal**: Erfolgreiche Anmeldung wird bestätigt

#### Features-Übersicht
- **KI-basierte Überwachung**: Automatische Erkennung von Änderungen
- **Vertrauenswürdige Quellen**: Nur autorisierte Stellen
- **Personalisierte Inhalte**: Basierend auf Interessensgebieten
- **Zeitnahe Benachrichtigung**: Schnelle Informationsübermittlung

### Responsive Design

Das System ist vollständig responsive und funktioniert auf:
- **Desktop**: Optimale Darstellung auf großen Bildschirmen
- **Tablet**: Angepasste Navigation und Formulare
- **Mobile**: Touch-optimierte Bedienung

## 🎛️ Admin-Dashboard

### Übersicht

Das Admin-Dashboard bietet eine zentrale Verwaltungsoberfläche für alle Systemfunktionen.

#### Statistik-Karten

1. **Aktive Abonnenten**
   - Zeigt die Anzahl der registrierten Newsletter-Abonnenten
   - Klickbar für detaillierte Liste

2. **Überwachte Dokumente**
   - Anzahl der aktuell überwachten Dokumente
   - Zeigt Status der letzten Überprüfung

3. **Unverarbeitete Änderungen**
   - Erkannte Änderungen, die noch nicht in Newsletter verarbeitet wurden
   - Warnung bei hoher Anzahl

4. **Letzte Newsletter**
   - Anzahl der kürzlich generierten Newsletter
   - Links zur Vorschau

#### Scheduler-Status

- **Status**: Läuft/Gestoppt
- **Aktive Jobs**: Liste der geplanten Aufgaben
- **Nächste Ausführung**: Zeitpunkt der nächsten automatischen Ausführung

### Funktionen

#### Manuelle Aktionen

1. **Manuelles Scraping**
   - Startet sofortige Überprüfung aller Quellen
   - Dauer: 5-15 Minuten je nach Anzahl der Quellen
   - Status wird in Echtzeit angezeigt

2. **Newsletter generieren**
   - Erstellt Newsletter basierend auf erkannten Änderungen
   - Versendet automatisch an alle Abonnenten
   - Vorschau vor Versand möglich

#### Datenansichten

1. **Alle Abonnenten anzeigen**
   - Vollständige Liste aller registrierten Nutzer
   - Filtermöglichkeiten nach Interessensgebieten
   - Export-Funktionen

2. **Alle Dokumente anzeigen**
   - Liste der überwachten Dokumente
   - Status der letzten Überprüfung
   - Möglichkeit, neue Quellen hinzuzufügen

3. **Änderungen anzeigen**
   - Chronologische Liste aller erkannten Änderungen
   - Details zu Art und Umfang der Änderungen
   - Status der Verarbeitung

#### System-Verwaltung

1. **System-Status prüfen**
   - Überprüft alle Systemkomponenten
   - Datenbank-Verbindung
   - E-Mail-Service
   - Scheduler-Status

2. **Logs anzeigen**
   - Systemlogs der letzten 24 Stunden
   - Filtermöglichkeiten nach Log-Level
   - Download-Option für detaillierte Analyse

## 📧 Newsletter-Verwaltung

### Automatische Generierung

#### Trigger-Bedingungen
- Neue Dokumente in überwachten Quellen
- Änderungen in bestehenden Dokumenten
- Zeitbasierte Generierung (wöchentlich/monatlich)

#### Inhaltserstellung
1. **Änderungsanalyse**: KI analysiert erkannte Änderungen
2. **Relevanz-Bewertung**: Bewertung der Wichtigkeit für verschiedene Zielgruppen
3. **Personalisierung**: Anpassung basierend auf Abonnenten-Interessen
4. **Template-Anwendung**: Professionelle HTML-Formatierung

#### Qualitätskontrolle
- Automatische Rechtschreibprüfung
- Link-Validierung
- Template-Konsistenz
- Spam-Filter-Kompatibilität

### Manuelle Generierung

#### Schritt-für-Schritt Prozess

1. **Admin-Dashboard öffnen**
2. **"Newsletter generieren" klicken**
3. **Bestätigung der Aktion**
4. **Warten auf Verarbeitung** (2-5 Minuten)
5. **Vorschau prüfen** (optional)
6. **Versand bestätigen**

#### Vorschau-Funktionen
- **HTML-Vorschau**: Vollständige Darstellung
- **Text-Vorschau**: Nur-Text-Version
- **Mobile-Vorschau**: Darstellung auf mobilen Geräten
- **Spam-Score**: Bewertung der Zustellbarkeit

### Newsletter-Archiv

#### Zugriff
- Über Admin-Dashboard: "Letzte Newsletter"
- Direkte URL: `/newsletter/{id}`
- API-Endpunkt für programmatischen Zugriff

#### Funktionen
- **Vollständige Historie** aller versendeten Newsletter
- **Suchfunktion** nach Datum, Thema, Quelle
- **Export-Optionen**: PDF, HTML, Text
- **Statistiken**: Öffnungsraten, Klicks, Abmeldungen

## 👥 Abonnenten-Verwaltung

### Abonnenten-Liste

#### Ansicht
- **Tabellarische Darstellung** aller Abonnenten
- **Sortierung** nach Name, E-Mail, Anmeldedatum
- **Filterung** nach Interessensgebieten
- **Suchfunktion** für schnelle Suche

#### Informationen pro Abonnent
- **E-Mail-Adresse**: Primärer Identifikator
- **Name**: Falls angegeben
- **Unternehmen**: Falls angegeben
- **Interessensgebiete**: Ausgewählte Kategorien
- **Anmeldedatum**: Zeitstempel der Registrierung
- **Status**: Aktiv/Inaktiv
- **Letzte Aktivität**: Letzter Newsletter-Empfang

### Abonnenten-Aktionen

#### Einzelaktionen
1. **Abonnent bearbeiten**
   - Interessensgebiete anpassen
   - Kontaktdaten aktualisieren
   - Status ändern

2. **Abonnent löschen**
   - Vollständige Entfernung aus dem System
   - DSGVO-konforme Löschung
   - Bestätigungsschritt erforderlich

3. **Test-Newsletter senden**
   - Einzelversand für Tests
   - Personalisierte Vorschau
   - Debugging-Informationen

#### Massenaktionen
1. **Export**
   - CSV-Format für Excel/Google Sheets
   - JSON-Format für technische Integration
   - Gefilterte Exporte möglich

2. **Import**
   - CSV-Upload für Masseneinfügung
   - Validierung der E-Mail-Adressen
   - Duplikat-Erkennung

3. **Massen-E-Mail**
   - Newsletter an ausgewählte Gruppen
   - Segmentierung nach Interessensgebieten
   - Zeitgesteuerte Versendung

### DSGVO-Compliance

#### Datenschutz-Funktionen
- **Einverständnis-Tracking**: Zeitstempel der Zustimmung
- **Datenminimierung**: Nur notwendige Daten speichern
- **Recht auf Löschung**: Einfache Löschfunktion
- **Datenportabilität**: Export der persönlichen Daten
- **Transparenz**: Klare Datenschutzerklärung

#### Automatische Prozesse
- **Double-Opt-In**: Bestätigung per E-Mail (optional)
- **Abmelde-Links**: In jedem Newsletter
- **Inaktivitäts-Bereinigung**: Automatische Löschung nach X Monaten
- **Audit-Log**: Protokollierung aller Änderungen

## 📊 System-Überwachung

### Health-Checks

#### Automatische Überwachung
- **Datenbank-Verbindung**: Kontinuierliche Prüfung
- **E-Mail-Service**: Regelmäßige Test-E-Mails
- **Scheduler-Status**: Überwachung der geplanten Jobs
- **Speicherplatz**: Warnung bei niedrigem Speicher
- **CPU/RAM-Nutzung**: Performance-Monitoring

#### Health-Endpunkt
- **URL**: `/health`
- **Format**: JSON-Response
- **Informationen**: Status aller Komponenten
- **Verwendung**: Externe Monitoring-Tools

### Logging

#### Log-Kategorien
1. **Application Logs**
   - Anwendungslogik
   - Fehler und Warnungen
   - Performance-Metriken

2. **Access Logs**
   - HTTP-Requests
   - IP-Adressen
   - Response-Zeiten

3. **Scheduler Logs**
   - Job-Ausführungen
   - Erfolg/Fehler-Status
   - Ausführungszeiten

4. **Email Logs**
   - Versendete E-Mails
   - Zustellungsstatus
   - Bounce-Handling

#### Log-Verwaltung
- **Rotation**: Automatische Archivierung alter Logs
- **Komprimierung**: Platzsparende Speicherung
- **Retention**: Konfigurierbare Aufbewahrungszeit
- **Export**: Download für externe Analyse

### Performance-Monitoring

#### Metriken
- **Response-Zeiten**: Durchschnittliche Antwortzeiten
- **Durchsatz**: Requests pro Sekunde
- **Fehlerrate**: Prozentsatz fehlgeschlagener Requests
- **Ressourcennutzung**: CPU, RAM, Disk I/O

#### Alerting
- **E-Mail-Benachrichtigungen**: Bei kritischen Fehlern
- **Schwellenwerte**: Konfigurierbare Limits
- **Eskalation**: Mehrere Benachrichtigungsebenen
- **Integration**: Webhook-Support für externe Tools

## 🔧 Fehlerbehebung

### Häufige Probleme

#### 1. Newsletter werden nicht versendet

**Symptome:**
- Abonnenten erhalten keine E-Mails
- Admin-Dashboard zeigt "0 Newsletter versendet"

**Lösungsschritte:**
1. **E-Mail-Konfiguration prüfen**
   ```bash
   # Health-Check aufrufen
   curl http://localhost:5000/health
   ```
2. **SMTP-Einstellungen validieren**
   - Server-Adresse korrekt?
   - Benutzername/Passwort gültig?
   - Port und Verschlüsselung richtig?
3. **Test-E-Mail senden**
   - Über Admin-Dashboard
   - An eigene E-Mail-Adresse
4. **Logs prüfen**
   ```bash
   tail -f /var/log/medtech-newsletter/app.log | grep -i mail
   ```

#### 2. Scraping funktioniert nicht

**Symptome:**
- Keine neuen Dokumente erkannt
- "Überwachte Dokumente: 0" im Dashboard

**Lösungsschritte:**
1. **Internet-Verbindung prüfen**
   ```bash
   curl -I https://www.fda.gov
   ```
2. **Chrome/ChromeDriver Status**
   ```bash
   which chromedriver
   chromium-browser --version
   ```
3. **Manuelles Scraping starten**
   - Über Admin-Dashboard
   - Logs in Echtzeit verfolgen
4. **Firewall-Einstellungen**
   - Ausgehende Verbindungen erlaubt?
   - Proxy-Konfiguration erforderlich?

#### 3. Scheduler läuft nicht

**Symptome:**
- "Scheduler Status: Gestoppt"
- Keine automatischen Updates

**Lösungsschritte:**
1. **Service-Status prüfen**
   ```bash
   sudo systemctl status medtech-newsletter
   ```
2. **Umgebungsvariable prüfen**
   ```bash
   grep START_SCHEDULER .env
   # Sollte "true" sein
   ```
3. **Service neu starten**
   ```bash
   sudo systemctl restart medtech-newsletter
   ```
4. **Logs analysieren**
   ```bash
   sudo journalctl -u medtech-newsletter -f
   ```

#### 4. Hohe Speichernutzung

**Symptome:**
- Langsame Response-Zeiten
- Server-Warnungen

**Lösungsschritte:**
1. **Speichernutzung analysieren**
   ```bash
   free -h
   ps aux --sort=-%mem | head
   ```
2. **Log-Dateien bereinigen**
   ```bash
   sudo logrotate -f /etc/logrotate.d/medtech-newsletter
   ```
3. **Datenbank optimieren**
   ```sql
   VACUUM ANALYZE;  -- PostgreSQL
   ```
4. **Cache leeren**
   - Browser-Cache
   - Anwendungs-Cache

### Debug-Modi

#### Entwicklungsmodus aktivieren
```bash
# In .env Datei
FLASK_ENV=development
LOG_LEVEL=DEBUG
```

#### Detaillierte Logs
```bash
# Alle Logs in Echtzeit
tail -f /var/log/medtech-newsletter/app.log

# Nur Fehler
grep -i error /var/log/medtech-newsletter/app.log

# Nur E-Mail-bezogene Logs
grep -i mail /var/log/medtech-newsletter/app.log
```

#### Database-Debugging
```sql
-- Abonnenten-Anzahl prüfen
SELECT COUNT(*) FROM subscribers;

-- Letzte Newsletter
SELECT * FROM newsletters ORDER BY created_at DESC LIMIT 5;

-- Erkannte Änderungen
SELECT * FROM document_changes ORDER BY detected_at DESC LIMIT 10;
```

## ❓ FAQ

### Allgemeine Fragen

**Q: Wie oft werden Newsletter versendet?**
A: Newsletter werden nur versendet, wenn tatsächlich relevante Änderungen erkannt werden. Dies kann von täglich bis monatlich variieren, abhängig von der Aktivität der überwachten Quellen.

**Q: Welche Quellen werden überwacht?**
A: Aktuell werden FDA, BfArM, ISO, TÜV und andere autorisierte Stellen überwacht. Die Liste kann erweitert werden.

**Q: Kann ich meine Interessensgebiete nachträglich ändern?**
A: Ja, kontaktieren Sie den Administrator oder melden Sie sich ab und erneut an mit den gewünschten Einstellungen.

**Q: Ist der Service kostenlos?**
A: Das hängt von der Implementierung ab. Kontaktieren Sie den Anbieter für Preisinformationen.

### Technische Fragen

**Q: Welche Browser werden unterstützt?**
A: Alle modernen Browser (Chrome, Firefox, Safari, Edge) werden unterstützt. Mobile Browser sind ebenfalls kompatibel.

**Q: Wie sicher sind meine Daten?**
A: Das System ist DSGVO-konform und verwendet moderne Sicherheitsstandards. Daten werden verschlüsselt übertragen und gespeichert.

**Q: Kann ich das System in meine bestehende IT-Infrastruktur integrieren?**
A: Ja, das System bietet APIs für die Integration in bestehende Systeme.

**Q: Wie wird die Qualität der erkannten Änderungen sichergestellt?**
A: Das KI-System wird kontinuierlich trainiert und verbessert. Zusätzlich gibt es manuelle Überprüfungsprozesse.

### Admin-Fragen

**Q: Wie füge ich neue Überwachungsquellen hinzu?**
A: Neue Quellen können über die Konfigurationsdateien oder das Admin-Interface hinzugefügt werden.

**Q: Kann ich Newsletter-Templates anpassen?**
A: Ja, Templates können über die Template-Dateien angepasst werden. HTML- und CSS-Kenntnisse sind erforderlich.

**Q: Wie erstelle ich Backups?**
A: Automatische Backups sind konfiguriert. Manuelle Backups können über das bereitgestellte Script erstellt werden.

**Q: Wie skaliere ich das System für mehr Nutzer?**
A: Das System kann horizontal und vertikal skaliert werden. Siehe Deployment-Guide für Details.

### Support

**Weitere Hilfe benötigt?**

1. **Dokumentation**: Vollständige Dokumentation in den README-Dateien
2. **Logs**: Prüfen Sie die System-Logs für detaillierte Fehlermeldungen
3. **Health-Check**: Nutzen Sie `/health` für System-Status
4. **Community**: GitHub Issues für technische Fragen
5. **Professional Support**: Kontaktieren Sie den Entwickler für professionellen Support

**Notfall-Kontakt:**
- Bei kritischen Systemausfällen
- Sicherheitsproblemen
- Datenverlust

Das System ist robust und selbstheilend konzipiert, aber bei Problemen stehen umfassende Debugging-Tools zur Verfügung.

