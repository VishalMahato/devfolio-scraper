import httpx
import json
import time
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

HEADERS = {
    "accept": "text/html,application/xhtml+xml",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def fetch_profile_detail(username: str) -> dict | None:
    url = f"https://devfolio.co/@{username}"
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        r = client.get(url, headers=HEADERS)
        if r.status_code == 404:
            return None
        r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    script = soup.find("script", {"id": "__NEXT_DATA__"})
    if not script:
        return None

    data = json.loads(script.string)

    # Navigate to the user object
    queries = data["props"]["pageProps"]["dehydratedState"]["queries"]
    user_data = None
    stats_data = None

    for q in queries:
        key = q.get("queryKey", [])
        if key[0] == "userPublicProfile":
            users = q["state"]["data"].get("users", [])
            if users:
                user_data = users[0]
        elif key[0] == "userDevfolioStats":
            stats_data = q["state"]["data"]

    if not user_data:
        return None

    parsed_data = parse_profile(user_data, stats_data)
    
    # Also fetch GitHub stats directly
    github_stats = fetch_github_stats(username)
    if github_stats:
        parsed_data["github_stats"] = github_stats
        
    return parsed_data

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def fetch_github_stats(username: str) -> dict | None:
    url = f"https://api.devfolio.co/api/users/{username}/githubPublicProfile"
    headers = {
        "accept": "application/json, text/plain, */*",
        "user-agent": HEADERS["user-agent"]
    }
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        r = client.get(url, headers=headers)
        if r.status_code in (404, 422):
             return None
        r.raise_for_status()
        
    return r.json()

def parse_profile(user: dict, stats: dict) -> dict:
    # Extract social links as clean dict
    social_links = {}
    for p in user.get("profiles", []):
        platform = p.get("profile", {}).get("name", "").lower()
        social_links[platform] = p.get("value")

    # Extract skills
    skills = [
        s["skill"]["name"]
        for s in user.get("skills", [])
        if s.get("skill")
    ]

    # Extract experiences
    experiences = [
        {
            "title": e.get("title"),
            "company": e.get("company", {}).get("name"),
            "start": e.get("start"),
            "end": e.get("end"),
            "description": e.get("description"),
        }
        for e in user.get("experiences", [])
    ]

    # Extract top projects
    projects = [
        {
            "name": p["project"]["name"],
            "slug": p["project"]["slug"],
            "tagline": p["project"]["tagline"],
            "links": p["project"].get("links", "").split(","),
            "prizes_won": p["project"]["winning_prizes_aggregate"]["aggregate"]["count"] if p["project"].get("winning_prizes_aggregate") else 0,
        }
        for p in user.get("public_profile_projects", [])
        if p.get("project")
    ]

    address = user.get("address", {}) or {}

    return {
        "uuid": user.get("uuid"),
        "username": user.get("username"),
        "bio": user.get("bio"),
        "short_bio": user.get("short_bio"),
        "city": address.get("city"),
        "country": address.get("country"),
        "skills": skills,
        "social_links": social_links,
        "experiences": experiences,
        "projects": projects,
        "prize_winnings_amount": stats.get("prize_winnings_amount") if stats else None,
    }
