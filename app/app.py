import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="FPL Edge",
    layout="wide"
) 

st.title("FPL Edge")
st.subheader("A Fantasy Premier League Player Projections")

DATA_PATH = "scripts/data/processed/projections.csv"


try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error("No projections file found. Please run scripts/build_features.py first")
    st.stop()

st.sidebar.header("Filters")

positions = sorted(df["position"].dropna().unique().tolist())
selected_positions = st.sidebar.multiselect(
    "Position",
    options=positions,
    default=positions
)

min_price = float(df["price"].min()) 
max_price = float(df["price"].max()) 

price_range = st.sidebar.slider(
    "Price Range",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=0.1
)

min_projected = st.sidebar.number_input(
    "Minimum Projected Points",
    min_value=0.0,
    max_value=20.0,
    value=0.0,
    step=0.5
)

filtered_df = df[
    (df["position"].isin(selected_positions))&
    (df["price"] >= price_range[0])&
    (df["price"] <= price_range[1])&
    (df["projected_points"] >= min_projected)
]

filtered_df = filtered_df.sort_values("projected_points", ascending=False)

st.write(f"Showing {len(filtered_df)} players")

st.dataframe(
    filtered_df[
        [
            "web_name","team_name","position","price",
            "selected_by_percent","total_points","minutes","form",
            "points_per_game","opponent","home","fixture_difficulty",
            "projected_points","value"
        ]
    ], 
    use_container_width=True
)














