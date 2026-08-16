from pathlib import Path
from textwrap import dedent

import pandas as pd
import streamlit as st
import base64

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PLAYER_ASSETS_DIR = PROJECT_ROOT / "app" / "assets" / "players"
SILHOUETTE_DIR = PROJECT_ROOT / "app" / "assets" / "silhouettes"


PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

CATEGORIES = [
    ("top_players.csv", "Best Overall", "🏆", "#f59e0b"),
    ("captain_recommendations.csv","Captain","👑","#a78bfa"),
    ("value_picks.csv", "Best Value", "💰", "#34d399"),
    ("differentials.csv", "Hidden Gem", "💎", "#38bdf8")
]


def load_recommendations(filename):
    """Load a recommendation CSV safely."""

    path = PROCESSED_DIR / filename

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

def image_to_data_uri(image_path):
    if not image_path.exists():
        return None
    
    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    
    return f"data:image/png;base64,{encoded}"


def _img_tag(uri, player, fallback=False):
    dim = ' style="opacity:.55"' if fallback else ""
    return f"""
        <div class="fpl-player-glow"></div>
        <img class="fpl-player-image" src="{uri}" alt="{player}"{dim}>
    """


def _silhouette_uri(row):
    """Position-based silhouette, falling back to default.png."""
    pos = str(row.get("position", "")).upper().strip()
    pos = {"GKP": "GK"}.get(pos, pos)  # FPL sometimes uses GKP

    for name in ([pos, "default"] if pos else ["default"]):
        uri = image_to_data_uri(SILHOUETTE_DIR / f"{name}.png")
        if uri:
            return uri
    return None


def build_image_html(row, player):
    #Actual Hero Card Photo
    pid = row.get("id")
    if pd.notna(pid):
        uri = image_to_data_uri(PLAYER_ASSETS_DIR / f"{int(pid)}.png")
        if uri:
            return _img_tag(uri, player)

    #Silhouettes
    uri = _silhouette_uri(row)
    return _img_tag(uri, player, fallback=True)

def _number(value, default=0.0):
    """Safely convert a value to float."""
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_edge_score(row):
    """
    Use the Edge Score when available.

    Falls back to recommendation_score if the newer recommendation engine is being used.
    """

    if "edge_score" in row.index:
        return _number(row["edge_score"])

    if "recommendation_score" in row.index:
        return _number(row["recommendation_score"])
    
    return None


def _reason_for(category, row):
    """One line of analysis explaining WHY this player earned the card."""
    own = _number(row.get("selected_by_percent", 0))
    value = _number(row.get("value", 0))
    proj = _number(row.get("projected_points", 0))
    opp = row.get("opponent", "-")

    if category == "Hidden Gem":
        return f"Only {own:.1f}% owned  · proj {proj:.1f}"
    if category == "Best Value":
        return f"{value:.1f} pts per £1m"
    if category == "Captain":
        return f"Proj {proj:.1f} vs {opp}"
    return f"Proj {proj:.1f} vs {opp}"

def _pick_unique_row(dataframe, picked_ids):
    """First row in this list whose player hasn't been picked yet."""
    if dataframe is None or dataframe.empty:
        return None
    for _, row in dataframe.iterrows():
        pid = row.get("id")
        if pd.isna(pid) or pid not in picked_ids:
            return row
    return dataframe.iloc[0]

