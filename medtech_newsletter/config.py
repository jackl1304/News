import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Basis-Konfiguration für die Anwendung"""
    
    # Flask Konfiguration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Datenbank Konfiguration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///medtech_newsletter.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # E-Mail Konfiguration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Scraping Konfiguration
    SCRAPING_INTERVAL_HOURS = int(os.environ.get('SCRAPING_INTERVAL_HOURS') or 24)
    NEWSLETTER_GENERATION_INTERVAL_HOURS = int(os.environ.get('NEWSLETTER_GENERATION_INTERVAL_HOURS') or 168)  # Wöchentlich
    
    # Quellen Konfiguration
    SOURCES = {
        'DESTATIS': {
            'base_url': 'https://www.destatis.de',
            'search_paths': [
                '/DE/Presse/_inhalt.html'
            ]
        },
        'BfArM': {
            'base_url': 'https://www.bfarm.de',
            'search_paths': [
                '/DE/Medizinprodukte/_node.html'
            ]
        },
        'EUROSTAT': {
            'base_url': 'https://ec.europa.eu/eurostat',
            'search_paths': [
                '/web/main/news/whats-new'
            ]
        },
        'EZB': {
            'base_url': 'https://www.ecb.europa.eu',
            'search_paths': [
                '/press/press_releases/html/index.de.html'
            ]
        },
        'FDA': {
            'base_url': 'https://www.fda.gov',
            'search_paths': [
                '/medical-devices/news-events-medical-devices'
            ]
        },
        'WELTBANK': {
            'base_url': 'https://www.worldbank.org',
            'search_paths': [
                '/en/news/press-release'
            ]
        }
    }
    
    # Logging Konfiguration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'medtech_newsletter.log'

class DevelopmentConfig(Config):
    """Entwicklungs-Konfiguration"""
    DEBUG = True

class ProductionConfig(Config):
    """Produktions-Konfiguration"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
