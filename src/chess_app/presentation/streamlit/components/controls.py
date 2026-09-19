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
    st.markdown("### Actions")

    if game.status == "in_progress":
        st.button(
            "⏸ Suspend",
            key=f"suspend-{game.game_id}",
            on_click=on_suspend,
        )

    elif game.status == "suspended":
        st.button(
            "▶ Resume",
            key=f"resume-{game.game_id}",
            on_click=on_resume,
        )
