# src/chess_app/presentation/streamlit/components/promotion.py

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from chess_app.application.state import GameState

from .styles import inject_css

# (UCI suffix, piece type used for the SVG variable, label)
_CHOICES = (
    ("q", "queen", "Queen"),
    ("r", "rook", "Rook"),
    ("b", "bishop", "Bishop"),
    ("n", "knight", "Knight"),
)


def render_promotion(
    game: GameState,
    pending_promotion: tuple[str, str] | None,
    on_promotion_selected: Callable[
        [str, str, str],
        None,
    ],
) -> None:
    """Render the promotion picker: one click on the piece to promote to."""
    if pending_promotion is None:
        return

    source, target = pending_promotion

    # The choices show the pieces of the side that is promoting. Like on the
    # board, Python only sets CSS variables; promotion.css draws them.
    tile = "--sq-dark" if game.turn == "white" else "--sq-light"

    rules = [
        f".st-key-promo-{code} "
        f"{{ --piece: var(--piece-{game.turn}-{piece_type}); }}"
        for code, piece_type, _ in _CHOICES
    ]
    rules.append(f".st-key-promotion_choices {{ --promo-bg: var({tile}); }}")

    inject_css("\n".join(rules))

    # A keyed container is the reliable way to style a group of widgets:
    # an HTML <div> opened in one st.markdown() call cannot wrap the next ones.
    with st.container(key="promotion"):
        st.html(
            '<div class="promotion-title">Promote to</div>'
            f'<div class="promotion-move">{source} → {target}</div>'
        )

        with st.container(key="promotion_choices"):
            for code, _, label in _CHOICES:
                st.button(
                    label,
                    key=f"promo-{code}",
                    on_click=on_promotion_selected,
                    args=(source, target, code),
                )
