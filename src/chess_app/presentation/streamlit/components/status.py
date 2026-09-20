# src/chess_app/presentation/streamlit/components/status.py

from __future__ import annotations

import streamlit as st

from chess_app.application.state import GameState


def render_game_status(game: GameState) -> None:
    """Render the current game status as a single card."""
    in_progress = game.status == "in_progress"
    turn = _color_label(game.turn)

    lines = [
        f'<div class="game-status-value">{_status_label(game.status)}</div>'
    ]

    if in_progress:
        lines.append(f'<div class="game-turn">{turn} to move</div>')

    if in_progress and game.in_check:
        lines.append(f'<div class="game-check">{turn} is in check</div>')

    st.html(
        f'<div class="game-status game-status--{_tone(game.status)}">'
        + "".join(lines)
        + "</div>"
    )


def _tone(status: str) -> str:
    """Return the CSS modifier used to colour the status dot."""
    if status == "in_progress":
        return "live"

    if status == "suspended":
        return "paused"

    return "over"


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
