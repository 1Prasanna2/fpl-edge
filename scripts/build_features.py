import json
import logging
import pandas as pd
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT/"data"/"raw"
OUT_DIR = PROJECT_ROOT/"data"/"processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MINUTES_PER_SEASON = 3420
MIN_MINUTES_FOR_PRIOR = 900
MIN_MINUTES_SHARE = 0.35
PRIORS_URL = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2024-25/cleaned_players.csv"

POSITION_PRIORS = {"GKP": 2.2, "DEF": 3.2, "MID": 4.2, "FWD": 4.0}

NUMERIC_COLUMNS = [
    "form",
    "points_per_game",
    "total_points",
    "minutes",
    "goals_scored",
    "assists",
    "ict_index",
    "influence",
    "creativity",
    "threat",
    "selected_by_percent",
    "chance_of_playing_next_round",
    "now_cost",
]

FINAL_COLUMNS = [
    "id",
    "web_name",
    "photo",
    "team_name",
    "team_short_name",
    "position",
    "price",
    "selected_by_percent",
    "total_points",
    "minutes",
    "goals_scored",
    "assists",
    "form",
    "points_per_game",
    "ict_index",
    "influence",
    "creativity",
    "threat",
    "status",
    "news",
    "chance_of_playing_next_round",
    "availability",
    "opponent",
    "home",
    "fixture_difficulty",
    "fixture_adjustment",
    "base_projection",
    "projected_points",
    "value",
]

def load_json(filename):
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {filename}: {e}")


def get_next_gameweek(events: pd.DataFrame) -> int:
    """Determine the next gameweek from events data."""
    if events.empty:
        return 1

    next_event = events[events["is_next"] | events["is_current"]]
    if not next_event.empty:
        return int(next_event.iloc[0]["id"])

    return int(events["id"].max()) + 1


def build_fixture_lookup(
    fixtures: pd.DataFrame, team_short_map: dict, next_gw: int
) -> dict:
    """Build a team_id -> fixture info mapping (vectorized, fast)."""
    lookup = {}

    if "event" not in fixtures.columns or fixtures.empty:
        return lookup

    for team_id in team_short_map.keys():
        # Try current/next gameweek first
        mask = (fixtures["event"] == next_gw) & (
            (fixtures["team_h"] == team_id) | (fixtures["team_a"] == team_id)
        )
        subset = fixtures[mask]

        # Fallback to future unfinished fixtures
        if subset.empty:
            mask = (
                (fixtures["event"] >= next_gw)
                & ((fixtures["team_h"] == team_id) | (fixtures["team_a"] == team_id))
                & (fixtures["finished"] == False)
            )
            subset = fixtures[mask].sort_values("event")

        if subset.empty:
            lookup[team_id] = {
                "opponent": None,
                "home": None,
                "fixture_difficulty": None,
            }
        else:
            row = subset.iloc[0]
            home = row["team_h"] == team_id
            opponent_id = row["team_a"] if home else row["team_h"]

            lookup[team_id] = {
                "opponent": team_short_map.get(opponent_id),
                "home": home,
                "fixture_difficulty": row.get("difficulty"),
            }

    return lookup


def compute_projections(players: pd.DataFrame) -> pd.DataFrame:
    """Compute projected points using priors, availability, and fixtures."""
    # Load historical priors
    try:
        prior = pd.read_csv(PRIORS_URL)
        logger.info("Loaded historical priors")
    except Exception as e:
        logger.warning(f"Priors download failed: {e}")
        prior = pd.DataFrame()

    players["prior_pp90"] = pd.NA

    needed = {"total_points", "minutes", "first_name", "second_name"}
    if not prior.empty and needed.issubset(prior.columns):
        prior["minutes"] = pd.to_numeric(prior["minutes"], errors="coerce").clip(
            lower=MIN_MINUTES_FOR_PRIOR
        )
        prior["rate"] = (
            pd.to_numeric(prior["total_points"], errors="coerce")
            / prior["minutes"]
            * 90
        ).clip(0.5, 10)

        # Damp by minutes share
        prior["minutes_share"] = (prior["minutes"] / MINUTES_PER_SEASON).clip(
            MIN_MINUTES_SHARE, 1.0
        )
        prior["rate"] = (prior["rate"] * prior["minutes_share"] ** 0.5).clip(0.5, 10)

        def make_key(df):
            return (
                df["first_name"].astype(str).str.strip().str.lower()
                + "|"
                + df["second_name"].astype(str).str.strip().str.lower()
            )

        lookup = prior.assign(key=make_key(prior)).groupby("key")["rate"].mean()
        players["prior_pp90"] = make_key(players).map(lookup)

    # Fill unmapped with position priors
    players["prior_pp90"] = players["prior_pp90"].fillna(
        players["position"].map(POSITION_PRIORS)
    )

    # Compute final projection
    players["base_projection"] = players["prior_pp90"]
    players["projected_points"] = (
        players["base_projection"]
        * players["availability"]
        * players["fixture_adjustment"]
    ).round(2)

    players["value"] = players["projected_points"] / players["price"].replace(0, pd.NA)

    return players


