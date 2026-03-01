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

def get_unenriched_usernames(conn, batch_size=100):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT username FROM profiles
            WHERE enrichment_status = 'pending'
            ORDER BY total_hackathons_attended DESC
            LIMIT %s
        """, (batch_size,))
        return [row[0] for row in cur.fetchall()]

def upsert_enriched(conn, data: dict):
    with conn.cursor() as cur:
        import json
        cur.execute("""
            UPDATE profiles SET
                bio                   = %s,
                short_bio             = %s,
                city                  = %s,
                country               = %s,
                skills                = %s,
                social_links          = %s,
                experiences           = %s,
                projects              = %s,
                github_stats          = %s,
                prize_winnings_amount = %s,
                enriched_at           = NOW(),
                updated_at            = NOW()
            WHERE uuid = %s
        """, (
            data.get("bio"),
            data.get("short_bio"),
            data.get("city"),
            data.get("country"),
            json.dumps(data.get("skills", [])),
            json.dumps(data.get("social_links", {})),
            json.dumps(data.get("experiences", [])),
            json.dumps(data.get("projects", [])),
            json.dumps(data.get("github_stats", {})),
            data.get("prize_winnings_amount"),
            data.get("uuid"),
        ))
    conn.commit()

def update_enrichment_status(conn, username: str, status: str):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE profiles SET
                enrichment_status = %s,
                updated_at        = NOW()
            WHERE username = %s
        """, (status, username))
    conn.commit()
