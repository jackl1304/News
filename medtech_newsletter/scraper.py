import requests
from bs4 import BeautifulSoup
from loguru import logger
from urllib.parse import urljoin
import os
import time
import random

# Eine Liste von echten Browser User-Agents zur zufälligen Auswahl
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15',
]

class DocumentScraper:
    def __init__(self, sources):
        self.sources = sources
        self.session = requests.Session()
        self.scraper_api_key = os.environ.get('SCRAPER_API_KEY')
        if not self.scraper_api_key:
            logger.warning("SCRAPER_API_KEY nicht gefunden. Scraping wird fehlschlagen.")

    def scrape_all_sources(self):
        logger.info("Starte unauffälliges Scraping aller Quellen...")
        all_documents = []
        for source_name, config in self.sources.items():
            docs = self.scrape_source(source_name, config)
            all_documents.extend(docs)
            # Menschliches Timing: Eine längere Pause zwischen den verschiedenen Webseiten
            time.sleep(random.uniform(5, 10))
        logger.info(f"Scraping abgeschlossen. {len(all_documents)} Dokumente gefunden.")
        return all_documents

    def scrape_source(self, name, config):
        logger.info(f"Starte Scraping für: {name}...")
        base_url = config['base_url']
        all_docs = []
        for path in config['search_paths']:
            all_docs.extend(self._scrape_generic_page(base_url, path))
            # Menschliches Timing: Eine kurze Pause zwischen Unterseiten derselben Webseite
            time.sleep(random.uniform(2, 5))
        logger.info(f"{name} Scraping abgeschlossen. {len(all_docs)} Dokumente gefunden.")
        return all_docs

    def _scrape_generic_page(self, base_url, path):
        target_url = urljoin(base_url, path)
        
        if not self.scraper_api_key:
            logger.error("Scraping ohne API Key nicht möglich.")
            return []

        # Premium-Proxy und JS-Rendering aktivieren
        proxy_url = f"http://api.scraperapi.com/?api_key={self.scraper_api_key}&url={target_url}&render=true&premium=true"
        documents = []
        
        try:
            # Rotiere die Browser-Header für jede Anfrage
            headers = {
                'User-Agent': random.choice(USER_AGENTS)
            }
            logger.info(f"Scraping URL: {target_url} via Premium Proxy")
            response = self.session.get(proxy_url, headers=headers, timeout=180)
            
            if response.status_code != 200:
                logger.error(f"Fehler von ScraperAPI für {target_url}. Status: {response.status_code}")
                logger.error(f"Antwort-Anfang: {response.text[:1000]}") 
                response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)
            
            if not links:
                logger.warning(f"Keine Links auf der Seite gefunden: {target_url}")
                logger.warning(f"Seiteninhalt-Anfang: {response.text[:1000]}")

            for link in links:
                href = link['href']
                if href.startswith(('#', 'mailto:', 'javascript:')) or not link.get_text(strip=True):
                    continue

                doc_url = urljoin(target_url, href)
                doc_title = link.get_text(strip=True)
                
                documents.append({'source': base_url, 'url': doc_url, 'title': doc_title})

        except requests.exceptions.RequestException as e:
            logger.error(f"Netzwerkfehler beim Scraping von {target_url}: {e}")
        
        return documents
