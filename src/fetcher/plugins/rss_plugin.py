# src/fetcher/plugins/rss_plugin.py

from .base import SourcePlugin
import aiohttp
import feedparser
from datetime import datetime
from typing import List, Dict

class RssPlugin(SourcePlugin):
    def __init__(self, url: str):
        self.url = url

    async def fetch(self) -> List[Dict]:
        """
        Ruft RSS-Feed ab und liefert eine Liste von Artikeln:
        [{ title, link, published, source }, …]
        """
        items: List[Dict] = []
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, timeout=10) as resp:
                text = await resp.text()

        parsed = feedparser.parse(text)
        for entry in parsed.entries:
            try:
                published = datetime(*entry.published_parsed[:6])
            except Exception:
                published = datetime.utcnow()

            items.append({
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", "").strip(),
                "published": published,
                "source": self.url
            })
        return items
