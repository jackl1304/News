"""Modul zur Analyse und Verarbeitung von Dokumenten."""
import difflib
from typing import Dict, List
import re

import spacy
import nltk
from loguru import logger
from textdistance import jaccard

# NLTK Downloads (falls noch nicht vorhanden)
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

class DocumentAnalyzer:
    """Klasse für die Analyse und Verarbeitung von Dokumenten"""
    
    def __init__(self):
        self.nlp = None
        self._load_nlp_model()
        
        # Medizintechnik-spezifische Keywords
        self.medical_keywords = {
            \"regulations\": [\"regulation\", \"directive\", \"law\", \"act\", \"verordnung\", \"richtlinie\", \"gesetz\"],
            \"standards\": [\"standard\", \"norm\", \"iso\", \"iec\", \"din\", \"astm\"],
            \"devices\": [\"medical device\", \"medizinprodukt\", \"implant\", \"diagnostic\", \"therapeutic\"],
            \"quality\": [\"quality\", \"safety\", \"risk\", \"qualität\", \"sicherheit\", \"risiko\"],
            \"approval\": [\"approval\", \"certification\", \"clearance\", \"zulassung\", \"zertifizierung\"],
            \"clinical\": [\"clinical trial\", \"study\", \"evaluation\", \"klinische studie\", \"bewertung\"]
        }
        
        # Wichtigkeits-Scores für verschiedene Änderungstypen
        self.importance_weights = {
            \"new_regulation\": 10,
            \"regulation_update\": 8,
            \"new_standard\": 7,
            \"standard_update\": 6,
            \"deadline_change\": 9,
            \"requirement_change\": 8,
            \"general_update\": 5
        }
    
    def _load_nlp_model(self):
        """Lädt das spaCy NLP-Modell"""
        try:
            # Versuche deutsches Modell zu laden
            self.nlp = spacy.load("de_core_news_sm")
            logger.info("Deutsches spaCy-Modell geladen")
        except OSError:
            try:
                # Fallback auf englisches Modell
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("Englisches spaCy-Modell geladen")
            except OSError:
                logger.warning("Kein spaCy-Modell gefunden. Verwende einfache Textverarbeitung.")
                self.nlp = None
    
    def extract_key_information(self, content: str) -> Dict:
        """Extrahiert Schlüsselinformationen aus dem Dokumentinhalt"""
        info = {
            \"summary\": \"\\
