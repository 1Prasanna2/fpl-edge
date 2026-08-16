import pandas as pd
import streamlit as st
from pathlib import Path 

from styles.theme import inject_theme

st.set_page_config(page_title="Transfer Target Finder",layout="wide")
inject_theme()
st.title("Transfer Target Finder")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJ = PROJECT_ROOT / "data" / "processed" / "projections.csv"

if not PROJ.exists():
    st.error(f"Projections file not found: {PROJ}")
    st.info("Run the pipeline: `python scripts/build_features.py`")
    st.stop()

try:
    df = pd.read_csv(PROJ)
except Exception as e:
    st.error(f"Error loading projections: {e}")
    st.stop()

if df.empty:
    st.error("Projections file is empty. Re-run the pipeline.")
    st.stop()

st.sidebar.header("Filters")

if "position" in df.columns:
    positions = sorted(df["position"].dropna().unique().tolist())
    position = st.sidebar.selectbox("Position", options=positions)
else:
    position = None

has_price = "price" in df.columns and not df["price"].isna().all()
lo = float(df["price"].min()) if has_price else 4.0
hi = float(df["price"].max()) if has_price else 15.5
if hi <= lo:
    hi = lo + 0.1
max_price = st.sidebar.slider(
    "Maximum Price (£m)", min_value=lo, max_value=hi, value=min(hi, 10.0), step=0.1
)

avoid_injured = st.sidebar.checkbox("Avoid doubtful / injured players", value=True)

filtered = df.copy()

if position and "position" in filtered.columns:
    filtered = filtered[filtered["position"] == position]

if "price" in filtered.columns:
    filtered = filtered[filtered["price"] <= max_price]

if avoid_injured and "status" in filtered.columns:
    filtered = filtered[~filtered["status"].isin(["i", "d", "s"])]

if "projected_points" in filtered.columns:
    filtered = filtered.sort_values("projected_points", ascending=False)

st.write(f"Best Transfer Targets ({len(filtered)} players)")

if filtered.empty:
    st.info("No players match your filters. Try widening the criteria.")
else:
    # Only show columns that exist
    display_columns = [
        "web_name",
        "team_name",
        "position",
        "price",
        "opponent",
        "home",
        "fixture_difficulty",
        "selected_by_percent",
        "form",
        "points_per_game",
        "projected_points",
        "value",
        "status",
        "news",
    ]

    available_columns = [col for col in display_columns if col in filtered.columns]

    st.dataframe(filtered[available_columns], use_container_width=True, hide_index=True)
