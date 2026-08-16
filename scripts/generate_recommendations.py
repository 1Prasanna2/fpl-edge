import pandas as pd
import numpy as np
from pathlib import Path

VALUE_MAX_PRICE = 8.5
DIFF_MAX_OWNERSHIP = 10.0
DIFF_MIN_OWNERSHIP = 0.1

MIN_CHANCE_TO_PLAY = 50

TOP_PLAYERS_COUNT = 50
CAPTAIN_COUNT = 10
VALUE_COUNT = 20
DIFFERENTIAL_COUNT = 20

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" /"processed"
PROJECTIONS_FILE = PROCESSED_DIR / "projections.csv"


DISPLAY_COLUMNS = [
    "rank", "web_name","team_short_name", "position", "price",
    "selected_by_percent", "form", "opponent", "home", 
    "fixture_difficulty", "projected_points", "value", "edge_score",
    "confidence", "recommendation_reason"
]


def load_projections():
    if not PROJECTIONS_FILE.exists():
        raise SystemExit(
            "projections.csv not found. Run `python scripts/build_features.py` first."
        )
    df = pd.read_csv(PROJECTIONS_FILE)

    numeric_columns = [
        "price",
        "selected_by_percent",
        "projected_points",
        "value",
        "minutes",
        "chance_of_playing_next_round",
        "form",
        "fixture_difficulty"
    ]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def available_mask(df):
    mask = pd.Series(True, index=df.index)
    if "status" in df.columns:
        mask &= ~df["status"].isin(["i","s"])
    if "chance_of_playing_next_round" in df.columns:
        mask &= (df["chance_of_playing_next_round"].fillna(100) >= MIN_CHANCE_TO_PLAY)
    return mask

def min_max_score(series):
    series = pd.to_numeric(
        series, errors="coerce"
    ).fillna(0)
    
    minimum = series.min()
    maximum = series.max()
    
    if maximum == minimum:
        return pd.Series(
            50.0, index=series.index
        )

    return (
        (series - minimum) / (maximum - minimum) * 100
    )
    

def add_scores(df):
    df = df.copy()
    
    if "price" in df.columns:
        df["value"] = (
            df["projected_points"] / df["price"].replace(0, np.nan)
        )
    else:
        df["value"] = 0
        
    df["projection_score"] = min_max_score(df["projected_points"])
    
    if "form" in df.columns:
        df["form_score"] = min_max_score(df["form"])
    else:
        df["form_score"] = 50
    
    if "fixture_difficulty" in df.columns:
        difficulty = (
            df["fixture_difficulty"].fillna(3)
        )
        
        df["fixture_score"] = (
            5 - difficulty
        ) / 4 * 100
        
        df["fixture_score"] = (
            df["fixture_score"].clip(0,100)
        )
    else:
        df["fixture_score"] = 50
    
    if "chance_of_playing_next_round" in df.columns:
        df["availability_score"] = (
            df["chance_of_playing_next_round"].fillna(100).clip(0, 100)
        )
    else:
        df["availability_score"] = 100
    
    if "home" in df.columns:
        home_values = (
            df["home"].astype(str).str.lower()
        )
        
        df["home_score"] = np.where(
            home_values.isin(["true","1","yes"]),100,50
            )
    else:
        df["home_score"] = 50
    
    df["value_score"] = min_max_score(df["value"])
    
    if "selected_by_percent" in df.columns:
        ownership = (
            df["selected_by_percent"].fillna(0)
        )
        
        df["ownership_opportunity"] = (100 - ownership.clip(0,100))
    else: 
        df["ownership_oppoertunity"] = 50
    
    return df
    
def calculate_top_score(df):
    return (
        df["projection_score"] * 0.60 +
        df["form_score"] * 0.15 +
        df["fixture_score"] * 0.15 + 
        df["availability_score"] * 0.10
    )

def calculate_captain_score(df):
    return (
        df["projection_score"] * 0.50 +
        df["fixture_score"] * 0.20 + 
        df["form_score"] * 0.15 +
        df["availability_score"] * 0.10 +
        df["home_score"] * 0.05
    )

def calculate_value_score(df):
    return (
        df["projection_score"] * 0.50 +
        df["projection_score"] * 0.25 +
        df["fixture_score"] * 0.15 + 
        df["availability_score"] * 0.10
    )

def calculate_differential_score(df):
    return (
        df["projection_score"] * 0.50 +
        df["fixture_score"] * 0.20 + 
        df["ownership_opportunity"] * 0.15 +
        df["form_score"] * 0.10 +
        df["value_score"] * 0.05 
    )

