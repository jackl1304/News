# src/main.py

import os
import asyncio
from dotenv import load_dotenv
from scheduler import start_scheduler

def main():
    # Umweltvariablen laden
    load_dotenv()
    # Scheduler starten
    asyncio.run(start_scheduler())

if __name__ == "__main__":
    main()
