import pandas as pd
import streamlit as st
from pathlib import Path

from styles.theme import inject_theme 
st.set_page_config(page_title="Players", layout="wide")
inject_theme()
st.title("Player Explorer")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJ = PROJECT_ROOT / "data" / "processed" / "projections.csv"

if not PROJ.exists():
    st.error(f"Projection files not found: {PROJ}.")
    st.error("Run the pipeline: `python scripts/build_features.py`")
    st.stop()

try:
    df = pd.read_csv(PROJ)
except Exception as e:
    st.error(f"Error loading projections: {e}")
    st.stop()
    
    
st.sidebar.header("Filters")
q = st.sidebar.text_input("Search player")

positions = sorted(df["position"].dropna().unique())
pos = st.sidebar.multiselect("Position", positions, default=positions)

has_price = "price" in df.columns and not df["price"].isna().all()
lo = float(df["price"].min()) if has_price else 4.0
hi = float(df["price"].max()) if has_price else 15.5
if hi <= lo:
    hi = lo + 0.1
max_price = st.sidebar.slider("Max price (£m)", lo, hi, hi, 0.1)

view = df.copy()
if "position" in view.columns:
    view = view[view["position"].isin(pos)]
if "price" in view.columns:
    view = view[view["price"] <= max_price]
if q and "web_name" in view.columns:
    view = view[view["web_name"].str.contains(q, case=False, na=False)]
if "projected_points" in view.columns:
    view = view.sort_values("projected_points", ascending=False)

COLS = [
    c
    for c in ["web_name", "team_short_name", "position", "price", "selected_by_percent", "opponent", "projected_points", "value",]
    if c in view.columns
]

st.write(f"{len(view)} players")
if view.empty:
    st.info("No players match your filters. Try widening the criteria.")
else:
    st.dataframe(view[COLS], use_container_width=True, hide_index=True)


st.divider()
st.subheader("Player Spotlight")

options = view["web_name"].head(100).tolist() if "web_name" in view.columns else []
if options:
    name = st.selectbox("Pick a player", options)
    p = view[view["web_name"] == name].iloc[0]
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Projected", f"{p['projected_points']:.1f}")
    c2.metric("Price", f"£{p.get('price', 0):.1f}m")
    c3.metric("Owned", f"{p.get('selected_by_percent', 0):.1f}%")
    c4.metric("Position", f"{p.get('position')}")
    c5.metric("Next fixture", str(p.get("opponent", "—")))
else:
    st.info("Select at least one player to see the spotlight.")