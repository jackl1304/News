# src/models/db.py

import os
import aiosqlite
from typing import List, Dict

# Pfad zur SQLite-Datenbank, standardmäßig im data/-Ordner
DB_PATH = os.getenv("DB_PATH", "./data/news.db")

async def init_db() -> None:
    """
    Initialisiert die Datenbank und legt die Tabelle an, falls nicht vorhanden.
    """
    # Verzeichnisse anlegen, falls nötig
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                link TEXT NOT NULL UNIQUE,
                published TEXT,
                source TEXT,
                sent INTEGER NOT NULL DEFAULT 0
            );
        """)
        await db.commit()

async def save_articles(items: List[Dict]) -> None:
    """
    Speichert neue Artikel; doppelte Links werden ignoriert.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        for item in items:
            # published als ISO-String speichern
            pub = item["published"]
            pub_str = pub.isoformat() if hasattr(pub, "isoformat") else str(pub)
            await db.execute(
                """
                INSERT OR IGNORE INTO articles
                    (title, link, published, source)
                VALUES (?, ?, ?, ?);
                """,
                (item["title"], item["link"], pub_str, item.get("source"))
            )
        await db.commit()

async def get_unsent_articles() -> List[Dict]:
    """
    Gibt alle Artikel zurück, die noch nicht versendet wurden.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, title, link, published, source FROM articles WHERE sent = 0 ORDER BY published DESC;"
        )
        rows = await cursor.fetchall()

    return [
        {
          "id": row[0],
          "title": row[1],
          "link": row[2],
          "published": row[3],
          "source": row[4]
        }
        for row in rows
    ]

async def mark_as_sent(article_ids: List[int]) -> None:
    """
    Markiert die Artikel mit den gegebenen IDs als gesendet.
    """
    if not article_ids:
        return

    placeholders = ",".join("?" for _ in article_ids)
    query = f"UPDATE articles SET sent = 1 WHERE id IN ({placeholders});"

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(query, article_ids)
        await db.commit()
