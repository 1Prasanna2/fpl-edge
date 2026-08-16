import requests
import json 
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://fantasy.premierleague.com/api"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; FPLEdgeProject/1.0)"}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def fetch_json(url: str) -> dict:
    """Fetch JSON data from a URL with error handling."""
    logger.info(f"Fetching: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to fetch {url}: {e}")


def save_json(data: dict, filename: str) -> None:
    """Save JSON data to a file."""
    path = RAW_DIR / filename
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved: {path}")
    except IOError as e:
        raise IOError(f"Failed to save {path}: {e}")


def main():
    """Fetch current season data (bootstrap + fixtures)."""
    logger.info("Starting data fetch pipeline")

    # Fetch bootstrap (players, teams, events)
    bootstrap = fetch_json(f"{BASE_URL}/bootstrap-static/")
    save_json(
        bootstrap, "bootstrap_static.json"
    )  # Note: underscore to match build_features.py

    # Fetch fixtures
    fixtures = fetch_json(f"{BASE_URL}/fixtures/")
    save_json(fixtures, "fixtures.json")

    player_count = len(bootstrap.get("elements", []))
    team_count = len(bootstrap.get("teams", []))
    fixture_count = len(fixtures)

    logger.info(
        f"Successfully fetched {player_count} players, "
        f"{team_count} teams, {fixture_count} fixtures"
    )


if __name__ == "__main__":
    main()
