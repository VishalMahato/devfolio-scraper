# Devfolio Scraper

A Python script to scrape devfolio and insert data into a PostgreSQL database.

## Setup
1. Ensure you have Python 3.10+ and PostgreSQL installed.
2. Clone the repo and navigate to `devfolio-scraper/`.
3. Create and activate the virtual environment: `python -m venv venv`
4. Install requirements: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in DB credentials.
6. Initialize the DB with `db/init.sql`.

## Running
```bash
python -m src.main
```
