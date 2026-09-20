# src/chess_app/presentation/streamlit/components/board.py

from __future__ import annotations

from collections.abc import Callable, Iterable

import streamlit as st

from chess_app.application.state import GameState

from .styles import inject_css

_FILES = "abcdefgh"
_RANKS = "87654321"  # displayed from the top (rank 8) to the bottom (rank 1)


def render_board(
    game: GameState,
    selected_square: str | None,
    on_square_clicked: Callable[[str, tuple[str, ...]], None],
) -> None:
    """Render the interactive chess board.

    The board is one container holding 64 buttons. board.css turns that
    container into an 8x8 grid, so no st.columns() is needed.
    """
    inject_css(_board_state_css(game, selected_square))

    # Nothing else may be rendered inside this container: board.css relies
    # on the position of each button (:nth-child) to paint the squares.
    with st.container(key="chess_board"):
        for rank in _RANKS:
            for file in _FILES:
                _render_square(game, f"{file}{rank}", on_square_clicked)


def _render_square(
    game: GameState,
    square: str,
    on_square_clicked: Callable[[str, tuple[str, ...]], None],
) -> None:
    """Render one clickable square.

    Do NOT pass help=...: Streamlit then wraps the button in tooltip
    elements (and duplicates it), so selectors on the button stop matching.
    """
    st.button(
        square,
        key=f"sq-{square}",
        on_click=on_square_clicked,
        args=(square, game.legal_moves),
        disabled=(game.status != "in_progress"),
    )


def _board_state_css(
    game: GameState,
    selected_square: str | None,
) -> str:
    """Generate the per-square CSS variables for the current position.

    Only variables are set here (--piece, --overlay, --hint, --cursor,
    --hover-ring); board.css decides how they are drawn.
    """
    pieces = {piece.square: piece for piece in game.board.pieces}
    in_progress = game.status == "in_progress"
    legal_targets = _legal_targets(game.legal_moves, selected_square)

    rules: list[str] = []

    # 1. Pieces, grouped by image (at most 12 rules)
    squares_by_piece: dict[str, list[str]] = {}

    for square, piece in pieces.items():
        squares_by_piece.setdefault(
            f"{piece.color}-{piece.type}",
            [],
        ).append(square)

    for asset, squares in sorted(squares_by_piece.items()):
        rules.append(
            f"{_squares(squares)} {{ --piece: var(--piece-{asset}); }}"
        )

    # 2. Last move
    if game.last_move is not None:
        rules.append(
            f"{_squares((game.last_move.source, game.last_move.target))} "
            "{ --overlay: var(--hl-last); }"
        )

    # 3. Selected square
    if selected_square is not None:
        rules.append(
            f"{_squares((selected_square,))} "
            "{ --overlay: var(--hl-selected); }"
        )

    # 4. King in check
    if game.in_check and in_progress:
        king_squares = [
            square
            for square, piece in pieces.items()
            if piece.type == "king" and piece.color == game.turn
        ]

        if king_squares:
            rules.append(
                f"{_squares(king_squares)} {{ --overlay: var(--hl-check); }}"
            )

    # 5. Legal targets: dot on an empty square, corners on a capture
    quiet = [square for square in legal_targets if square not in pieces]
    captures = [square for square in legal_targets if square in pieces]

    if quiet:
        rules.append(f"{_squares(quiet)} {{ --hint: var(--hint-move); }}")

    if captures:
        rules.append(f"{_squares(captures)} {{ --hint: var(--hint-capture); }}")

    # 6. Squares that react to a click get a pointer and a hover ring
    if in_progress:
        clickable = {move[:2] for move in game.legal_moves}
        clickable.update(legal_targets)

        if selected_square is not None:
            clickable.add(selected_square)

        if clickable:
            rules.append(
                f"{_squares(sorted(clickable))} "
                "{ --cursor: pointer; --hover-ring: var(--hover-color); }"
            )

    # 7. Game not in progress: mute the whole board
    if not in_progress:
        rules.append(
            ".st-key-chess_board { filter: saturate(0.6) brightness(0.95); }"
        )

    return "\n".join(rules)


def _squares(squares: Iterable[str]) -> str:
    """Build a selector list targeting the given squares."""
    return ", ".join(f".st-key-sq-{square}" for square in squares)


def _legal_targets(
    legal_moves: tuple[str, ...],
    selected_square: str | None,
) -> tuple[str, ...]:
    """Extract the (unique) destination squares of the selected piece."""
    if selected_square is None:
        return ()

    targets = dict.fromkeys(
        move[2:4]
        for move in legal_moves
        if len(move) >= 4 and move[:2] == selected_square
    )

    return tuple(targets)
