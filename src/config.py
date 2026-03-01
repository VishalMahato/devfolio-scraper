import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     os.getenv("DB_PORT", 5432),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "dbname":   os.getenv("DB_NAME", "devfolio"),
}

SCRAPE_SIZE  = int(os.getenv("SCRAPE_SIZE", 50))
SCRAPE_DELAY = float(os.getenv("SCRAPE_DELAY", 0.5))
