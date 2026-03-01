import streamlit as st
import pandas as pd
import psycopg2
from src.config import DB_CONFIG

st.set_page_config(page_title="Devfolio Explorer", layout="wide", page_icon="🕵️")

st.title("🕵️‍♂️ Devfolio Builder Explorer")
st.markdown("Browse, filter, and discover top developer talent from your scraped Devfolio data.")

@st.cache_data(ttl=60)
def load_data():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            username, first_name, last_name, 
            total_hackathons_attended, total_hackathons_won,
            total_projects, total_merits, total_funding_received,
            ama_enabled,
            city, country, skills, github_stats, bio, enrichment_status
        FROM profiles
    """)
    rows = cur.fetchall()
    
    if not rows:
        cur.close()
        conn.close()
        return pd.DataFrame()

    cols = [desc[0] for desc in cur.description]
    df = pd.DataFrame(rows, columns=cols)
    cur.close()
    conn.close()
    
    # Create an actual profile URL link
    df['profile_link'] = "https://devfolio.co/@" + df['username']
    
    # Process JSONB columns safely
    df['skills'] = df['skills'].apply(lambda x: x if isinstance(x, list) else [])
    
    def extract_github_stat(row, stat_key):
        if isinstance(row, dict):
            return row.get(stat_key, 0)
        return 0
        
    df['github_followers'] = df['github_stats'].apply(lambda x: extract_github_stat(x, 'followers'))
    df['github_repos'] = df['github_stats'].apply(lambda x: extract_github_stat(x, 'repositories'))
    df['github_stars'] = df['github_stats'].apply(lambda x: extract_github_stat(x, 'stars'))
    
    # Prepare searchable strings for multi-selects
    df['city'] = df['city'].fillna('Unknown')
    df['country'] = df['country'].fillna('Unknown')
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Failed to connect to the database. Ensure Postgres is running! Error: {e}")
    st.stop()

if df.empty:
    st.warning("No profiles found. Run the scraper first! (python -m src.main)")
    st.stop()

st.sidebar.header("🎯 Filters")

# Status Filter to gauge enrichment
status_counts = df['enrichment_status'].value_counts()
st.sidebar.markdown(f"**Enrichment Progress:**")
st.sidebar.write(f"✅ Success: {status_counts.get('success', 0)}")
st.sidebar.write(f"⏳ Pending: {status_counts.get('pending', 0)}")

# Numeric Filters
max_hacks = int(df['total_hackathons_attended'].max() or 10)
min_hacks = st.sidebar.slider("Min Hackathons Attended", 0, max_hacks, 0)

max_wins = int(df['total_hackathons_won'].max() or 5)
min_wins = st.sidebar.slider("Min Hackathons Won", 0, max_wins, 0) if max_wins > 0 else 0

max_projects = int(df['total_projects'].max() or 10)
min_projects = st.sidebar.slider("Min Projects Built", 0, max_projects, 0) if max_projects > 0 else 0

# Extract a unique list of all skills across all users
all_skills = set()
for s_list in df['skills']:
    all_skills.update(s_list)
all_skills = sorted(list(all_skills))

# Location & Skills Filters
selected_skills = st.sidebar.multiselect("Filter by Skills", all_skills)
all_countries = sorted([c for c in df['country'].unique() if c != 'Unknown'])
selected_countries = st.sidebar.multiselect("Filter by Country", all_countries)

# Search
search_name = st.sidebar.text_input("Search Name, Username or Bio", "")

# Apply Filters
filtered_df = df[
    (df['total_hackathons_attended'] >= min_hacks) &
    (df['total_hackathons_won'] >= min_wins) &
    (df['total_projects'] >= min_projects)
]

if selected_countries:
    filtered_df = filtered_df[filtered_df['country'].isin(selected_countries)]

if selected_skills:
    # Check if user's skills list contains all the selected skills
    def has_required_skills(user_skills):
        return all(skill in user_skills for skill in selected_skills)
    filtered_df = filtered_df[filtered_df['skills'].apply(has_required_skills)]

if search_name:
    search_lower = search_name.lower()
    filtered_df = filtered_df[
        filtered_df['username'].astype(str).str.lower().str.contains(search_lower, na=False) |
        filtered_df['first_name'].astype(str).str.lower().str.contains(search_lower, na=False) |
        filtered_df['last_name'].astype(str).str.lower().str.contains(search_lower, na=False) |
        filtered_df['bio'].astype(str).str.lower().str.contains(search_lower, na=False)
    ]

st.metric("Total Builders Found", len(filtered_df))

# Reorder columns for better UI
display_cols = [
    'profile_link', 'username', 'first_name', 'last_name', 
    'skills', 'city', 'country',
    'total_projects', 'total_hackathons_won', 
    'github_followers', 'github_stars', 'github_repos'
]

st.dataframe(
    filtered_df[display_cols],
    use_container_width=True,
    hide_index=True,
    column_config={
        "profile_link": st.column_config.LinkColumn("Devfolio Link", display_text="View Profile ↗"),
        "username": "Username",
        "first_name": "First Name",
        "last_name": "Last Name",
        "skills": st.column_config.ListColumn("Skills"),
        "city": "City",
        "country": "Country",
        "total_projects": st.column_config.NumberColumn("Projects", format="%d"),
        "total_hackathons_won": st.column_config.NumberColumn("Hacks Won", format="%d"),
        "github_followers": st.column_config.NumberColumn("GitHub Followers", format="%d"),
        "github_stars": st.column_config.NumberColumn("GitHub Stars", format="%d"),
        "github_repos": st.column_config.NumberColumn("GitHub Repos", format="%d"),
    }
)
