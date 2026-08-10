import requests
import json 
import time
from pathlib import Path

BASE_URL = "https://fantasy.premierleague.com/api"

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; FPLEdgeProject/1.0)"}

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def fetch_json(url):
    print(f"Fetching: {url}")
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()

def save_json(data, filename):
    path = RAW_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {path}")
    
def main():
    bootstrap = fetch_json(f"{BASE_URL}/bootstrap-static/")
    fixtures = fetch_json(f"{BASE_URL}/fixtures/")
    
    save_json(bootstrap, "bootstrap-static.json")
    save_json(fixtures, "fixtures.json")
    
    players = bootstrap.get("elements", [])
    
    top_players = sorted(
        players,
        key=lambda x: float(x.get("selected_by_percent") or 0),
        reverse = True
    )[:100]
    
    all_history = []
    
    for player in top_players:
        player_id = player.get("id")
        player_name = player.get("web_name")
        
        try:
            summary = fetch_json(f"{BASE_URL}/element-summary/{player_id}/")
            history = summary.get("history", [])
            
            for row in history:
                row["element"] = player_id
                row["player_name"] = player_name
            
            all_history.extend(history)
            
            print(f"Fetched history for {player_name}")
            
            time.sleep(1)
        
        except Exception as e:
            print(f"Failed to fetch history for {player_name}: {e}")
    
    save_json(all_history, "player_history_top100.json")


if __name__ == "__main__":
    main()
