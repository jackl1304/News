# src/scheduler.py

import os
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from fetcher.manager import load_plugins
from models.db import init_db, save_articles, get_unsent_articles, mark_as_sent
from renderer.email import render_newsletter
from sender.mail import send_email

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

async def job_poll_and_send():
    """
    Pollt alle Quellen, speichert neue Artikel, sendet
    ungesendete Artikel als Newsletter und markiert sie.
    """
    try:
        # 1) Lade Plugins
        plugins = load_plugins()
        logging.info(f"Loaded {len(plugins)} plugins.")

        # 2) Hole alle Artikel von den Plugins
        items = []
        for plugin in plugins:
            try:
                fetched = await plugin.fetch()
                items.extend(fetched)
                logging.info(f"Fetched {len(fetched)} items from {plugin.__class__.__name__}.")
            except Exception as e:
                logging.error(f"Error fetching from {plugin}: {e}")

        # 3) Speichere Artikel in DB
        await save_articles(items)
        logging.info(f"Saved {len(items)} items to database.")

        # 4) Hole ungesendete Artikel
        unsent = await get_unsent_articles()
        if not unsent:
            logging.info("No new articles to send.")
            return

        # 5) Rendern und Versenden
        html = render_newsletter(unsent)
        subject = f"News-Update: {len(unsent)} neue Artikel"
        send_email(html, subject)
        logging.info(f"Sent email with {len(unsent)} articles.")

        # 6) Als gesendet markieren
        ids = [item["id"] for item in unsent]
        await mark_as_sent(ids)
        logging.info("Marked articles as sent.")
    except Exception:
        logging.exception("Unexpected error in job_poll_and_send.")

async def start_scheduler():
    """
    Initialisiert DB und startet den Scheduler:
    - Intervall-Job (Poll-Intervall)
    - Wöchentlicher Cron-Job
    """
    # .env laden
    load_dotenv()

    # DB initialisieren
    await init_db()
    logging.info("Database initialized.")

    # Scheduler konfigurieren
    sched = AsyncIOScheduler()

    # Poll-Intervall aus ENV oder Default (15 Minuten)
    interval = int(os.getenv("POLL_INTERVAL_MINUTES", 15))
    sched.add_job(job_poll_and_send, "interval", minutes=interval, next_run_time=datetime.now())

    # Wöchentlicher Fallback (Cron) aus ENV oder Default (Mo 08:00)
    cron = os.getenv("WEEKLY_CRON", "0 8 * * MON").split()
    sched.add_job(
        job_poll_and_send,
        "cron",
        day_of_week=cron[3].lower(),
        hour=int(cron[1]),
        minute=int(cron[0])
    )

    sched.start()
    logging.info("Scheduler started.")
    # Laufende Schleife, damit das Programm nicht beendet
    await asyncio.Event().wait()