def render_hero_card( row,category,icon,color):
    if row is None:
        st.html(dedent(f"""
        <div class="fpl-card" style="--accent:{color}; border-top:3px solid {color}">
            <div class="fpl-card-content">
                <div class="fpl-card-header">
                    <div class="fpl-card-label">{category}</div>
                    <div class="fpl-card-icon">{icon}</div>
                </div>
                <div class="fpl-card-player">No recommendation</div>
                <div class="fpl-card-meta">Recommendation data unavailable</div>
            </div>
        </div>
        """))

        return

    player_id = row.get("id")

    player = str(row.get("web_name", "Unknown Player"))

    team = str(row.get("team_short_name", "—"))

    position = str(row.get("position", "—"))

    projected = _number(row.get("projected_points", 0))

    edge_score = _get_edge_score(row)

    opponent = str(row.get("opponent", "—"))

    edge_html = f"{edge_score:.0f}" if edge_score is not None else "—"

    reason = _reason_for(category, row)

    image_html = build_image_html(row, player)

    st.html(dedent(f"""
        <div class="fpl-card" style="--accent:{color}; border-top:3px solid {color}">
        {image_html}
            <div class="fpl-card-content">

            <div class="fpl-card-header">

                <div class="fpl-card-label">
                    {category}
                </div>

                <div class="fpl-card-icon">
                    {icon}
                </div>

            </div>

            <div class="fpl-card-player">
                {player}
            </div>

            <div class="fpl-card-meta">
                {team} · {position}
            </div>

            <div class="fpl-score-label">
                FPL Edge Score
            </div>

            <div class="fpl-score" style="color:{color}">
                {edge_html}
            </div>
            <div style="color:#9aa4b2;font-size:12px;margin-top:8px;">
                ▸ {reason}
            </div>
            </div>
                
            <div class="fpl-card-bottom">

                <div class="fpl-stat">
                    <span class="fpl-stat-label">
                        Projected
                    </span>

                    <span class="fpl-stat-value">
                        {projected:.1f}
                    </span>
                </div>

                <div class="fpl-stat">
                    <span class="fpl-stat-label">
                        Next Fixture
                    </span>

                    <span class="fpl-stat-value">
                        {opponent}
                    </span>
                </div>

            </div>

        </div>
        """))


def render_hero_section():
    """
    Render the four primary FPL Edge recommendations.
    """
    frames = {file: load_recommendations(file) for file, _, _, _ in CATEGORIES}

    st.html(
        dedent("""
        <div class="fpl-hero-intro">
            <div class="fpl-hero-kicker">
                FPL Edge · Decision Engine
            </div>
            <h1 class="fpl-hero-title">
                See the Edge. Make the Move.
            </h1>
            <div class="fpl-hero-subtitle">
                Data-driven recommendations for your next
                Fantasy Premier League decision.
            </div>
        </div>
        """))

    st.html('<div class="fpl-section-title">This Week\'s Edge</div>')

    picked_ids = set()
    cards = []
    for file, category, icon, color in CATEGORIES:
        row = _pick_unique_row(frames[file], picked_ids)
        if row is not None and pd.notna(row.get("id")):
            picked_ids.add(row.get("id"))
        cards.append((row, category, icon, color))

    columns = st.columns(4)
    for col, (row, category, icon, color) in zip(columns, cards):
        with col:
            render_hero_card(row, category, icon, color)

TEAM_STADIUMS = {
    "ARS": "Emirates Stadium",
    "AVL": "Villa Park",
    "BOU": "Vitality Stadium",
    "BRE": "Gtech Community Stadium",
    "BHA": "Amex Stadium",
    "CHE": "Stamford Bridge",
    "CRY": "Selhurst Park",
    "EVE": "Hill Dickinson Stadium",
    "FUL": "Craven Cottage",
    "LEE": "Elland Road",
    "LIV": "Anfield",
    "MUN": "Old Trafford",
    "MCI": "Etihad Stadium",
    "NEW": "St James' Park",
    "NFO": "City Ground",
    "SUN": "Stadium of Light",
    "TOT": "Tottenham Hotspur Stadium",
    "WHU": "London Stadium",
    "WOL": "Molineux",
    "BUR": "Turf Moor",
}


def _stat_tile(label, value):
    return f"""
    <div class="fpl-dossier-tile">
        <div class="fpl-dossier-tile-label">{label}</div>
        <div class="fpl-dossier-tile-value">{value}</div>
    </div>
    """


def _pct_bar(label, value_pct, display):
    v = max(0.0, min(100.0, value_pct))
    return f"""
    <div class="fpl-dossier-bar">
        <div class="fpl-dossier-tile-label">{label}</div>
        <div class="fpl-dossier-bar-track">
            <div class="fpl-dossier-bar-fill" style="width:{v:.0f}%"></div>
        </div>
        <div class="fpl-dossier-bar-value">{display}</div>
    </div>
    """


