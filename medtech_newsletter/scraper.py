import requests
from bs4 import BeautifulSoup
from loguru import logger
from urllib.parse import urljoin

class DocumentScraper:
    def __init__(self, sources):
        self.sources = sources
        self.session = requests.Session()
        # WICHTIG: Tarnung als echter Browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_all_sources(self):
        logger.info("Starte Scraping aller Quellen...")
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
        full_url = urljoin(base_url, path)
        documents = []
        try:
            logger.info(f"Scraping URL: {full_url}")
            response = self.session.get(full_url, timeout=30)
            response.raise_for_status()  # Löst einen Fehler bei 4xx/5xx Antworten aus
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Finde alle Links (<a> tags mit href Attribut)
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                # Filtere uninteressante Links heraus
                if href.startswith('#') or href.startswith('mailto:') or href.startswith('javascript:'):
                    continue

                doc_url = urljoin(full_url, href)
                doc_title = link.get_text(strip=True)
                
                if doc_title: # Nur Links mit Titel hinzufügen
                    documents.append({
                        'source': base_url,
                        'url': doc_url,
                        'title': doc_title
                    })

        except requests.exceptions.RequestException as e:
            logger.error(f"Fehler beim Scraping von {full_url}: {e}")
        
        return documents

    def scrape_fda(self, config):
        logger.info("Starte FDA Scraping...")
        base_url = config['base_url']
        all_docs = []
        for path in config['search_paths']:
            all_docs.extend(self._scrape_generic_page(base_url, path))
        logger.info(f"FDA Scraping abgeschlossen. {len(all_docs)} Dokumente gefunden.")
        return all_docs

    def scrape_bfarm(self, config):
        logger.info("Starte BfArM Scraping...")
        base_url = config['base_url']
        all_docs = []
        for path in config['search_paths']:
            all_docs.extend(self._scrape_generic_page(base_url, path))
        logger.info(f"BfArM Scraping abgeschlossen. {len(all_docs)} Dokumente gefunden.")
        return all_docs

    def scrape_iso(self, config):
        logger.info("Starte ISO Scraping...")
        base_url = config['base_url']
        all_docs = []
        for path in config['search_paths']:
            all_docs.extend(self._scrape_generic_page(base_url, path))
        logger.info(f"ISO Scraping abgeschlossen. {len(all_docs)} Dokumente gefunden.")
        return all_docs

    def scrape_tuv(self, config):
        logger.info("Starte TUV Scraping...")
        base_url = config['base_url']
        all_docs = []
        for path in config['search_paths']:
            all_docs.extend(self._scrape_generic_page(base_url, path))
        logger.info(f"TUV Scraping abgeschlossen. {len(all_docs)} Dokumente gefunden.")
        return all_docs
