# Business Logic & Architecture

This document describes the internal workings of the Devfolio Scraper.

## Architecture Overview
The scraper operates as a one-off batch process. It extracts data from the Devfolio Search API and loads it directly into a local PostgreSQL database.

**Tech Stack**:
*   `httpx`: High performance HTTP client for fetching data.
*   `psycopg2`: PostgreSQL adapter for Python.
*   `tenacity`: Robust retry library to handle network flakes and rate-limiting.

## Component Breakdown

### 1. Scraper (`src/scraper.py`)
Handles all communications with the external API.
*   **`fetch_page`**: Makes the actual HTTP request. Wrapped in a `@retry` decorator (Exponential Backoff). If the API rate limits or drops the connection, it waits and tries up to 5 times.
*   **`get_all_builders`**: A Python generator. It acts as an infinite loop that tracks the current pagination offset (`from_offset`). It fetches a page, unwraps the `_source` Elasticsearch object, yields the list of profiles to the main script, increments the offset, sleeps for `SCRAPE_DELAY`, and loops.
*   **Limit Handling**: Automatically stops yielding pages if the remaining hits run out, or if it reaches the Elasticsearch 10,000 result integer limit to prevent HTTP 400 crash errors.

### 2. Database Layer (`src/database.py`)
Handles persistent storage. 
*   **Upsert Logic**: We use `ON CONFLICT (uuid) DO UPDATE` in PostgreSQL. 
    *   If a profile `uuid` is completely new, it performs an standard `INSERT`.
    *   If a profile `uuid` already exists in the database, it **updates** the changing fields (e.g. `total_hackathons_attended`, `total_projects`) instead of crashing due to a unique constraint violation.
    *   This logic makes the script highly idempotent (you can safely run it 10 times in a row without corrupting data).
*   **Raw JSONB Storage**: The entire unaltered API response for that specific user is saved in the `raw` column as JSONB. If Devfolio adds a new field tomorrow, it is automatically captured in the database without requiring schema changes.

### 3. Orchestration (`src/main.py`)
The entry point.
1. Establishes a connection to the Postgres database.
2. Checks the first page of the API to calculate how many total builders are available.
3. Consumes the `get_all_builders` generator page by page.
4. Passes each profile dictionary into the `upsert_profile` function.
5. Keeps a running total logged to the console to measure progress.

## Deduplication Strategy
If running multiple passes (e.g. scraping by Top Projects, then scraping again by Top Hackathons), the database `uuid` unique constraint paired with the upsert logic seamlessly merges the duplicate profiles so that only the most updated data remains. No complex in-memory set tracking is needed.
