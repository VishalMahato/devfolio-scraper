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
            ama_enabled
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

# Numeric Filters
max_hacks = int(df['total_hackathons_attended'].max() or 10)
min_hacks = st.sidebar.slider("Min Hackathons Attended", 0, max_hacks, 0)

max_wins = int(df['total_hackathons_won'].max() or 5)
if max_wins > 0:
    min_wins = st.sidebar.slider("Min Hackathons Won", 0, max_wins, 0)
else:
    min_wins = 0

max_projects = int(df['total_projects'].max() or 10)
if max_projects > 0:
    min_projects = st.sidebar.slider("Min Projects Built", 0, max_projects, 0)
else:
    min_projects = 0

# Search
search_name = st.sidebar.text_input("Search Name or Username", "")

# Apply Filters
filtered_df = df[
    (df['total_hackathons_attended'] >= min_hacks) &
    (df['total_hackathons_won'] >= min_wins) &
    (df['total_projects'] >= min_projects)
]

if search_name:
    search_lower = search_name.lower()
    filtered_df = filtered_df[
        filtered_df['username'].astype(str).str.lower().str.contains(search_lower, na=False) |
        filtered_df['first_name'].astype(str).str.lower().str.contains(search_lower, na=False) |
        filtered_df['last_name'].astype(str).str.lower().str.contains(search_lower, na=False)
    ]

st.metric("Total Builders Found", len(filtered_df))

# Reorder columns for better UI
display_cols = [
    'profile_link', 'username', 'first_name', 'last_name', 
    'total_projects', 'total_hackathons_attended', 
    'total_hackathons_won', 'total_merits'
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
        "total_projects": st.column_config.NumberColumn("Projects", format="%d"),
        "total_hackathons_attended": st.column_config.NumberColumn("Hacks Attended", format="%d"),
        "total_hackathons_won": st.column_config.NumberColumn("Hacks Won", format="%d"),
        "total_merits": st.column_config.NumberColumn("Merits", format="%d"),
    }
)
