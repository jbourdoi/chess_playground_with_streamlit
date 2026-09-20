# src/chess_app/presentation/streamlit/components/styles.py

from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

import streamlit as st

_STATIC_DIRECTORY = Path(__file__).resolve().parent.parent / "static"
_CSS_DIRECTORY = _STATIC_DIRECTORY / "css"
_PIECES_DIRECTORY = _STATIC_DIRECTORY / "pieces"

_COLORS = ("white", "black")
_PIECE_TYPES = ("pawn", "knight", "bishop", "rook", "queen", "king")

_CSS_FILENAMES = (
    "layout.css",
    "header.css",
    "messages.css",
    "players.css",
    "status.css",
    "board.css",
    "promotion.css",
    "controls.css",
    "history.css",
)


def inject_css(css: str) -> None:
    """Inject CSS into the page.

    st.html() is used instead of st.markdown(): a style-only st.html() does
    not add an (empty) element to the page flow, whereas each st.markdown()
    call adds one flex gap above the content.
    """
    st.html(f"<style>\n{css}\n</style>")


def render_styles() -> None:
    """Load the piece images and every application CSS file."""
    parts = [_piece_variables()]
    parts.extend(_read_css(filename) for filename in _CSS_FILENAMES)

    inject_css("\n".join(parts))


def _read_css(filename: str) -> str:
    """Read one CSS file (not cached, so CSS edits show up on rerun)."""
    path = _CSS_DIRECTORY / filename

    if not path.is_file():
        raise FileNotFoundError(f"CSS file not found: {path}")

    return path.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _piece_variables() -> str:
    """Expose each piece SVG as a CSS variable: --piece-<color>-<type>.

    Every image is embedded once here; the board then only references
    these variables instead of repeating the base64 data per square.
    """
    lines = [
        f"    --piece-{color}-{piece_type}: url"
        f'("{_svg_data_uri(color, piece_type)}");'
        for color in _COLORS
        for piece_type in _PIECE_TYPES
    ]

    return ":root {\n" + "\n".join(lines) + "\n}"


def _svg_data_uri(color: str, piece_type: str) -> str:
    """Return a piece SVG as a base64 data URI."""
    path = _PIECES_DIRECTORY / color / f"{piece_type}.svg"

    if not path.is_file():
        raise FileNotFoundError(f"Chess piece SVG not found: {path}")

    svg = path.read_text(encoding="utf-8")

    # A browser only renders an SVG used as an image (data URI included)
    # when it declares its XML namespace; otherwise the image stays blank.
    if "xmlns=" not in svg:
        svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)

    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")

    return f"data:image/svg+xml;base64,{encoded}"
