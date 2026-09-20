# src/chess_app/presentation/streamlit/components/board.py
from __future__ import annotations

import base64
from collections.abc import Callable, Mapping
from functools import lru_cache
from pathlib import Path

import streamlit as st

from chess_app.application.state import GameState, PieceState

_PIECES_DIRECTORY = Path(__file__).resolve().parent.parent / "static" / "pieces"

_PIECE_ASSETS = {
    "♙": ("white", "pawn"),
    "♖": ("white", "rook"),
    "♘": ("white", "knight"),
    "♗": ("white", "bishop"),
    "♕": ("white", "queen"),
    "♔": ("white", "king"),
    "♟": ("black", "pawn"),
    "♜": ("black", "rook"),
    "♞": ("black", "knight"),
    "♝": ("black", "bishop"),
    "♛": ("black", "queen"),
    "♚": ("black", "king"),
    "P": ("white", "pawn"),
    "R": ("white", "rook"),
    "N": ("white", "knight"),
    "B": ("white", "bishop"),
    "Q": ("white", "queen"),
    "K": ("white", "king"),
    "p": ("black", "pawn"),
    "r": ("black", "rook"),
    "n": ("black", "knight"),
    "b": ("black", "bishop"),
    "q": ("black", "queen"),
    "k": ("black", "king"),
}


def render_board(
    game: GameState,
    selected_square: str | None,
    on_square_clicked: Callable[[str, tuple[str, ...]], None],
) -> None:
    """Render the interactive chess board."""
    pieces = {piece.square: piece for piece in game.board.pieces}
    legal_targets = _legal_targets(game.legal_moves, selected_square)

    # Dynamic CSS (SVG pieces, selection, legal moves, check)
    dynamic_css = _generate_dynamic_css(
        game=game,
        pieces=pieces,
        selected_square=selected_square,
        legal_targets=legal_targets,
    )
    st.markdown(dynamic_css, unsafe_allow_html=True)

    with st.container(key="chess_board_container"):
        # Render ranks from 8 down to 1
        for rank in range(7, -1, -1):
            rank_name = str(rank + 1)
            # 1 col for rank label + 8 cols for board squares
            columns = st.columns([0.4] + [1] * 8, gap=None)

            # Rank coordinate label (1 to 8)
            with columns[0]:
                st.markdown(
                    f'<div class="board-rank-coordinate">{rank_name}</div>',
                    unsafe_allow_html=True,
                )

            # Render the 8 squares of the row
            for file_index in range(8):
                square = f"{chr(ord('a') + file_index)}{rank_name}"
                with columns[file_index + 1]:
                    _render_square(
                        game=game,
                        square=square,
                        on_square_clicked=on_square_clicked,
                    )

        # File coordinate labels (a to h) at the bottom
        _render_file_coordinates()


def _render_square(
    game: GameState,
    square: str,
    on_square_clicked: Callable[[str, tuple[str, ...]], None],
) -> None:
    """Render a clickable square using a single Streamlit button."""
    st.button(
        " ",
        key=f"sq-{square}",
        on_click=on_square_clicked,
        args=(square, game.legal_moves),
        use_container_width=True,
        disabled=(game.status != "in_progress"),
        help=f"Case {square}",
    )