def _slide_html(row, category, icon, color):
    name = str(row.get("web_name", "—"))
    team_short = str(row.get("team_short_name", "—"))
    team_full = str(row.get("team_name", team_short))
    stadium = TEAM_STADIUMS.get(team_short, "—")
    position = str(row.get("position", "—"))
    edge = _get_edge_score(row)
    edge_html = f"{edge:.0f}" if edge is not None else "—"
    home = "H" if bool(row.get("home", False)) else "A"
    opp = str(row.get("opponent", "—"))
    diff = row.get("fixture_difficulty")
    diff_html = f"{int(diff)}/5" if pd.notna(diff) else "—"
    chance = _number(row.get("chance_of_playing_next_round"), 100)
    owned = _number(row.get("selected_by_percent"))
    value = _number(row.get("value"))
    reason = _reason_for(category, row)

    news_raw = row.get("news")
    news = "" if news_raw is None or pd.isna(news_raw) else str(news_raw).strip()
    news = news or "No injury or rotation concerns reported."

    tiles = "".join(
        [
            _stat_tile("Price", f"£{_number(row.get('price')):.1f}m"),
            _stat_tile("Projected", f"{_number(row.get('projected_points')):.1f}"),
            _stat_tile("Form", f"{_number(row.get('form')):.1f}"),
            _stat_tile("Pts / Game", f"{_number(row.get('points_per_game')):.1f}"),
            _stat_tile("Goals", f"{_number(row.get('goals_scored')):.0f}"),
            _stat_tile("Assists", f"{_number(row.get('assists')):.0f}"),
            _stat_tile("ICT Index", f"{_number(row.get('ict_index')):.1f}"),
            _stat_tile("Value", f"{value:.2f}"),
            _stat_tile("Next Fixture", f"{home} vs {opp}"),
            _stat_tile("Fixture Diff.", diff_html),
        ]
    )

    bars = "".join(
        [
            _pct_bar("Ownership", owned, f"{owned:.1f}% owned"),
            _pct_bar("Chance of Playing", chance, f"{chance:.0f}% fit"),
        ]
    )

    return f"""
    <div class="fpl-dossier-slide">
        <div class="fpl-dossier-card" style="--accent:{color}; border-top:3px solid {color}">
            <div class="fpl-dossier-head">
                <div>
                    <div class="fpl-dossier-name">{name}</div>
                    <div class="fpl-dossier-sub">{team_full} · {position} · {stadium}</div>
                </div>
                <div class="fpl-dossier-scorebox">
                    <div class="fpl-dossier-scorenum" style="color:{color}">{edge_html}</div>
                    <div class="fpl-dossier-scorecap">{icon} {category}</div>
                </div>
            </div>
            <div class="fpl-dossier-verdict">▸ {reason}</div>
            <div class="fpl-dossier-grid">{tiles}</div>
            <div class="fpl-dossier-bars">{bars}</div>
            <div class="fpl-dossier-news">📰 {news}</div>
        </div>
    </div>
    """


def render_hero_details():
    """Sliding dossier section: deep info for the four hero players only."""
    frames = {file: load_recommendations(file) for file, _, _, _ in CATEGORIES}

    picked_ids, slides = set(), []
    for file, category, icon, color in CATEGORIES:
        row = _pick_unique_row(frames[file], picked_ids)
        if row is None:
            continue
        if pd.notna(row.get("id")):
            picked_ids.add(row.get("id"))
        slides.append((row, category, icon, color))

    if not slides:
        return

    st.html('<div class="fpl-section-title">Inside the Picks</div>')

    radios = "".join(
        f'<input type="radio" name="hero-slide" id="hero-slide-{i}"'
        + (" checked" if i == 1 else "")
        + ">"
        for i in range(1, len(slides) + 1)
    )
    labels = "".join(
        f'<label for="hero-slide-{i}" style="--accent:{color}">{icon} {row["web_name"]}</label>'
        for i, (row, _, icon, color) in enumerate(slides, start=1)
    )
    panels = "".join(
        _slide_html(row, category, icon, color) for row, category, icon, color in slides
    )

    st.html(dedent(f"""
    <div class="fpl-dossier">
        {radios}
        <div class="fpl-dossier-tabs">{labels}</div>
        <div class="fpl-dossier-slider">{panels}</div>
    </div>
    """))
