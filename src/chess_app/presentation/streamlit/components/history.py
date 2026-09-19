# src/chess_app/presentation/streamlit/components/history.py

from __future__ import annotations

import streamlit as st

from chess_app.application.state import GameState


def render_move_history(game: GameState) -> None:
    """Render the move history."""
    st.markdown("### History")

    if not game.moves:
        st.caption("No moves played.")
        return

    rows: list[str] = []

    for index in range(0, len(game.moves), 2):
        number = index // 2 + 1

        white_move = game.moves[index].uci

        black_move = ""

        if index + 1 < len(game.moves):
            black_move = game.moves[index + 1].uci

        rows.append(
            '<div class="move-row">'
            f'<span class="move-number">{number}.</span>'
            f"<span>{white_move}</span>"
            f"<span>{black_move}</span>"
            "</div>"
        )

    st.markdown(
        '<div class="move-history">' + "".join(rows) + "</div>",
        unsafe_allow_html=True,
    )
