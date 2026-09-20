# src/chess_app/presentation/streamlit/components/history.py

from __future__ import annotations

from html import escape

import streamlit as st

from chess_app.application.state import GameState


def render_move_history(game: GameState) -> None:
    """Render the move history (oldest first, scrolled to the latest move)."""
    if not game.moves:
        body = '<p class="game-history-empty">No moves played yet.</p>'
    else:
        last_index = len(game.moves) - 1
        rows: list[str] = []

        for index in range(0, len(game.moves), 2):
            cells = []

            for offset in (0, 1):
                move_index = index + offset

                if move_index >= len(game.moves):
                    cells.append("<span></span>")
                    continue

                css_class = "move-uci"

                if move_index == last_index:
                    css_class += " move-uci--last"

                cells.append(
                    f'<span class="{css_class}">'
                    f"{escape(game.moves[move_index].uci)}</span>"
                )

            rows.append(
                '<div class="move-entry">'
                f'<span class="move-number">{index // 2 + 1}.</span>'
                + "".join(cells)
                + "</div>"
            )

        # .move-history is the scroller; it holds a single child (.move-list)
        body = (
            '<div class="move-history">'
            '<div class="move-list">' + "".join(rows) + "</div>"
            "</div>"
        )

    st.html(
        '<div class="game-history">'
        '<div class="game-history-title">Moves</div>'
        f"{body}"
        "</div>"
    )
