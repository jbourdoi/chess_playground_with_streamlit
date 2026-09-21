# src/chess_app/presentation/streamlit/components/controls.py

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from chess_app.application.state import GameState


def render_controls(
    game: GameState,
    on_suspend: Callable[[], None],
    on_resume: Callable[[], None],
    on_new_game_local: Callable[[], None] | None = None,
    on_new_game_ai: Callable[[], None] | None = None,
    on_engine_retry: Callable[[], None] | None = None,
) -> None:
    """Render game controls."""
    with st.container(key="game_controls"):
        col1, col2 = st.columns(2)
        with col1:
            if on_new_game_local:
                st.button(
                    "2 Players (Local)",
                    key=f"new-local-{game.game_id}",
                    on_click=on_new_game_local,
                    icon=":material/groups:",
                    use_container_width=True,
                )
        with col2:
            if on_new_game_ai:
                st.button(
                    "Vs IA",
                    key=f"new-ai-{game.game_id}",
                    on_click=on_new_game_ai,
                    icon=":material/smart_toy:",
                    use_container_width=True,
                )
            if on_engine_retry:
                st.button(
                    "Relancer l'IA",
                    key=f"engine-retry-{game.game_id}",
                    on_click=on_engine_retry,
                    icon=":material/refresh:",
                    use_container_width=True,
                )

        if game.status in {"in_progress", "suspended"}:
            if game.status == "in_progress":
                st.button(
                    "Suspend",
                    key=f"suspend-{game.game_id}",
                    on_click=on_suspend,
                    icon=":material/pause:",
                    use_container_width=True,
                )
            else:
                st.button(
                    "Resume",
                    key=f"resume-{game.game_id}",
                    on_click=on_resume,
                    icon=":material/play_arrow:",
                    use_container_width=True,
                )