def generate_reason(row):
    reasons = []
    
    projected = row.get("projected_points",0)
    form = row.get("form",0)
    fixture = row.get("fixture_difficulty", 3)
    ownership = row.get("selected_by_percent", np.nan)
    value = row.get("value", 0)
    
    if projected >= 8:
        reasons.append("elite projection")
    elif projected >= 6:
        reasons.append("strong projection")
    
    if form >= 6:
        reasons.append("excellent form")
    elif form >= 4:
        reasons.append("good form")
    
    if pd.notna(fixture):
        if fixture <= 2:
            reasons.append("favorable fixture")
        elif fixture >= 4:
            reasons.append("difficult fixture")
    
    if pd.notna(ownership):
        if ownership < 5:
            reasons.append("low ownership")
        elif ownership < 10:
            reasons.append("under-owned")
    
    if pd.notna(value) and value >= 0.8:
        reasons.append("strong value")
    
    if not reasons:
        reasons.append(
            "strong overall statistical profile"
        )
    return " + ".join(reasons)
    

def prepare_recommendations(df,score,count):
    result = df.copy()
    
    result["edge_score"] = (
        score.clip(0, 100).round(1)
    )
    
    result["confidence"] = (
        result["edge_score"].clip(1, 99).round().astype(int)
    )
    
    result["recommendation_reason"] = (
        result.apply(generate_reason, axis=1)
    )
    
    result = (
        result.sort_values("edge_score", ascending=False)
    ).head(count).reset_index(drop=True)
    
    result.insert(0, "rank", result.index + 1)
    
    return result

def show(df, title):
    cols = [c for c in DISPLAY_COLUMNS if c in df.columns]
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(df.head(10)[cols].to_string(index=False))

def main():
    print("\n FPL Edge Recommendation Engine")
    print("=" * 80)
    
    df = load_projections()
    print(f"Loaded players: {len(df)}")
    
    pool = df[available_mask(df)].copy()
    print(f"Available players: {len(pool)}")
    
    if pool.empty:
        raise SystemExit("No available players found.")

    pool = add_scores(pool)

    # if "value" not in pool.columns or pool["value"].isna().all():
    #     pool["value"] = pool["projected_points"] / pool["price"].replace(0,pd.NA)

    top_players = prepare_recommendations(
        pool, calculate_top_score(pool), TOP_PLAYERS_COUNT
    )
    # top_players = (
    #     pool.sort_values("projected_points", ascending=False)
    #     .head(50).reset_index(drop=True)
    # )
    # top_players.insert(0, "rank", top_players.index + 1)

    captains = prepare_recommendations(
        pool, calculate_captain_score(pool), CAPTAIN_COUNT
    )
    # captains = (
    #     pool.sort_values("projected_points", ascending=False)
    #     .head(10).reset_index(drop=True)
    # )
    # captains.insert(0, "rank", captains.index + 1)

    value_pool = pool[pool["price"] <= VALUE_MAX_PRICE].copy()
    
    value_picks = prepare_recommendations(value_pool, calculate_value_score(value_pool),VALUE_COUNT)
    # value_picks = (
    #     pool[pool["price"] <= VALUE_MAX_PRICE]
    #     .sort_values("value", ascending=False)
    #     .head(20).reset_index(drop=True)
    # )
    # value_picks.insert(0, "rank", value_picks.index + 1)

    differential_pool = pool[
        (pool["selected_by_percent"] >= DIFF_MIN_OWNERSHIP) &
        (pool["selected_by_percent"] < DIFF_MAX_OWNERSHIP)
        ].copy()
    
    differentials = prepare_recommendations(
        differential_pool, calculate_differential_score(differential_pool),DIFFERENTIAL_COUNT
    )
    # differentials = (
    #     pool[
    #         (pool["selected_by_percent"] >= DIFF_MIN_OWNERSHIP)  &
    #         (pool["selected_by_percent"] <= DIFF_MAX_OWNERSHIP)
    #     ]
    #     .sort_values("projected_points", ascending=False)
    #     .head(20).reset_index(drop=True)
    # )
    # differentials.insert(0, "rank", differentials.index + 1)
    
    outputs = {
        "top_players.csv" : (top_players, "TOP PROJECTED PLAYERS"),
        "captain_recommendations.csv":(captains, "CAPTAIN RECOMMENDATIONS"),
        "value_picks.csv":(value_picks, f"VALUE PICKS (<= £{VALUE_MAX_PRICE}m)"),
        "differentials.csv":(differentials, f"DIFFERENTIALS PICKS (< {DIFF_MAX_OWNERSHIP}% owned)"),    
    }
    
    for filename, (data, title) in outputs.items():
        output_path = (PROCESSED_DIR / filename)
        data.to_csv(output_path, index=False)
        show(data, title)
        
    print(f"\nSaved all recommendation files to {output_path}")
    print("\n" + "=" * 80)
    print("All recommendation files generated successfully.")
    print("=" * 80)

if __name__ == "__main__":
    main()