def _generate_dynamic_css(
    game: GameState,
    pieces: Mapping[str, PieceState],
    selected_square: str | None,
    legal_targets: tuple[str, ...],
) -> str:
    """Generate dynamic CSS rules for current board state."""
    rules: list[str] = []

    # 1. Piece SVG backgrounds
    for square, piece in pieces.items():
        symbol = str(getattr(piece, "symbol", ""))
        asset = _PIECE_ASSETS.get(symbol)
        if asset:
            side, piece_name = asset
            svg_data = _load_piece_svg(side, piece_name)
            sel = f'.st-key-sq-{square} div[data-testid="stButton"] > button'
            bg_url = f"data:image/svg+xml;base64,{svg_data}"
            rules.append(
                f"{sel} {{\n"
                f'    background-image: url("{bg_url}") !important;\n'
                f"    background-size: 84% 84% !important;\n"
                f"    background-position: center !important;\n"
                f"    background-repeat: no-repeat !important;\n"
                f"}}"
            )

    # 2. Selected square highlight
    if selected_square:
        sel = (
            f'.st-key-sq-{selected_square} div[data-testid="stButton"] > button'
        )
        rules.append(f"{sel} {{\n    background-color: #cdd26a !important;\n}}")

    # 3. Legal move targets (empty target = dot, occupied = capture ring)
    for target in legal_targets:
        sel = f'.st-key-sq-{target} div[data-testid="stButton"] > button::after'
        if target in pieces:
            # Capture target
            rules.append(
                f"{sel} {{\n"
                f'    content: "";\n'
                f"    position: absolute;\n"
                f"    top: 0; left: 0; right: 0; bottom: 0;\n"
                f"    box-sizing: border-box;\n"
                f"    border: 5px solid rgba(20, 85, 30, 0.45);\n"
                f"    border-radius: 50%;\n"
                f"    pointer-events: none;\n"
                f"}}"
            )
        else:
            # Normal move target
            rules.append(
                f"{sel} {{\n"
                f'    content: "";\n'
                f"    position: absolute;\n"
                f"    top: 50%; left: 50%;\n"
                f"    width: 26%; height: 26%;\n"
                f"    transform: translate(-50%, -50%);\n"
                f"    border-radius: 50%;\n"
                f"    background-color: rgba(20, 85, 30, 0.35);\n"
                f"    pointer-events: none;\n"
                f"}}"
            )

    # 4. King in check highlight
    if game.in_check:
        for square, piece in pieces.items():
            if _is_checked_king(game, square, piece):
                sel = (
                    f'.st-key-sq-{square} div[data-testid="stButton"] > button'
                )
                rules.append(
                    f"{sel} {{\n"
                    f"    background: radial-gradient(circle, #e53935 0%,"
                    f" #b71c1c 70%, transparent 100%) !important;\n"
                    f"}}"
                )

    css_content = "\n".join(rules)
    return f"<style>\n{css_content}\n</style>"


def _is_checked_king(
    game: GameState,
    square: str,
    piece: PieceState | None,
) -> bool:
    """Check if given square contains the king currently in check."""
    if not game.in_check or piece is None:
        return False

    symbol = str(getattr(piece, "symbol", ""))

    if game.turn == "white":
        return square == piece.square and symbol in ("♔", "K")

    if game.turn == "black":
        return square == piece.square and symbol in ("♚", "k")

    return False


def _legal_targets(
    legal_moves: tuple[str, ...],
    selected_square: str | None,
) -> tuple[str, ...]:
    """Extract valid destination squares for selected piece."""
    if selected_square is None:
        return ()

    targets = []
    for move in legal_moves:
        if len(move) < 4:
            continue
        if move[:2] == selected_square:
            targets.append(move[2:4])

    return tuple(targets)


@lru_cache(maxsize=12)
def _load_piece_svg(
    side: str,
    piece_name: str,
) -> str:
    """Load piece SVG file and encode it as Base64."""
    path = _PIECES_DIRECTORY / side / f"{piece_name}.svg"

    if not path.is_file():
        raise FileNotFoundError(f"Chess piece SVG not found: {path}")

    return base64.b64encode(path.read_bytes()).decode("ascii")


def _render_file_coordinates() -> None:
    """Render file coordinate labels (a to h) beneath the board."""
    columns = st.columns([0.4] + [1] * 8, gap=None)

    with columns[0]:
        st.write("")

    for file_index in range(8):
        file_name = chr(ord("a") + file_index)
        with columns[file_index + 1]:
            st.markdown(
                f'<div class="board-file-coordinate">{file_name}</div>',
                unsafe_allow_html=True,
            )
