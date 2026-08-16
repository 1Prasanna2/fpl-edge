import pandas as pd
import streamlit as st
from pathlib import Path

from components.hero_cards import render_hero_section, render_hero_details
from styles.theme import inject_theme

st.set_page_config(
    page_title="FPL Edge",
    layout="wide"
) 
inject_theme()

st.title("FPL EDGE")
st.subheader("Fantasy Premier League Projections & Weekly Decision Engine")
render_hero_section()
st.divider()
render_hero_details()
# PROJECT_ROOT = Path(__file__).resolve().parents[1]
# DATA_PATH = PROJECT_ROOT / "data" / "processed" / "projections.csv"

# if not DATA_PATH.exists():
#     st.error(f"Projections file not found: {DATA_PATH}")
#     st.info("Run the data pipeline: `python scripts/build_features.py`")
#     st.stop()

# try:
#     df = pd.read_csv(DATA_PATH)
#     if df.empty:
#         st.error("Projections file is empty. Check the data pipeline.")
#         st.stop()
# except Exception as e:
#     st.error(f"Error loading projections: {e}")
#     st.stop()

# st.sidebar.header("Filters")

# if "position" in df.columns:
#     positions = sorted(df["position"].dropna().unique().tolist())
#     selected_positions = st.sidebar.multiselect(
#         "Position",
#         options=positions,
#         default=positions
#     )
# else:
#     selected_positions = []
    

# if "price" in df.columns and not df["price"].isna().all():
#     min_price = float(df["price"].min()) 
#     max_price = float(df["price"].max()) 

#     if min_price != max_price:
#         price_range = st.sidebar.slider(
#             "Price Range",
#             min_value=min_price,
#             max_value=max_price,
#             value=(min_price, max_price),
#             step=0.1
#         )
#     else:
#         price_range = (min_price, max_price)
# else:
#     price_range = (0,100)
    
# if "projected_points" in df.columns:
#         min_projected = st.sidebar.number_input(
#         "Minimum Projected Points",
#         min_value=0.0,
#         max_value=20.0,
#         value=0.0,
#         step=0.5
#     )
# else:
#     min_projected = 0.0

# filtered_df = df.copy()

# if "position" in filtered_df.columns:
#     filtered_df = filtered_df[filtered_df["position"].isin(selected_positions)]
    
# if "price" in filtered_df.columns:
#     filtered_df = filtered_df[
#         (filtered_df["price"] >= price_range[0])&
#         (filtered_df["price"] <= price_range[1])
#     ]

# if "projected_points" in filtered_df.columns:
#     filtered_df = filtered_df[filtered_df["projected_points"] >= min_projected]
    
# if "projected_points" in filtered_df.columns:
#     filtered_df = filtered_df.sort_values("projected_points", ascending=False)

# st.write(f"Showing {len(filtered_df)} players")

# if filtered_df.empty:
#     st.info("No players match your filters. Try adjusting the criteria.")
# else:
#     display_columns = [
#         "web_name","team_name","position","price",
#         "selected_by_percent","total_points","minutes",
#         "points_per_game","opponent","home","fixture_difficulty",
#         "projected_points","value"
#     ]
    
#     available_columns = [col for col in display_columns if col in filtered_df.columns]

#     st.dataframe(
#         filtered_df[available_columns],
#         use_container_width=True
#     )
