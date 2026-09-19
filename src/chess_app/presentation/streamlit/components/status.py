# src/chess_app/presentation/streamlit/components/status.py

from __future__ import annotations

import streamlit as st

from chess_app.application.state import GameState


def render_game_status(game: GameState) -> None:
    """Render the current game status."""
    status = _status_label(game.status)
    turn = _color_label(game.turn)

    st.markdown(
        '<div class="game-info">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="game-info-label">Status</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="game-info-value">{status}</div>',
        unsafe_allow_html=True,
    )

    if game.status == "in_progress":
        st.markdown(
            '<div class="game-info-label">Turn</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="game-info-value">{turn}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    if game.in_check and game.status == "in_progress":
        st.warning(
            f"{turn.capitalize()} are in check.",
            icon="⚠️",
        )


def _status_label(status: str) -> str:
    """Return a human-readable game status."""
    labels = {
        "in_progress": "In progress",
        "suspended": "Suspended",
        "white_won": "White wins",
        "black_won": "Black wins",
        "draw": "Draw",
    }

    return labels.get(status, status)


def _color_label(color: str) -> str:
    """Return a human-readable player color."""
    labels = {
        "white": "White",
        "black": "Black",
    }

    return labels.get(color, color)
