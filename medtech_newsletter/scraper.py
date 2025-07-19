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
]

class DocumentScraper:
    def __init__(self, sources):
        self.sources = sources
        self.session = requests.Session()
        self.scraper_api_key = os.environ.get('SCRAPER_API_KEY')
        if not self.scraper_api_key:
            logger.warning("SCRAPER_API_KEY nicht gefunden. Scraping wird fehlschlagen.")

    def scrape_all_sources(self):
        logger.info("Starte gezieltes Scraping zur Fehleranalyse...")
        all_documents = []
        
        # WIR TESTEN JETZT NUR EINE QUELLE
        source_to_test = 'G-BA'
        
        logger.info(f"Fokussiere auf Test-Quelle: {source_to_test}")
        config = self.sources.get(source_to_test)
        
        if config:
            docs = self.scrape_source(source_to_test, config)
            all_documents.extend(docs)
        else:
            logger.error(f"Test-Quelle '{source_to_test}' nicht in der Konfiguration gefunden.")
            
        logger.info(f"Scraping abgeschlossen. {len(all_documents)} Dokumente von {source_to_test} gefunden.")
        return all_documents

    def scrape_source(self, name, config):
        logger.info(f"Starte Scraping für: {name}...")
        base_url = config['base_url']
        all_docs = []
        for path in config['search_paths']:
            all_docs.extend(self._scrape_generic_page(base_url, path))
            time.sleep(random.uniform(2, 5))
        logger.info(f"{name} Scraping abgeschlossen. {len(all_docs)} Dokumente gefunden.")
        return all_docs

    def _scrape_generic_page(self, base_url, path):
        target_url = urljoin(base_url, path)
        
        if not self.scraper_api_key:
            logger.error("Scraping ohne API Key nicht möglich.")
            return []

        proxy_url = f"http://api.scraperapi.com/?api_key={self.scraper_api_key}&url={target_url}&render=true&premium=true"
        documents = []
        
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            logger.info(f"Scraping URL: {target_url} via Premium Proxy")
            response = self.session.get(proxy_url, headers=headers, timeout=180)
            
            if response.status_code != 200:
                logger.error(f"Fehlerhafte Antwort für {target_url}. Status: {response.status_code}")
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
