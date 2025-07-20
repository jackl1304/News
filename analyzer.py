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
            'regulations': ['regulation', 'directive', 'law', 'act', 'verordnung', 'richtlinie', 'gesetz'],
            'standards': ['standard', 'norm', 'iso', 'iec', 'din', 'astm'],
            'devices': ['medical device', 'medizinprodukt', 'implant', 'diagnostic', 'therapeutic'],
            'quality': ['quality', 'safety', 'risk', 'qualität', 'sicherheit', 'risiko'],
            'approval': ['approval', 'certification', 'clearance', 'zulassung', 'zertifizierung'],
            'clinical': ['clinical trial', 'study', 'evaluation', 'klinische studie', 'bewertung']
        }
        
        # Wichtigkeits-Scores für verschiedene Änderungstypen
        self.importance_weights = {
            'new_regulation': 10,
            'regulation_update': 8,
            'new_standard': 7,
            'standard_update': 6,
            'deadline_change': 9,
            'requirement_change': 8,
            'general_update': 5
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
            'summary': '',
            'key_topics': [],
            'dates': [],
            'regulations': [],
            'standards': [],
            'importance_score': 0,
            'change_indicators': []
        }
        
        if not content:
            return info
        
        # Text in Sätze aufteilen
        sentences = self._split_into_sentences(content)
        
        # Wichtige Sätze identifizieren
        important_sentences = self._identify_important_sentences(sentences)
        info['summary'] = ' '.join(important_sentences[:3])  # Top 3 Sätze als Zusammenfassung
        
        # Schlüsselthemen extrahieren
        info['key_topics'] = self._extract_topics(content)
        
        # Daten extrahieren
        info['dates'] = self._extract_dates(content)
        
        # Regulierungen und Standards identifizieren
        info['regulations'] = self._extract_regulations(content)
        info['standards'] = self._extract_standards(content)
        
        # Wichtigkeitsscore berechnen
        info['importance_score'] = self._calculate_importance_score(content, info)
        
        # Änderungsindikatoren suchen
        info['change_indicators'] = self._find_change_indicators(content)
        
        return info
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Teilt Text in Sätze auf"""
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
        
        # Fallback: einfache Satzaufteilung
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _identify_important_sentences(self, sentences: List[str]) -> List[str]:
        """Identifiziert wichtige Sätze basierend auf Keywords"""
        scored_sentences = []
        
        for sentence in sentences:
            score = 0
            sentence_lower = sentence.lower()
            
            # Score basierend auf medizinischen Keywords
            for _, keywords in self.medical_keywords.items(): # 'category' ist ungenutzt
                for keyword in keywords:
                    if keyword in sentence_lower:
                        score += 1
            
            # Zusätzliche Punkte für Änderungsindikatoren
            change_words = ['new', 'updated', 'revised', 'amended', 'changed', 'modified', 
                           'neu', 'aktualisiert', 'überarbeitet', 'geändert', 'modifiziert']
            for word in change_words:
                if word in sentence_lower:
                    score += 2
            
            if score > 0:
                scored_sentences.append((sentence, score))
        
        # Sortiere nach Score und gib die besten zurück
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [sent[0] for sent in scored_sentences]
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extrahiert Hauptthemen aus dem Inhalt"""
        topics = []
        content_lower = content.lower()
        
        # Suche nach spezifischen Themen
        topic_patterns = {
            'Medical Device Regulation': ['mdr', 'medical device regulation', 'medizinprodukteverordnung'],
            'In Vitro Diagnostic': ['ivd', 'in vitro diagnostic', 'in-vitro-diagnostika'],
            'Quality Management': ['quality management', 'qualitätsmanagement', 'iso 13485'],
            'Risk Management': ['risk management', 'risikomanagement', 'iso 14971'],
            'Clinical Evaluation': ['clinical evaluation', 'klinische bewertung'],
            'Post Market Surveillance': ['post market surveillance', 'marktüberwachung'],
            'Biocompatibility': ['biocompatibility', 'biokompatibilität', 'iso 10993'],
            'Software': ['software', 'iec 62304'],
            'Sterilization': ['sterilization', 'sterilisation', 'iso 11135']
        }
        
        for topic, patterns in topic_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    topics.append(topic)
                    break
        
        return list(set(topics))  # Entferne Duplikate
    
    def _extract_dates(self, content: str) -> List[str]:
        """Extrahiert Daten aus dem Inhalt"""
        date_patterns = [
            r'\b\d{1,2}[./]\d{1,2}[./]\d{4}\b',
            r'\b\d{4}[./]\d{1,2}[./]\d{1,2}\b',
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
            r'\b(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dates.extend(matches)
        
        return list(set(dates))  # Entferne Duplikate
    
    def _extract_regulations(self, content: str) -> List[str]:
        """Extrahiert Regulierungen aus dem Inhalt"""
        regulation_patterns = [
            r'\b(EU|EC)\s+\d+/\d+\b',  # EU Regulierungen
            r'\bMDR\b',  # Medical Device Regulation
            r'\bIVDR\b',  # In Vitro Diagnostic Regulation
            r'\bFDA\s+\w+\b',  # FDA Regulierungen
            r'\b21\s+CFR\s+\d+\b',  # FDA Code of Federal Regulations
            r'\bMedizinproduktegesetz\b',
            r'\bMPG\b'
        ]
        
        regulations = []
        for pattern in regulation_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            regulations.extend(matches)
        
        return list(set(regulations))
    
    def _extract_standards(self, content: str) -> List[str]:
        """Extrahiert Standards aus dem Inhalt"""
        standard_patterns = [
            r'\bISO\s+\d+(-\d+)?\b',
            r'\bIEC\s+\d+(-\d+)?\b',
            r'\bDIN\s+EN\s+\d+\b',
            r'\bASTM\s+\w+\d+\b'
        ]
        
        standards = []
        for pattern in standard_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            standards.extend(matches)
        
        return list(set(standards))
    
    def _calculate_importance_score(self, content: str, info: Dict) -> int:
        """Berechnet einen Wichtigkeitsscore für das Dokument"""
        score = 0
        content_lower = content.lower()
        
        # Basis-Score basierend auf Schlüsselwörtern
        for _, keywords in self.medical_keywords.items(): # 'category' ist ungenutzt
            for keyword in keywords:
                score += content_lower.count(keyword)
        
        # Zusätzliche Punkte für spezifische Indikatoren
        high_importance_words = ['mandatory', 'required', 'deadline', 'compliance', 
                               'pflicht', 'erforderlich', 'frist', 'konformität']
        for word in high_importance_words:
            score += content_lower.count(word) * 2
        
        # Punkte für gefundene Regulierungen und Standards
        score += len(info.get('regulations', [])) * 3
        score += len(info.get('standards', [])) * 2
        
        # Punkte für Änderungsindikatoren
        score += len(info.get('change_indicators', [])) * 2
        
        return min(score, 100)  # Maximal 100 Punkte
    
    def _find_change_indicators(self, content: str) -> List[str]:
        """Findet Indikatoren für Änderungen im Inhalt"""
        change_patterns = [
            r'(new|updated|revised|amended|changed|modified|introduced)\s+\w+',
            r'(neu|aktualisiert|überarbeitet|geändert|modifiziert|eingeführt)\s+\w+',
            r'effective\s+(date|from)',
            r'(gültig|wirksam)\s+(ab|vom)',
            r'deadline\s+\w+',
            r'(frist|termin)\s+\w+'
        ]
        
        indicators = []
        for pattern in change_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            indicators.extend([match if isinstance(match, str) else ' '.join(match) for match in matches])
        
        return list(set(indicators))
    
    def compare_documents(self, old_content: str, new_content: str) -> Dict:
        """Vergleicht zwei Dokumentversionen und identifiziert Änderungen"""
        if not old_content:
            return {
                'similarity_score': 0.0,
                'change_type': 'new',
                'diff_summary': 'Neues Dokument',
                'detailed_changes': [],
                'importance_score': 0
            }
        if not new_content:
            return {
                'similarity_score': 0.0,
                'change_type': 'deleted',
                'diff_summary': 'Dokument gelöscht',
                'detailed_changes': [],
                'importance_score': 0
            }
        
        # Ähnlichkeitsscore berechnen
        similarity_score = self._calculate_similarity(old_content, new_content)
        
        # Änderungstyp bestimmen
        change_type = self._determine_change_type(similarity_score)
        
        # Detaillierte Unterschiede finden
        detailed_changes = self._find_detailed_changes(old_content, new_content)
        
        # Zusammenfassung der Änderungen
        diff_summary = self._create_diff_summary(detailed_changes)
        
        # Wichtigkeitsscore für die Änderungen
        importance_score = self._calculate_change_importance(detailed_changes)
        
        return {
            'similarity_score': similarity_score,
            'change_type': change_type,
            'diff_summary': diff_summary,
            'detailed_changes': detailed_changes,
            'importance_score': importance_score
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Berechnet die Ähnlichkeit zwischen zwei Texten"""
        # Verwende verschiedene Metriken und nimm den Durchschnitt
        jaccard_sim = jaccard(text1, text2)
        
        # Sequenz-Ähnlichkeit
        seq_matcher = difflib.SequenceMatcher(None, text1, text2)
        seq_sim = seq_matcher.ratio()
        
        return (jaccard_sim + seq_sim) / 2
    
    def _determine_change_type(self, similarity_score: float) -> str:
        """Bestimmt den Typ der Änderung basierend auf dem Ähnlichkeitsscore"""
        if similarity_score > 0.9:
            return 'minor_update'
        if similarity_score > 0.7:
            return 'moderate_update'
        if similarity_score > 0.3:
            return 'major_update'
        return 'complete_rewrite'
    
    def _find_detailed_changes(self, old_content: str, new_content: str) -> List[Dict]:
        """Findet detaillierte Änderungen zwischen zwei Texten"""
        changes = []
        
        # Verwende difflib für Zeilen-basierte Unterschiede
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        
        differ = difflib.unified_diff(old_lines, new_lines, lineterm='')
        diff_lines = list(differ)
        
        current_change = {
            'type': 'section_change',
            'location': '',
            'removed_lines': [],
            'added_lines': []
        }
        for line in diff_lines:
            if line.startswith('@@'):
                if current_change['removed_lines'] or current_change['added_lines']:
                    changes.append(current_change)
                current_change = {
                    'type': 'section_change',
                    'location': line,
                    'removed_lines': [],
                    'added_lines': []
                }
            elif line.startswith('-'):
                current_change['removed_lines'].append(line[1:])
            elif line.startswith('+'):
                current_change['added_lines'].append(line[1:])
        
        if current_change['removed_lines'] or current_change['added_lines']:
            changes.append(current_change)
        
        return changes
    
    def _create_diff_summary(self, detailed_changes: List[Dict]) -> str:
        """Erstellt eine Zusammenfassung der Änderungen"""
        if not detailed_changes:
            return "Keine signifikanten Änderungen erkannt."
        
        total_additions = sum(len(change.get('added_lines', [])) for change in detailed_changes)
        total_removals = sum(len(change.get('removed_lines', [])) for change in detailed_changes)
        
        summary = f"Dokument wurde aktualisiert: {total_additions} Zeilen hinzugefügt, {total_removals} Zeilen entfernt."
        
        # Versuche spezifische Änderungen zu identifizieren
        change_keywords = []
        for change in detailed_changes:
            for line in change.get('added_lines', []):
                if any(keyword in line.lower() for keyword in ['deadline', 'requirement', 'mandatory', 'frist', 'pflicht']):
                    change_keywords.append('Wichtige Anforderungen geändert')
                    break
        
        if change_keywords:
            summary += f" Wichtige Änderungen: {', '.join(set(change_keywords))}"
        
        return summary
    
    def _calculate_change_importance(self, detailed_changes: List[Dict]) -> int:
        """Berechnet die Wichtigkeit der Änderungen"""
        if not detailed_changes:
            return 0
        
        importance = 0
        
        for change in detailed_changes:
            # Punkte für hinzugefügte Zeilen
            added_lines = change.get('added_lines', [])
            for line in added_lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in ['mandatory', 'required', 'deadline', 'pflicht', 'frist']):
                    importance += 5
                elif any(keyword in line_lower for keyword in ['new', 'updated', 'revised', 'neu', 'aktualisiert']):
                    importance += 3
                else:
                    importance += 1
            
            # Punkte für entfernte Zeilen
            removed_lines = change.get('removed_lines', [])
            importance += len(removed_lines)
        
        return min(importance, 100)  # Maximal 100 Punkte

