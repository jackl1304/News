# Deployment-Anleitung: Medizintechnik Newsletter AI

## 🚀 Produktionsbereitstellung

### Übersicht

Dieses Dokument beschreibt die Schritte zur Bereitstellung des Medizintechnik Newsletter AI-Systems in einer Produktionsumgebung.

## 📋 Voraussetzungen

### Server-Anforderungen

#### Minimum-Konfiguration
- **CPU**: 2 vCPUs
- **RAM**: 4 GB
- **Storage**: 20 GB SSD
- **Betriebssystem**: Ubuntu 20.04+ oder CentOS 8+
- **Python**: 3.11+
- **Netzwerk**: Öffentliche IP-Adresse

#### Empfohlene Konfiguration
- **CPU**: 4 vCPUs
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **Betriebssystem**: Ubuntu 22.04 LTS
- **Python**: 3.11
- **Netzwerk**: Load Balancer + CDN

### Cloud-Provider Optionen

#### 1. AWS (Amazon Web Services)
- **EC2 Instance**: t3.medium (2 vCPU, 4 GB RAM)
- **RDS**: PostgreSQL db.t3.micro
- **SES**: E-Mail-Versand
- **CloudWatch**: Monitoring
- **Geschätzte Kosten**: $50-80/Monat

#### 2. Google Cloud Platform
- **Compute Engine**: e2-medium (2 vCPU, 4 GB RAM)
- **Cloud SQL**: PostgreSQL db-f1-micro
- **SendGrid**: E-Mail-Versand
- **Cloud Monitoring**: Überwachung
- **Geschätzte Kosten**: $45-75/Monat

#### 3. Microsoft Azure
- **Virtual Machine**: B2s (2 vCPU, 4 GB RAM)
- **Azure Database**: PostgreSQL Basic
- **SendGrid**: E-Mail-Versand
- **Azure Monitor**: Überwachung
- **Geschätzte Kosten**: $55-85/Monat

#### 4. DigitalOcean (Kostengünstig)
- **Droplet**: 4 GB RAM, 2 vCPUs
- **Managed Database**: PostgreSQL Basic
- **Mailgun**: E-Mail-Versand
- **Monitoring**: Integriert
- **Geschätzte Kosten**: $35-60/Monat

## 🔧 Schritt-für-Schritt Deployment

### 1. Server-Setup

```bash
# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Python und Dependencies installieren
sudo apt install -y python3.11 python3.11-venv python3-pip nginx postgresql postgresql-contrib

# Benutzer erstellen
sudo adduser medtech-newsletter
sudo usermod -aG sudo medtech-newsletter
```

### 2. Anwendung installieren

```bash
# Als medtech-newsletter Benutzer
su - medtech-newsletter

# Repository klonen
git clone <repository-url> medtech-newsletter-ai
cd medtech-newsletter-ai

# Virtual Environment erstellen
python3.11 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# spaCy Modelle herunterladen
python -m spacy download de_core_news_sm
python -m spacy download en_core_web_sm
```

### 3. Datenbank konfigurieren

```bash
# PostgreSQL konfigurieren
sudo -u postgres psql

CREATE DATABASE medtech_newsletter;
CREATE USER medtech_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE medtech_newsletter TO medtech_user;
\q
```

### 4. Umgebungsvariablen konfigurieren

```bash
# .env Datei erstellen
cp .env.example .env

# Konfiguration anpassen
nano .env
```

**Produktions-.env Beispiel:**
```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-here
START_SCHEDULER=true

DATABASE_URL=postgresql://medtech_user:secure_password_here@localhost/medtech_newsletter

MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_DEFAULT_SENDER=newsletter@yourdomain.com

SCRAPING_INTERVAL_HOURS=6
NEWSLETTER_GENERATION_INTERVAL_HOURS=24

LOG_LEVEL=INFO
LOG_FILE=/var/log/medtech-newsletter/app.log

PORT=5000
```

### 5. Systemd Service erstellen

```bash
# Service-Datei erstellen
sudo nano /etc/systemd/system/medtech-newsletter.service
```

**Service-Konfiguration:**
```ini
[Unit]
Description=Medizintechnik Newsletter AI
After=network.target postgresql.service

[Service]
Type=simple
User=medtech-newsletter
Group=medtech-newsletter
WorkingDirectory=/home/medtech-newsletter/medtech-newsletter-ai
Environment=PATH=/home/medtech-newsletter/medtech-newsletter-ai/venv/bin
ExecStart=/home/medtech-newsletter/medtech-newsletter-ai/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Service aktivieren
sudo systemctl daemon-reload
sudo systemctl enable medtech-newsletter
sudo systemctl start medtech-newsletter
```

### 6. Nginx Reverse Proxy

```bash
# Nginx konfigurieren
sudo nano /etc/nginx/sites-available/medtech-newsletter
```

