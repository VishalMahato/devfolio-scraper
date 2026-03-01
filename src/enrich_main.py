import time
import random
import psycopg2
from src.database import get_connection, upsert_enriched, update_enrichment_status
from src.enricher import fetch_profile_detail

def main():
    conn = get_connection()
    total = 0
    errors = 0

    while True:
        usernames = get_unenriched_usernames(conn, batch_size=100)
        if not usernames:
            print("All profiles enriched!")
            break

        for username in usernames:
            try:
                data = fetch_profile_detail(username)
                if data:
                    upsert_enriched(conn, data)
                    update_enrichment_status(conn, username, 'success')
                    total += 1
                    print(f"✓ {username} enriched (total: {total})")
                else:
                    update_enrichment_status(conn, username, 'not_found')
                    print(f"✗ {username} — no data (private/deleted)")
            except Exception as e:
                update_enrichment_status(conn, username, 'error')
                errors += 1
                print(f"✗ {username} error: {e}")

            time.sleep(0.5 + random.uniform(0, 0.3))

    conn.close()
    print(f"\nDone! Enriched: {total}, Errors: {errors}")

def get_unenriched_usernames(conn, batch_size=100):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT username FROM profiles
            WHERE enrichment_status = 'pending'
            ORDER BY total_hackathons_attended DESC
            LIMIT %s
        """, (batch_size,))
        return [row[0] for row in cur.fetchall()]

if __name__ == "__main__":
    main()
