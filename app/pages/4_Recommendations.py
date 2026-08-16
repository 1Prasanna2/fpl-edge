import pandas as pd
import streamlit as st
from pathlib import Path

from styles.theme import inject_theme

st.set_page_config(page_title="Recommendations", layout="wide")
inject_theme()
st.title("Weekly Recommendations")

# HERE = Path(__file__).resolve()

# CANDIDATES = [
#     HERE.parents[2] / "data" / "processed",  # <root>/data/processed
#     HERE.parents[1]
#     / "data"
#     / "processed",  # <root>/app/data/processed (wrong, but check)
#     Path.cwd() / "data" / "processed",  # wherever the terminal was
#     Path.cwd() / "scripts" / "data" / "processed",  # the old stray location
# ]

# PROCESSED = next((c for c in CANDIDATES if (c / "top_players.csv").exists()), None)

# if PROCESSED is None:
#     st.error("Recommendation files not found. I looked in:")
#     for c in CANDIDATES:
#         st.code(str(c))
#     st.stop()
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED = PROJECT_ROOT / "data" / "processed"

if not PROCESSED.exists():
    st.error(f"Data directory not found: {PROCESSED}")
    st.info("Run the data pipeline first: `python scripts/generate_recommendations.py`")
    st.stop()


def load(name):
    path = PROCESSED / name
    if not path.exists():
        st.warning(f"File not found: {name}")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(path)
        if df.empty:
            st.warning(f"File is empty: {name}")
        return df
    except Exception as e:
        st.error(f"Error loading {name} : {e}")
        return pd.DataFrame()

top = load("top_players.csv")
captains = load("captain_recommendations.csv")
value = load("value_picks.csv")
diffs = load("differentials.csv")

if all(df.empty for df in [top, captains, value, diffs]):
    st.error("No recommendation data available. Please check the pipeline.")
    st.stop()

SHOW = ["rank", "web_name","team_short_name","position","price","selected_by_percent","opponent","home","fixture_difficulty","projected_points","value",]


def show(df,description):
    st.write(description)
    
    if df.empty:
        st.info("No data available for this category.")
        return 
    cols = [c for c in SHOW if c in df.columns]
    st.dataframe(df[cols], use_container_width=True)


tab1, tab2, tab3, tab4 = st.tabs(
    ["Top Projected", "Captains", "Value Picks", "Differentials"]
)

with tab1:
    show(top, "Highest projected points for the next gameweek.")
with tab2:
    show(captains, "Best captain options, ranked by projected points.")
with tab3:
    show(value, "Best points-per-£m among cheaper players.")
with tab4:
    show(diffs, "Low-ownership players with strong projections - rank boosters.")
