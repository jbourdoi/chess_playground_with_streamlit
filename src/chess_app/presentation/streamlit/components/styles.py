# src/chess_app/presentation/streamlit/components/styles.py

import streamlit as st


def render_styles() -> None:
    """Inject the visual styles used by the application."""
    st.markdown(
        """
        <style>

        /* =========================================================
           Board
           ========================================================= */

        .board-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }

        .board-coordinate {
            text-align: center;
            font-size: 0.72rem;
            opacity: 0.6;
        }

        [class*="st-key-board-"] {
            width: 100%;
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-board-"]
        div[data-testid="stButton"] {
            width: 100%;
            margin: 0 !important;
            padding: 0 !important;
        }

        [class*="st-key-board-"]
        div[data-testid="stButton"] > button {
            width: 100%;
            aspect-ratio: 1 / 1;

            min-height: 0 !important;
            height: auto !important;

            margin: 0 !important;
            padding: 0 !important;

            border: 0 !important;
            border-radius: 0 !important;

            font-size: clamp(
                1.8rem,
                4vw,
                3.8rem
            );

            line-height: 1;

            transition:
                filter 0.1s ease,
                box-shadow 0.1s ease;
        }

        [class*="st-key-board-"]
        div[data-testid="stButton"] > button:hover {
            filter: brightness(1.08);
        }

        /* =========================================================
           Dark squares
           ========================================================= */

        .st-key-board-b1
        button,
        .st-key-board-d1
        button,
        .st-key-board-f1
        button,
        .st-key-board-h1
        button,

        .st-key-board-a2
        button,
        .st-key-board-c2
        button,
        .st-key-board-e2
        button,
        .st-key-board-g2
        button,

        .st-key-board-b3
        button,
        .st-key-board-d3
        button,
        .st-key-board-f3
        button,
        .st-key-board-h3
        button,

        .st-key-board-a4
        button,
        .st-key-board-c4
        button,
        .st-key-board-e4
        button,
        .st-key-board-g4
        button,

        .st-key-board-b5
        button,
        .st-key-board-d5
        button,
        .st-key-board-f5
        button,
        .st-key-board-h5
        button,

        .st-key-board-a6
        button,
        .st-key-board-c6
        button,
        .st-key-board-e6
        button,
        .st-key-board-g6
        button,

        .st-key-board-b7
        button,
        .st-key-board-d7
        button,
        .st-key-board-f7
        button,
        .st-key-board-h7
        button,

        .st-key-board-a8
        button,
        .st-key-board-c8
        button,
        .st-key-board-e8
        button,
        .st-key-board-g8
        button {
            background: #b58863 !important;
        }

        /* =========================================================
           Light squares
           ========================================================= */

        .st-key-board-a1
        button,
        .st-key-board-c1
        button,
        .st-key-board-e1
        button,
        .st-key-board-g1
        button,

        .st-key-board-b2
        button,
        .st-key-board-d2
        button,
        .st-key-board-f2
        button,
        .st-key-board-h2
        button,

        .st-key-board-a3
        button,
        .st-key-board-c3
        button,
        .st-key-board-e3
        button,
        .st-key-board-g3
        button,

        .st-key-board-b4
        button,
        .st-key-board-d4
        button,
        .st-key-board-f4
        button,
        .st-key-board-h4
        button,

        .st-key-board-a5
        button,
        .st-key-board-c5
        button,
        .st-key-board-e5
        button,
        .st-key-board-g5
        button,

        .st-key-board-b6
        button,
        .st-key-board-d6
        button,
        .st-key-board-f6
        button,
        .st-key-board-h6
        button,

        .st-key-board-a7
        button,
        .st-key-board-c7
        button,
        .st-key-board-e7
        button,
        .st-key-board-g7
        button,

        .st-key-board-b8
        button,
        .st-key-board-d8
        button,
        .st-key-board-f8
        button,
        .st-key-board-h8
        button {
            background: #f0d9b5 !important;
        }

        /* =========================================================
           Coordinates
           ========================================================= */

        .board-coordinate {
            text-align: center;
            font-size: 0.72rem;
            opacity: 0.6;
        }

        /* =========================================================
           Other components
           ========================================================= */

        .player-card {
            padding: 0.7rem 0.9rem;
            margin-bottom: 0.7rem;
            border: 1px solid
                rgba(128, 128, 128, 0.25);
            border-radius: 0.6rem;
        }

        .player-name {
            font-size: 1.05rem;
            font-weight: 600;
        }

        .player-type {
            font-size: 0.78rem;
            opacity: 0.65;
        }

        .game-info {
            padding: 0.7rem 0.9rem;
            margin: 0.8rem 0;
            border-radius: 0.6rem;
            background: rgba(128, 128, 128, 0.08);
        }

        .game-info-label {
            font-size: 0.75rem;
            opacity: 0.65;
        }

        .game-info-value {
            font-size: 1rem;
            font-weight: 600;
        }

        .move-history {
            max-height: 15rem;
            overflow-y: auto;
            padding: 0.5rem 0.2rem;
        }

        .move-row {
            display: grid;
            grid-template-columns: 2rem 1fr 1fr;
            gap: 0.5rem;
            padding: 0.2rem 0;
            font-family: monospace;
        }

        .move-number {
            opacity: 0.55;
        }

        .promotion-box {
            padding: 0.7rem;
            margin: 0.8rem 0;
            border: 1px solid
                rgba(128, 128, 128, 0.25);
            border-radius: 0.6rem;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
