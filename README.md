# News-Aggregator

Dies ist ein universeller News-Aggregator, der Inhalte aus RSS-Feeds, JSON-APIs und HTML-Scraping sammelt
und als sofortigen oder wöchentlichen Newsletter versendet.

## Features

- Anbindung beliebiger Quellen via Plugin-Schnittstelle  
- RSS-Feeds, REST-APIs und HTML-Scraping  
- Asynchrones Fetching mit aiohttp  
- Speicherung in SQLite (später PostgreSQL möglich)  
- Template-Rendering mit Jinja2  
- Versand via Gmail SMTP (später SendGrid, Mailgun etc.)  
- Scheduler für Echtzeit-Alerts und wöchentliche Zusammenfassungen  

## Projektstruktur

