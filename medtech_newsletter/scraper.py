import requests
from bs4 import BeautifulSoup
from loguru import logger
from urllib.parse import urljoin
import os

class DocumentScraper:
    def __init__(self, sources):
        self.sources = sources
        self.session = requests.Session()
        
        self.scraper_api_key = os.environ.get('SCRAPER_API_KEY')
        if not self.scraper_api_key:
            logger.warning("SCRAPER_API_KEY nicht gefunden. Scraping könnte fehlschlagen.")

    def scrape_all_sources(self):
        logger.info("Starte Scraping aller Quellen über Proxy mit JS-Rendering...")
        all_documents = []
        for source_name, config in self.sources.items():
            scraper_func = getattr(self, f"scrape_{source_name.lower()}", None)
            if scraper_func:
                docs = scraper_func(config)
                all_documents.extend(docs)
        logger.info(f"Scraping abgeschlossen. {len(all_documents)} Dokumente gefunden.")
        return all_documents

    def _scrape_generic_page(self, base_url, path):
        """Eine generische Funktion zum Scrapen einer Seite und Finden von Links."""
        target_url = urljoin(base_url, path)
        
        if not self.scraper_api_key:
            logger.error("Scraping ohne API Key nicht möglich.")
            return []

        # HIER IST DIE ÄNDERUNG: Wir fügen &render=true hinzu, um JavaScript zu aktivieren
        proxy_url = f"http://api.scraperapi.com/?api_key={self.scraper_api_key}&url={target_url}&render=true"

        documents = []
        try:
            logger.info(f"Scraping URL: {target_url} via Proxy")
            response = self.session.get(proxy_url, timeout=180) # Längeres Timeout für JS-Rendering
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                if href.startswith('#') or href.startswith('mailto:') or href.startswith('javascript:'):
                    continue

                doc_url = urljoin(target_url, href)
                doc_title = link.get_text(strip=True)
                
                if doc_title:
                    documents.append({
                        'source': base_url,
                        'url': doc_url,
                        'title': doc_title
                    })

        except requests.exceptions.RequestException as e:
            logger.error(f"Fehler beim Scraping von {target_url}: {e}")
        
        return documents

    # Die folgenden Funktionen bleiben gleich
    def scrape_destatis(self, config):
        logger.info("Starte Destatis Scraping...")
        base_url = config['base_url']
        all_docs = []
        for path in config['search_paths']:
            all_docs.extend(self._scrape_generic_page(base_url, path))
        logger.info(f"Destatis Scraping abgeschlossen. {len(all_docs)} Dokumente gefunden.")
        return all_docs
    
    def scrape_bfarm(self, config):
        logger.info("Starte BfArM Scraping...")
        base_url = config['base_url']
        all_docs = []
        for path in config['search_paths']:
            all_docs.extend(self._scrape_generic_page(base_url, path))
        logger.info(f"BfArM Scraping abgeschlossen. {len(all_docs)} Dokumente gefunden.")
        return all_docs

    def scrape_eurostat(self, config):
        logger.info("Starte Eurostat Scraping...")
        base_url = config['base_url']
        all_docs = []
        for path in config['search_paths']:
            all_docs.extend(self._scrape_generic_page(base_url, path))
        logger.info(f"Eurostat Scraping abgeschlossen. {len(all_docs)} Dokumente gefunden.")
        return all_docs
        
    def scrape_ezb(self, config):
        logger.info("Starte EZB Scraping...")
        base_url = config['base_url']
        all_docs = []
        for path in config['search_paths']:
            all_docs.extend(self._scrape_generic_page(base_url, path))
        logger.info(f"EZB Scraping abgeschlossen. {len(all_docs)} Dokumente gefunden.")
        return all_docs

    def scrape_fda(self, config):
        logger.info("Starte FDA Scraping...")
        base_url = config['base_url']
        all_docs = []
        for path in config['search_paths']:
            all_docs.extend(self._scrape_generic_page(base_url, path))
        logger.info(f"FDA Scraping abgeschlossen. {len(all_docs)} Dokumente gefunden.")
        return all_docs

    def scrape_weltbank(self, config):
        logger.info("Starte Weltbank Scraping...")
        base_url = config['base_url']
        all_docs = []
        for path in config['search_paths']:
            all_docs.extend(self._scrape_generic_page(base_url, path))
        logger.info(f"Weltbank Scraping abgeschlossen. {len(all_docs)} Dokumente gefunden.")
        return all_docs