def main():
    logger.info("Starting feature build pipeline")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load raw data
    bootstrap = load_json("bootstrap-static.json")
    fixtures_raw = load_json("fixtures.json")

    # Validate required keys
    for key in ["elements", "teams", "element_types", "events"]:
        if key not in bootstrap:
            raise ValueError(f"Missing required key in bootstrap: {key}")

    players = pd.json_normalize(bootstrap["elements"])
    teams = pd.json_normalize(bootstrap["teams"])
    element_types = pd.json_normalize(bootstrap["element_types"])
    events = pd.json_normalize(bootstrap["events"])
    fixtures = pd.json_normalize(fixtures_raw)

    logger.info(
        f"Loaded {len(players)} players, {len(teams)} teams, {len(fixtures)} fixtures"
    )

    # Build mappings
    team_map = teams.set_index("id")["name"].to_dict()
    team_short_map = teams.set_index("id")["short_name"].to_dict()

    position_col = (
        "singular_name_short"
        if "singular_name_short" in element_types.columns
        else "singular_name"
    )
    position_map = element_types.set_index("id")[position_col].to_dict()

    # Determine next gameweek
    next_gw = get_next_gameweek(events)
    logger.info(f"Next gameweek: {next_gw}")

    # Convert numeric columns
    for col in NUMERIC_COLUMNS:
        if col in players.columns:
            players[col] = pd.to_numeric(players[col], errors="coerce")

    # Derive price
    if "now_cost" in players.columns:
        players["price"] = players["now_cost"] / 10
    else:
        players["price"] = None

    # Map team and position names
    players["team_name"] = players["team"].map(team_map)
    players["team_short_name"] = players["team"].map(team_short_map)
    players["position"] = players["element_type"].map(position_map)

    # Build fixture info (vectorized)
    fixture_lookup = build_fixture_lookup(fixtures, team_short_map, next_gw)
    fixture_info = players["team"].map(fixture_lookup).apply(pd.Series)
    players = pd.concat([players, fixture_info], axis=1)

    # Compute availability
    if "chance_of_playing_next_round" in players.columns:
        players["availability"] = (
            players["chance_of_playing_next_round"].fillna(100) / 100
        )
    else:
        players["availability"] = 1.0

    # Compute fixture adjustment
    if players["fixture_difficulty"].notna().any():
        players["fixture_adjustment"] = 1 + (
            3 - players["fixture_difficulty"].fillna(3)
        )
    else:
        players["fixture_adjustment"] = 1.0

    # Fill NaN in key columns
    for col in ["form", "points_per_game", "ict_index"]:
        if col in players.columns:
            players[col] = players[col].fillna(0)

    # Compute projections
    players = compute_projections(players)

    # Select and sort final columns
    existing_columns = [col for col in FINAL_COLUMNS if col in players.columns]
    output_df = players[existing_columns].copy()
    output_df = output_df.sort_values("projected_points", ascending=False)

    # Save
    output_path = OUT_DIR / "projections.csv"
    output_df.to_csv(output_path, index=False)

    logger.info(f"Saved {len(output_df)} players to {output_path}")
    logger.info(f"Top 5: {output_df['web_name'].head().tolist()}")


if __name__ == "__main__":
    main()
