import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import hashlib
import time
import re
from datetime import datetime
from loguru import logger
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import json

class DocumentScraper:
    """Klasse für das Scraping von Dokumenten von verschiedenen Quellen"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def _get_selenium_driver(self) -> webdriver.Chrome:
        """Erstellt einen Selenium WebDriver für dynamische Inhalte"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des WebDrivers: {e}")
            raise
    
    def _calculate_content_hash(self, content: str) -> str:
        """Berechnet SHA-256 Hash des Inhalts"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _clean_text(self, text: str) -> str:
        """Bereinigt Text von überflüssigen Whitespaces und Zeichen"""
        if not text:
            return ""
        
        # Entferne mehrfache Leerzeichen und Zeilenumbrüche
        text = re.sub(r'\s+', ' ', text)
        # Entferne führende und nachfolgende Leerzeichen
        text = text.strip()
        return text
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extrahiert Metadaten aus dem HTML-Dokument"""
        metadata = {
            'url': url,
            'scraped_at': datetime.utcnow().isoformat()
        }
        
        # Versuche Datum zu extrahieren
        date_patterns = [
            r'(\d{1,2}[./]\d{1,2}[./]\d{4})',
            r'(\d{4}[./]\d{1,2}[./]\d{1,2})',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            r'(\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})'
        ]
        
        page_text = soup.get_text()
        for pattern in date_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                metadata['potential_dates'] = matches[:5]  # Erste 5 gefundene Daten
                break
        
        # Meta-Tags extrahieren
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            if tag.get('name') == 'description':
                metadata['description'] = tag.get('content', '')
            elif tag.get('name') == 'keywords':
                metadata['keywords'] = tag.get('content', '')
            elif tag.get('property') == 'og:title':
                metadata['og_title'] = tag.get('content', '')
        
        return metadata
    
    def scrape_fda(self) -> List[Dict]:
        """Scrapt FDA-Dokumente"""
        logger.info("Starte FDA Scraping...")
        documents = []
        
        base_url = self.config['SOURCES']['FDA']['base_url']
        search_paths = self.config['SOURCES']['FDA']['search_paths']
        
        for path in search_paths:
            try:
                url = urljoin(base_url, path)
                logger.info(f"Scraping FDA URL: {url}")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Suche nach Links zu Dokumenten
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href')
                    text = self._clean_text(link.get_text())
                    
                    # Filter für relevante Dokumente
                    if any(keyword in text.lower() for keyword in ['guidance', 'regulation', 'standard', 'requirement', 'device']):
                        full_url = urljoin(url, href)
                        
                        # Vermeide Duplikate
                        if not any(doc['url'] == full_url for doc in documents):
                            doc_content = self._scrape_document_content(full_url)
                            if doc_content:
                                documents.append({
                                    'source': 'FDA',
                                    'title': text,
                                    'url': full_url,
                                    'content': doc_content['content'],
                                    'content_hash': self._calculate_content_hash(doc_content['content']),
                                    'metadata': doc_content['metadata']
                                })
                
                time.sleep(2)  # Höfliche Pause zwischen Requests
                
            except Exception as e:
                logger.error(f"Fehler beim Scraping von FDA {path}: {e}")
                continue
        
        logger.info(f"FDA Scraping abgeschlossen. {len(documents)} Dokumente gefunden.")
        return documents
    
    def scrape_bfarm(self) -> List[Dict]:
        """Scrapt BfArM-Dokumente"""
        logger.info("Starte BfArM Scraping...")
        documents = []
        
        base_url = self.config['SOURCES']['BfArM']['base_url']
        search_paths = self.config['SOURCES']['BfArM']['search_paths']
        
        for path in search_paths:
            try:
                url = urljoin(base_url, path)
                logger.info(f"Scraping BfArM URL: {url}")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Suche nach Links zu Dokumenten
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href')
                    text = self._clean_text(link.get_text())
                    
                    # Filter für relevante Dokumente
                    if any(keyword in text.lower() for keyword in ['richtlinie', 'verordnung', 'leitfaden', 'norm', 'medizinprodukt']):
                        full_url = urljoin(url, href)
                        
                        # Vermeide Duplikate
                        if not any(doc['url'] == full_url for doc in documents):
                            doc_content = self._scrape_document_content(full_url)
                            if doc_content:
                                documents.append({
                                    'source': 'BfArM',
                                    'title': text,
                                    'url': full_url,
                                    'content': doc_content['content'],
                                    'content_hash': self._calculate_content_hash(doc_content['content']),
                                    'metadata': doc_content['metadata']
                                })
                
                time.sleep(2)  # Höfliche Pause zwischen Requests
                
            except Exception as e:
                logger.error(f"Fehler beim Scraping von BfArM {path}: {e}")
                continue
        
        logger.info(f"BfArM Scraping abgeschlossen. {len(documents)} Dokumente gefunden.")
        return documents
    
    def scrape_iso(self) -> List[Dict]:
        """Scrapt ISO-Dokumente"""
        logger.info("Starte ISO Scraping...")
        documents = []
        
        base_url = self.config['SOURCES']['ISO']['base_url']
        search_paths = self.config['SOURCES']['ISO']['search_paths']
        
        for path in search_paths:
            try:
                url = urljoin(base_url, path)
                logger.info(f"Scraping ISO URL: {url}")
                
                # ISO-Seiten sind oft dynamisch, verwende Selenium
                driver = self._get_selenium_driver()
                
                try:
                    driver.get(url)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Warte auf dynamische Inhalte
                    time.sleep(3)
                    
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # Suche nach Links zu Standards
                    links = soup.find_all('a', href=True)
                    
                    for link in links:
                        href = link.get('href')
                        text = self._clean_text(link.get_text())
                        
                        # Filter für relevante Dokumente
                        if any(keyword in text.lower() for keyword in ['iso', 'standard', 'medical', 'device', 'quality']):
                            full_url = urljoin(url, href)
                            
                            # Vermeide Duplikate
                            if not any(doc['url'] == full_url for doc in documents):
                                doc_content = self._scrape_document_content(full_url)
                                if doc_content:
                                    documents.append({
                                        'source': 'ISO',
                                        'title': text,
                                        'url': full_url,
                                        'content': doc_content['content'],
                                        'content_hash': self._calculate_content_hash(doc_content['content']),
                                        'metadata': doc_content['metadata']
                                    })
                    
                finally:
                    driver.quit()
                
                time.sleep(2)  # Höfliche Pause zwischen Requests
                
            except Exception as e:
                logger.error(f"Fehler beim Scraping von ISO {path}: {e}")
                continue
        
        logger.info(f"ISO Scraping abgeschlossen. {len(documents)} Dokumente gefunden.")
        return documents
    
    def scrape_tuv(self) -> List[Dict]:
        """Scrapt TÜV-Dokumente"""
        logger.info("Starte TÜV Scraping...")
        documents = []
        
        base_url = self.config['SOURCES']['TUV']['base_url']
        search_paths = self.config['SOURCES']['TUV']['search_paths']
        
        for path in search_paths:
            try:
                url = urljoin(base_url, path)
                logger.info(f"Scraping TÜV URL: {url}")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Suche nach Links zu Dokumenten
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href')
                    text = self._clean_text(link.get_text())
                    
                    # Filter für relevante Dokumente
                    if any(keyword in text.lower() for keyword in ['medical', 'device', 'testing', 'certification', 'standard']):
                        full_url = urljoin(url, href)
                        
                        # Vermeide Duplikate
                        if not any(doc['url'] == full_url for doc in documents):
                            doc_content = self._scrape_document_content(full_url)
                            if doc_content:
                                documents.append({
                                    'source': 'TUV',
                                    'title': text,
                                    'url': full_url,
                                    'content': doc_content['content'],
                                    'content_hash': self._calculate_content_hash(doc_content['content']),
                                    'metadata': doc_content['metadata']
                                })
                
                time.sleep(2)  # Höfliche Pause zwischen Requests
                
            except Exception as e:
                logger.error(f"Fehler beim Scraping von TÜV {path}: {e}")
                continue
        
        logger.info(f"TÜV Scraping abgeschlossen. {len(documents)} Dokumente gefunden.")
        return documents
    
    def _scrape_document_content(self, url: str) -> Optional[Dict]:
        """Scrapt den Inhalt eines einzelnen Dokuments"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Entferne Skripte und Styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extrahiere Text
            content = self._clean_text(soup.get_text())
            
            # Extrahiere Metadaten
            metadata = self._extract_metadata(soup, url)
            
            if len(content) < 100:  # Zu kurzer Inhalt, wahrscheinlich nicht relevant
                return None
            
            return {
                'content': content,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.warning(f"Fehler beim Scraping von {url}: {e}")
            return None
    
    def scrape_all_sources(self) -> List[Dict]:
        """Scrapt alle konfigurierten Quellen"""
        logger.info("Starte Scraping aller Quellen...")
        
        all_documents = []
        
        # Scrape jede Quelle
        scrapers = [
            self.scrape_fda,
            self.scrape_bfarm,
            self.scrape_iso,
            self.scrape_tuv
        ]
        
        for scraper in scrapers:
            try:
                documents = scraper()
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"Fehler beim Scraping mit {scraper.__name__}: {e}")
                continue
        
        logger.info(f"Scraping aller Quellen abgeschlossen. Insgesamt {len(all_documents)} Dokumente gefunden.")
        return all_documents

