import streamlit as st
import pandas as pd
import json
from pathlib import Path

from styles.theme import inject_theme

st.set_page_config(page_title="Backtest", layout="wide")
inject_theme()
st.title("Model Backtest & Evaluation")

st.write("""
This model predicts Fantasy Premier League points using lagged rolling features 
(minutes, points, ICT index) to avoid lookahead bias. It's trained on gameweeks 1-30 
and evaluated on held-out gameweeks 31-38 from the 2024-25 season.
""")

# Load metrics
PROJECT_ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = PROJECT_ROOT / "models" / "model_metrics.json"
IMPORTANCE_PATH = PROJECT_ROOT / "models" / "feature_importance.csv"

if not METRICS_PATH.exists():
    st.error(f"Metrics file not found: {METRICS_PATH}")
    st.info(
        "Run the evaluation cells in `notebooks/02_model.ipynb` to generate metrics."
    )
    st.stop()

try:
    with open(METRICS_PATH, "r") as f:
        metrics = json.load(f)
except Exception as e:
    st.error(f"Error loading metrics: {e}")
    st.stop()

# Display core metrics
st.subheader("Core Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("MAE", f"{metrics.get('mae', 0):.2f} pts")
col2.metric("RMSE", f"{metrics.get('rmse', 0):.2f} pts")
col3.metric("Rank Correlation", f"{metrics.get('spearman', 0):.2f}")
col4.metric("Captain Hit Rate", f"{metrics.get('captain_hit_rate', 0):.0%}")

# Baseline comparison
st.subheader("Model vs Baseline")
baseline_mae = metrics.get("baseline_mae")
model_mae = metrics.get("mae")

if baseline_mae and model_mae:
    if model_mae < baseline_mae:
        improvement = ((baseline_mae - model_mae) / baseline_mae) * 100
        st.success(
            f"✅ Model MAE ({model_mae:.2f}) beats baseline ({baseline_mae:.2f}) by {improvement:.1f}%"
        )
    else:
        st.warning(
            f"⚠️ Model MAE ({model_mae:.2f}) is similar to baseline ({baseline_mae:.2f})"
        )

st.write(
    f"**Test set:** {metrics.get('test_gameweeks', 'unknown')} ({metrics.get('n_test_rows', 0):,} player-gameweeks)"
)

# Feature importance
if IMPORTANCE_PATH.exists():
    st.subheader("Feature Importance")
    try:
        importance = pd.read_csv(IMPORTANCE_PATH)
        importance = importance.sort_values("importance", ascending=False)

        # Show top 10 features as a bar chart
        st.bar_chart(importance.head(10).set_index("feature"))

        with st.expander("All features"):
            st.dataframe(importance, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not load feature importance: {e}")
else:
    st.info("Feature importance data not available.")

# Methodology
st.subheader("Methodology")
st.write("""
**Features:** Lagged rolling averages (3-game and 5-game) of minutes, points, and ICT index. 
No current-week data is used to prevent lookahead bias.

**Target:** Next gameweek total points.

**Baseline:** Predicting each player's own 3-game rolling average (a strong naive baseline).

**Evaluation:**
- **MAE (Mean Absolute Error):** Average prediction error in points (lower is better).
- **RMSE (Root Mean Squared Error):** Penalizes large errors more heavily.
- **Rank Correlation (Spearman):** Does the model rank good players above bad ones? 
  This matters more than exact points for FPL decisions.
- **Captain Hit Rate:** How often the model's top-10 predictions contained the actual 
  highest-scoring player that gameweek (random chance ≈ 1.7%).

**Limitations:**
- Trained on a single season; player transfers and form changes year-to-year.
- Minutes/rotation risk is only partially captured.
- Model predicts points, not transfer value or price dynamics.
""")

# Data source attribution
st.caption(
    f"Season: {metrics.get('season', 'unknown')} • Source: FPL API + [vaastav/Fantasy-Premier-League](https://github.com/vaastav/Fantasy-Premier-League)"
)
