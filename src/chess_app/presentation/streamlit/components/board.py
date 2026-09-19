# src/chess_app/presentation/streamlit/components/board.py

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from chess_app.application.state import GameState


def render_board(
    game: GameState,
    selected_square: str | None,
    on_square_clicked: Callable[
        [str, tuple[str, ...]],
        None,
    ],
) -> None:
    """Render the responsive chess board."""
    pieces = {
        piece.square: piece
        for piece in game.board.pieces
    }

    legal_targets = _legal_targets(
        game.legal_moves,
        selected_square,
    )

    st.markdown(
        '<div class="board-title">Board</div>',
        unsafe_allow_html=True,
    )

    for rank in range(7, -1, -1):
        columns = st.columns(
            8,
            gap="small",
        )

        for file_index, column in enumerate(columns):
            square = (
                f"{chr(ord('a') + file_index)}"
                f"{rank + 1}"
            )

            piece = pieces.get(square)

            label = (
                piece.symbol
                if piece is not None
                else ""
            )

            if square in legal_targets:
                label = f"• {label}"

            if square == selected_square:
                label = f"◆ {label}"

            with column:
                with st.container(
                    key=f"board-{square}",
                ):
                    st.button(
                        label,
                        key=(
                            f"button-{game.game_id}-{square}"
                        ),
                        on_click=on_square_clicked,
                        args=(
                            square,
                            game.legal_moves,
                        ),
                        use_container_width=True,
                        disabled=(
                            game.status != "in_progress"
                        ),
                    )

    _render_file_coordinates()


def _render_file_coordinates() -> None:
    """Render the board file coordinates."""
    columns = st.columns(
        8,
        gap="small",
    )

    for file_index, column in enumerate(columns):
        with column:
            st.markdown(
                (
                    '<div class="board-coordinate">'
                    f"{chr(ord('a') + file_index)}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )


def _legal_targets(
    legal_moves: tuple[str, ...],
    selected_square: str | None,
) -> set[str]:
    """Return legal targets for the selected square."""
    if selected_square is None:
        return set()

    return {
        move[2:4]
        for move in legal_moves
        if move[:2] == selected_square
    }
