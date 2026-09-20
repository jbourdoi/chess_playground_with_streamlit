# src/chess_app/presentation/streamlit/components/styles.py

from pathlib import Path

import streamlit as st

_CSS_DIRECTORY = Path(__file__).resolve().parent.parent / "static" / "css"


def _load_css(filename: str) -> None:
    """Load one CSS file into the Streamlit page."""
    path = _CSS_DIRECTORY / filename

    if not path.is_file():
        raise FileNotFoundError(f"CSS file not found: {path}")

    css = path.read_text(encoding="utf-8")

    st.markdown(
        f"<style>\n{css}\n</style>",
        unsafe_allow_html=True,
    )


def render_styles() -> None:
    """Load all application CSS files."""
    filenames = (
        "layout.css",
        "header.css",
        "messages.css",
        "players.css",
        "status.css",
        "board.css",
        "promotion.css",
        "controls.css",
        "history.css",
    )

    for filename in filenames:
        _load_css(filename)