**Nginx-Konfiguration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/medtech-newsletter/medtech-newsletter-ai/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Site aktivieren
sudo ln -s /etc/nginx/sites-available/medtech-newsletter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL-Zertifikat (Let's Encrypt)

```bash
# Certbot installieren
sudo apt install certbot python3-certbot-nginx

# SSL-Zertifikat erstellen
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 🔒 Sicherheit

### Firewall konfigurieren

```bash
# UFW aktivieren
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw status
```

### Datenbank-Sicherheit

```bash
# PostgreSQL Zugriff beschränken
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Nur lokale Verbindungen erlauben
local   medtech_newsletter    medtech_user                     md5
```

### Backup-Strategie

```bash
# Automatisches Backup-Script
sudo nano /usr/local/bin/backup-medtech.sh
```

**Backup-Script:**
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/medtech-newsletter"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Datenbank-Backup
pg_dump -U medtech_user -h localhost medtech_newsletter > $BACKUP_DIR/db_$DATE.sql

# Anwendungs-Backup
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /home/medtech-newsletter/medtech-newsletter-ai

# Alte Backups löschen (älter als 30 Tage)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

```bash
# Backup-Script ausführbar machen
sudo chmod +x /usr/local/bin/backup-medtech.sh

# Cron-Job für tägliche Backups
sudo crontab -e
# Hinzufügen: 0 2 * * * /usr/local/bin/backup-medtech.sh
```

## 📊 Monitoring

### Log-Rotation

```bash
# Logrotate konfigurieren
sudo nano /etc/logrotate.d/medtech-newsletter
```

```
/var/log/medtech-newsletter/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 medtech-newsletter medtech-newsletter
    postrotate
        systemctl reload medtech-newsletter
    endscript
}
```

### Health-Checks

```bash
# Health-Check Script
nano /home/medtech-newsletter/health-check.sh
```

```bash
#!/bin/bash
HEALTH_URL="http://localhost:5000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "$(date): Service is healthy"
else
    echo "$(date): Service is unhealthy (HTTP $RESPONSE)"
    systemctl restart medtech-newsletter
fi
```

## 🔄 Updates und Wartung

### Update-Prozess

```bash
# 1. Backup erstellen
/usr/local/bin/backup-medtech.sh

# 2. Code aktualisieren
cd /home/medtech-newsletter/medtech-newsletter-ai
git pull origin main

# 3. Dependencies aktualisieren
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 4. Datenbank-Migrationen (falls erforderlich)
python -c "from app import create_app; from src.models import db; app = create_app(); app.app_context().push(); db.create_all()"

# 5. Service neu starten
sudo systemctl restart medtech-newsletter

# 6. Funktionalität testen
curl http://localhost:5000/health
```

## 📈 Skalierung

### Horizontale Skalierung

Für höhere Lasten können mehrere Instanzen mit Load Balancer eingesetzt werden:

1. **Load Balancer**: Nginx oder HAProxy
2. **Shared Database**: PostgreSQL Cluster
3. **Shared Storage**: NFS oder Object Storage
4. **Session Management**: Redis

### Vertikale Skalierung

Bei steigenden Anforderungen Server-Ressourcen erhöhen:

- **CPU**: 4-8 vCPUs
- **RAM**: 8-16 GB
- **Storage**: SSD mit höherer IOPS

## 🚨 Troubleshooting

### Häufige Probleme

#### Service startet nicht
```bash
# Logs prüfen
sudo journalctl -u medtech-newsletter -f

# Konfiguration testen
cd /home/medtech-newsletter/medtech-newsletter-ai
source venv/bin/activate
python app.py
```

#### Datenbank-Verbindungsfehler
```bash
# PostgreSQL Status prüfen
sudo systemctl status postgresql

# Verbindung testen
psql -U medtech_user -h localhost -d medtech_newsletter
```

#### E-Mail-Versand funktioniert nicht
```bash
# SMTP-Konfiguration testen
python -c "
from src.email_service import EmailService
from config.config import Config
service = EmailService(None, Config())
# Test-E-Mail senden
"
```

## 📞 Support

Bei Problemen:

1. **Logs prüfen**: `/var/log/medtech-newsletter/app.log`
2. **System-Status**: `sudo systemctl status medtech-newsletter`
3. **Health-Check**: `curl http://localhost:5000/health`
4. **Datenbank**: `psql -U medtech_user -d medtech_newsletter`

## 🎯 Nächste Schritte

Nach erfolgreichem Deployment:

1. **DNS konfigurieren**: Domain auf Server-IP zeigen lassen
2. **E-Mail-Authentifizierung**: SPF, DKIM, DMARC einrichten
3. **Monitoring einrichten**: Uptime-Monitoring, Alerting
4. **Performance optimieren**: Caching, CDN
5. **Backup testen**: Restore-Prozess validieren

