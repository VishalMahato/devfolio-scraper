from src.scraper import get_all_builders, get_total
from src.database import get_connection, upsert_profile

def main():
    locations = ["Kolkata"]  # Filtering by Kolkata builders
    sort_by   = "projects_built"  # or "hackathons_attended" / "hackathons_won"

    print("Connecting to DB...")
    conn = get_connection()

    total_available = get_total(locations, sort_by)
    print(f"Total builders available: {total_available} (max fetchable: 10,000)")

    total_saved = 0
    for page_num, page in enumerate(get_all_builders(locations, sort_by), start=1):
        for profile in page:
            upsert_profile(conn, profile)
        total_saved += len(page)
        print(f"Page {page_num} done — {total_saved} profiles saved so far...")

    conn.close()
    print(f"\nDone! Total profiles scraped and stored: {total_saved}")

if __name__ == "__main__":
    main()
