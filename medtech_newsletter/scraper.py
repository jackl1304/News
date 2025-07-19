import requests
from bs4 import BeautifulSoup
from loguru import logger
from urllib.parse import urljoin
import os

class DocumentScraper:
    def __init__(self, sources):
        self.sources = sources
        self.session = requests.Session()
        
        # Bessere Tarnung: Simuliert einen echten Browser-Request
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
        })
        
        self.scraper_api_key = os.environ.get('SCRAPER_API_KEY')
        if not self.scraper_api_key:
            logger.warning("SCRAPER_API_KEY nicht gefunden. Scraping wird fehlschlagen.")

    def scrape_all_sources(self):
        logger.info("Starte Scraping aller Quellen über Proxy mit JS-Rendering...")
        all_documents = []
        for source_name, config in self.sources.items():
            docs = self.scrape_source(source_name, config)
            all_documents.extend(docs)
        logger.info(f"Scraping abgeschlossen. {len(all_documents)} Dokumente gefunden.")
        return all_documents

    def scrape_source(self, name, config):
        logger.info(f"Starte Scraping für: {name}...")
        base_url = config['base_url']
        all_docs = []
        for path in config['search_paths']:
            all_docs.extend(self._scrape_generic_page(base_url, path))
        logger.info(f"{name} Scraping abgeschlossen. {len(all_docs)} Dokumente gefunden.")
        return all_docs

    def _scrape_generic_page(self, base_url, path):
        target_url = urljoin(base_url, path)
        
        if not self.scraper_api_key:
            logger.error("Scraping ohne API Key nicht möglich.")
            return []

        # Wir nutzen den Proxy-Dienst mit aktiviertem JavaScript-Rendering
        proxy_url = f"http://api.scraperapi.com/?api_key={self.scraper_api_key}&url={target_url}&render=true"
        documents = []
        
        try:
            logger.info(f"Scraping URL: {target_url} via Proxy")
            response = self.session.get(proxy_url, timeout=180)
            
            # **NEU: Intelligente Fehleranalyse**
            if response.status_code != 200:
                logger.error(f"Fehler von ScraperAPI für {target_url}. Status: {response.status_code}")
                # Wir loggen den Anfang der Antwort, um zu sehen, was schiefgeht
                logger.error(f"Antwort-Anfang: {response.text[:1000]}") 
                response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)
            
            if not links:
                logger.warning(f"Keine Links auf der Seite gefunden: {target_url}")
                # Wir loggen auch hier die Antwort, um zu sehen, warum keine Links da sind
                logger.warning(f"Seiteninhalt-Anfang: {response.text[:1000]}")

            for link in links:
                href = link['href']
                # Verfeinerter Filter für Links
                if href.startswith(('#', 'mailto:', 'javascript:')) or not link.get_text(strip=True):
                    continue

                doc_url = urljoin(target_url, href)
                doc_title = link.get_text(strip=True)
                
                documents.append({'source': base_url, 'url': doc_url, 'title': doc_title})

        except requests.exceptions.RequestException as e:
            logger.error(f"Netzwerkfehler beim Scraping von {target_url}: {e}")
        
        return documents
