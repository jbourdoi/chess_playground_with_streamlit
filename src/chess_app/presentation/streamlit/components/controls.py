# src/chess_app/presentation/streamlit/components/controls.py

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from chess_app.application.state import GameState


def render_controls(
    game: GameState,
    on_suspend: Callable[[], None],
    on_resume: Callable[[], None],
) -> None:
    """Render game controls."""
    if game.status not in {"in_progress", "suspended"}:
        return

    with st.container(key="game_controls"):
        if game.status == "in_progress":
            st.button(
                "Suspend",
                key=f"suspend-{game.game_id}",
                on_click=on_suspend,
                icon=":material/pause:",
            )
        else:
            st.button(
                "Resume",
                key=f"resume-{game.game_id}",
                on_click=on_resume,
                icon=":material/play_arrow:",
            )
