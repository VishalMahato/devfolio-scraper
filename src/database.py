import json
import psycopg2
from src.config import DB_CONFIG

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def upsert_profile(conn, source: dict):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO profiles (
                uuid, username, first_name, last_name,
                profile_image,
                total_hackathons_attended, total_hackathons_won,
                total_projects, total_merits, total_funding_received,
                ama_enabled, raw, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (uuid) DO UPDATE SET
                username                  = EXCLUDED.username,
                first_name                = EXCLUDED.first_name,
                last_name                 = EXCLUDED.last_name,
                profile_image             = EXCLUDED.profile_image,
                total_hackathons_attended = EXCLUDED.total_hackathons_attended,
                total_hackathons_won      = EXCLUDED.total_hackathons_won,
                total_projects            = EXCLUDED.total_projects,
                total_merits              = EXCLUDED.total_merits,
                total_funding_received    = EXCLUDED.total_funding_received,
                ama_enabled               = EXCLUDED.ama_enabled,
                raw                       = EXCLUDED.raw,
                updated_at                = NOW();
        """, (
            source.get("uuid"),
            source.get("username"),
            source.get("first_name"),
            source.get("last_name"),
            source.get("profile_image"),
            source.get("total_hackathons_attended", 0),
            source.get("total_hackathons_won", 0),
            source.get("total_projects", 0),
            source.get("total_merits", 0),
            source.get("total_funding_received", 0),
            source.get("ama_enabled", False),
            json.dumps(source),
        ))
    conn.commit()
