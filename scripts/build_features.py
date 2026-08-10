import json
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_json(filename):
    with open(RAW_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    bootstrap = load_json("bootstrap-static.json")
    fixtures_raw = load_json("fixtures.json")

    players = pd.json_normalize(bootstrap["elements"])
    teams = pd.json_normalize(bootstrap["teams"])
    element_types = pd.json_normalize(bootstrap["element_types"])
    events = pd.json_normalize(bootstrap["events"])
    fixtures = pd.json_normalize(fixtures_raw)
    
    team_map = teams.set_index("id")["name"].to_dict()
    team_short_map = teams.set_index("id")["short_name"].to_dict()
    
    if "singular_name_short" in element_types.columns:
        position_map = element_types.set_index("id")["singular_name_short"].to_dict()
    else:
        position_map = element_types.set_index("id")["singular_name"].to_dict()
    
    next_gw = None
    
    for _,row in events.iterrows():
        if row.get("is_next") or row.get("is_current"):
            next_gw = row.get("id")
            break
    
    if next_gw is None:
        next_gw = int(events["id"].max()) + 1 if len(events) > 0 else 1
    
    print(f"Next Gameweek: {next_gw}")
    
    numeric_columns = [
        "form","points_per_game","total_points",
        "minutes","goals_scored","assists",
        "ict_index","influence","creativity",
        "threat","selected_by_percent","chance_of_playing_next_round","now_cost" 
    ]
    
    for col in numeric_columns:
        if col in players.columns:
            players[col] = pd.to_numeric(players[col], errors="coerce")
            
    if "now_cost" in players.columns:
        players["price"] = players["now_cost"] / 10
    else:
        players["price"] = None
    
    players["team_name"] = players["team"].map(team_map)
    players["team_short_name"] = players["team"].map(team_short_map)
    players["position"] = players["element_type"].map(position_map)
    
    def get_next_fixture(team_id):
        if "event" not in fixtures.columns:
            return pd.Series({
                "opponent": None,
                "home":None,
                "fixture_difficulty":None
            })
        
        
        mask = (
            (fixtures["event"] == next_gw) &
            (
                (fixtures.get("team_h") == team_id) |
                (fixtures.get("team_a") == team_id)
            )
        )
        
        subset = fixtures[mask]
        
        if subset.empty:
            mask = (
                (fixtures.get("event") >= next_gw) &
                (
                    (fixtures.get("team_h") == team_id) |
                    (fixtures.get("team_a") == team_id)
                ) & 
                (fixtures.get("finished") == False)
            )
            subset = fixtures[mask].sort_values("event")
            
        if subset.empty:
            return pd.Series({
                "opponent": None,
                "home":None,
                "fixture_difficulty":None
            })
        
        row = subset.iloc[0]
        home = row.get("team_h") == team_id
        opponent_id = row.get("team_a") if home else row.get("team_h")  
        
        return pd.Series({
            "opponent": team_short_map.get(opponent_id),
            "home": home,
            "fixture_difficulty": row.get("difficulty")
        })
        
    fixture_info = players["team"].apply(get_next_fixture)
    players = pd.concat([players, fixture_info], axis=1)
    
    if "chance_of_playing_next_round" in players.columns:
        players["availability"] = players["chance_of_playing_next_round"].fillna(100) / 100
    else:
        players["availability"] = 1.0
        
    if players["fixture_difficulty"].notna().any():
        players["fixture_adjustment"] = 1 + (3 - players["fixture_difficulty"].fillna(3))
    else:
        players["fixture_adjustment"] = 1.0
        
        
    players["form"] = players.get("form", pd.Series([0] * len(players))).fillna(0)
    players["points_per_game"] = players.get("points_per_game", pd.Series([0] * len(players))).fillna(0)
    players["ict_index"] = players.get("ict_index", pd.Series([0] * len(players))).fillna(0)
    
    players["base_projection"] = (
        players["form"] * 0.5 + 
        players["points_per_game"] * 0.3 +
        players["ict_index"] * 0.2
    )
    
    players["projected_points"] = (
        players["base_projection"] * 
        players["availability"] * 
        players["fixture_adjustment"]
    )
    
    players["value"] = players["projected_points"] / players["price"].replace(0, pd.NA)
    
    final_columns = [
        "id","web_name","team_name","team_short_name","position","price","selected_by_percent",
        "total_points","minutes","goals_scored","assists","form","points_per_game","ict_index",
        "influence","creativity","threat","status","news","chance_of_playing_next_round","availability",
        "opponent","home","fixture_difficulty","fixture_adjustment","base_projection","projected_points","value"
    ]
    
    existing_columns = [col for col in final_columns if col in players.columns]
    
    output_df = players[existing_columns].copy()
    
    output_df = output_df.sort_values(by="projected_points", ascending=False)
    
    output_path = OUT_DIR / "projections.csv"
    output_df.to_csv(output_path, index=False)
    
    print(f"Saved projections to: {output_path}")
    print(output_df.head())
    
if __name__ == "__main__":
    main()