import httpx
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from src.config import SCRAPE_SIZE, SCRAPE_DELAY

API_URL = "https://api.devfolio.co/api/search/builders"
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "origin": "https://devfolio.co",
    "referer": "https://devfolio.co/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=10))
def fetch_page(from_offset: int, locations: list = None, sort_by: str = "projects_built") -> dict:
    payload = {
        "most": sort_by,
        "locations": locations or [],
        "from": from_offset,
        "size": SCRAPE_SIZE
    }
    with httpx.Client(timeout=30) as client:
        r = client.post(API_URL, headers=HEADERS, json=payload)
        r.raise_for_status()
        return r.json()

def get_total(locations=None, sort_by="projects_built") -> int:
    data = fetch_page(0, locations, sort_by)
    return data.get("hits", {}).get("total", {}).get("value", 0)

def get_all_builders(locations=None, sort_by="projects_built"):
    """Generator — yields one page of _source dicts at a time"""
    from_offset = 0
    while True:
        data = fetch_page(from_offset, locations, sort_by)
        hits = data.get("hits", {}).get("hits", [])
        
        if not hits:
            break

        yield [hit["_source"] for hit in hits]  # unwrap _source here

        from_offset += SCRAPE_SIZE

        # Elasticsearch hard cap is 10000 — stop before we make an invalid request
        if from_offset >= 10000:
            print("Hit Elasticsearch 10k limit. Wrapping up current search...")
            break

        time.sleep(SCRAPE_DELAY)
