from textwrap import dedent
import streamlit as st


def inject_theme():
    """Inject shared FPL Edge styling (theme-agnostic, light + dark)."""

    st.markdown(
        dedent("""
        <style>

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1500px;
        }

        .fpl-hero-intro { margin-bottom: 1.25rem; }

        .fpl-hero-kicker {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: color-mix(in srgb, var(--text-color) 45%, transparent);
            margin-bottom: 0.35rem;
        }

        .fpl-hero-title {
            font-size: 2.35rem;
            font-weight: 850;
            letter-spacing: -0.04em;
            margin: 0;
            color: var(--text-color);
        }

        .fpl-hero-subtitle {
            margin-top: 0.45rem;
            color: color-mix(in srgb, var(--text-color) 58%, transparent);
            font-size: 0.98rem;
        }

        .fpl-card {
            --accent: var(--primary-color);
            position: relative;
            height: 390px;
            padding: 20px;
            border-radius: 22px;
            background:
                radial-gradient(
                    circle at 80% 18%,
                    color-mix(in srgb, var(--text-color) 8%, transparent),
                    transparent 30%
                ),
                linear-gradient(
                    145deg,
                    var(--secondary-background-color),
                    var(--background-color)
                );
            border: 1px solid color-mix(in srgb, var(--text-color) 8%, transparent);
            box-shadow: 0 18px 45px rgba(0, 0, 0, 0.28);
            overflow: hidden;
            transition:
                transform 0.18s ease,
                border-color 0.18s ease,
                box-shadow 0.18s ease;
            margin-bottom: 0.5rem;
        }

        .fpl-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(
                150deg,
                color-mix(in srgb, var(--accent) 55%, var(--secondary-background-color)),
                color-mix(in srgb, var(--accent) 30%, var(--secondary-background-color))
            );
            opacity: 0;
            transition: opacity 0.25s ease;
            pointer-events: none;
        }

        .fpl-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent);
            box-shadow:
                0 24px 60px color-mix(in srgb, var(--text-color) 25%, transparent),
                0 6px 28px color-mix(in srgb, var(--accent) 25%, transparent);
        }

        .fpl-card:hover::before { opacity: 1; }

        .fpl-card::after {
            content: "";
            position: absolute;
            width: 120px;
            height: 120px;
            right: -40px;
            bottom: -45px;
            border-radius: 999px;
            background: color-mix(in srgb, var(--text-color) 3%, transparent);
        }

        .fpl-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .fpl-card-label {
            font-size: 0.72rem;
            font-weight: 750;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: color-mix(in srgb, var(--text-color) 52%, transparent);
        }

        .fpl-card-icon { font-size: 1.35rem; }

        .fpl-player-image {
            position: absolute;
            right: -12px;
            bottom: 52px;
            width: 72%;
            height: 285px;
            object-fit: contain;
            object-position: bottom center;
            filter: drop-shadow(0 20px 28px rgba(0, 0, 0, 0.48));
            z-index: 2;
        }

        .fpl-player-glow {
            position: absolute;
            right: 20px;
            bottom: 72px;
            width: 220px;
            height: 220px;
            border-radius: 50%;
            background: radial-gradient(
                circle,
                color-mix(in srgb, var(--text-color) 8%, transparent),
                transparent 68%
            );
            z-index: 1;
        }

        .fpl-card-content { position: relative; z-index: 4; }

        .fpl-card-player {
            margin-top: 0.8rem;
            font-size: 1.25rem;
            font-weight: 850;
            letter-spacing: -0.025em;
            color: var(--text-color);
            max-width: 72%;
        }

        .fpl-card-meta {
            margin-top: 0.2rem;
            font-size: 0.74rem;
            color: color-mix(in srgb, var(--text-color) 48%, transparent);
            max-width: 70%;
        }

        .fpl-score-label {
            margin-top: 0.8rem;
            font-size: 0.60rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: color-mix(in srgb, var(--text-color) 40%, transparent);
        }

        .fpl-score {
            margin-top: 0.05rem;
            font-size: 2.65rem;
            line-height: 1;
            font-weight: 900;
            letter-spacing: -0.05em;
            color: var(--text-color);
        }

        .fpl-reason {
            margin-top: 0.5rem;
            font-size: 0.74rem;
            color: color-mix(in srgb, var(--text-color) 55%, transparent);
        }

        .fpl-card-bottom {
            position: absolute;
            left: 20px;
            right: 20px;
            bottom: 18px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            gap: 1rem;
            z-index: 5;
        }

        .fpl-card-bottom::before {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            top: -10px;
            height: 1px;
            background: color-mix(in srgb, var(--text-color) 7%, transparent);
        }

        .fpl-stat { display: flex; flex-direction: column; }

        .fpl-stat-label {
            font-size: 0.62rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: color-mix(in srgb, var(--text-color) 38%, transparent);
        }

        .fpl-stat-value {
            margin-top: 0.15rem;
            font-size: 0.9rem;
            font-weight: 700;
            color: var(--text-color);
        }

        .fpl-section-title {
            margin-top: 1.8rem;
            margin-bottom: 0.5rem;
            font-size: 1.3rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            color: var(--text-color);
        }

        .fpl-section-description {
            color: color-mix(in srgb, var(--text-color) 52%, transparent);
            font-size: 0.88rem;
            margin-bottom: 0.9rem;
        }   
        
        .fpl-dossier { overflow: hidden; margin-top: 1rem; }
        .fpl-dossier input[type="radio"] { display: none; }

        .fpl-dossier-tabs { display: flex; gap: .5rem; margin-bottom: 1rem; flex-wrap: wrap; }
        .fpl-dossier-tabs label {
            padding: .45rem 1rem; border-radius: 999px; cursor: pointer;
            border: 1px solid color-mix(in srgb, var(--text-color) 18%, transparent);
            color: color-mix(in srgb, var(--text-color) 70%, transparent);
            font-weight: 700; font-size: .85rem;
            transition: all .25s ease;
        }
        #hero-slide-1:checked ~ .fpl-dossier-tabs label[for="hero-slide-1"],
        #hero-slide-2:checked ~ .fpl-dossier-tabs label[for="hero-slide-2"],
        #hero-slide-3:checked ~ .fpl-dossier-tabs label[for="hero-slide-3"],
        #hero-slide-4:checked ~ .fpl-dossier-tabs label[for="hero-slide-4"] {
            border-color: var(--accent);
            color: var(--accent);
            background: color-mix(in srgb, var(--accent) 12%, transparent);
        }

        .fpl-dossier-slider { display: flex; width: 400%; transition: transform .65s cubic-bezier(.77, 0, .18, 1); }
        .fpl-dossier-slide { width: 25%; }
        #hero-slide-1:checked ~ .fpl-dossier-slider { transform: translateX(0); }
        #hero-slide-2:checked ~ .fpl-dossier-slider { transform: translateX(-25%); }
        #hero-slide-3:checked ~ .fpl-dossier-slider { transform: translateX(-50%); }
        #hero-slide-4:checked ~ .fpl-dossier-slider { transform: translateX(-75%); }

        /* category-colored card background */
        .fpl-dossier-card {
            margin-right: 1.5rem;
            border-radius: 22px;
            padding: 1.75rem;
            background: linear-gradient(
                150deg,
                color-mix(in srgb, var(--accent) 22%, var(--secondary-background-color)),
                color-mix(in srgb, var(--accent) 7%, var(--background-color))
            );
            border: 1px solid color-mix(in srgb, var(--accent) 30%, transparent);
        }

        .fpl-dossier-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
        .fpl-dossier-name { font-size: 1.8rem; font-weight: 850; color: var(--text-color); }
        .fpl-dossier-sub { color: color-mix(in srgb, var(--text-color) 55%, transparent); font-size: .85rem; margin-top: .25rem; }
        .fpl-dossier-scorebox { text-align: right; }
        .fpl-dossier-scorenum { font-size: 2.6rem; font-weight: 900; line-height: 1; }
        .fpl-dossier-scorecap { margin-top: .2rem; font-size: .68rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: color-mix(in srgb, var(--text-color) 60%, transparent); }
        .fpl-dossier-verdict { margin-top: .9rem; font-size: .92rem; font-weight: 600; color: color-mix(in srgb, var(--accent) 65%, var(--text-color)); }

        .fpl-dossier-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: .75rem; margin-top: 1.25rem; }
        .fpl-dossier-tile {
            border-radius: 14px; padding: .7rem .8rem;
            background: color-mix(in srgb, var(--background-color) 45%, transparent);
            border: 1px solid color-mix(in srgb, var(--text-color) 6%, transparent);
        }
        .fpl-dossier-tile-label { font-size: .6rem; letter-spacing: .1em; text-transform: uppercase; color: color-mix(in srgb, var(--text-color) 45%, transparent); }
        .fpl-dossier-tile-value { margin-top: .25rem; font-weight: 800; color: var(--text-color); font-size: 1.05rem; }

        .fpl-dossier-bars { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-top: 1.25rem; }
        .fpl-dossier-bar-track { height: 6px; border-radius: 999px; background: color-mix(in srgb, var(--text-color) 12%, transparent); margin-top: .45rem; overflow: hidden; }
        .fpl-dossier-bar-fill { height: 100%; border-radius: 999px; background: var(--accent); }
        .fpl-dossier-bar-value { margin-top: .35rem; font-weight: 800; font-size: .9rem; color: var(--text-color); }

        .fpl-dossier-news { margin-top: 1.1rem; font-size: .85rem; color: color-mix(in srgb, var(--text-color) 60%, transparent); }

        @media (max-width: 900px) {
            .fpl-dossier-grid { grid-template-columns: repeat(2, 1fr); }
            .fpl-dossier-bars { grid-template-columns: 1fr; }
        }

        </style>
        """),
        unsafe_allow_html=True,
    )
