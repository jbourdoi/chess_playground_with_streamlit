# src/chess_app/presentation/streamlit/components/promotion.py

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from chess_app.application.state import GameState


def render_promotion(
    game: GameState,
    pending_promotion: tuple[str, str] | None,
    on_promotion_selected: Callable[
        [str, str, str],
        None,
    ],
) -> None:
    """Render the promotion selector."""
    if pending_promotion is None:
        return

    source, target = pending_promotion

    st.markdown(
        '<div class="promotion-box">',
        unsafe_allow_html=True,
    )

    st.markdown("### Promotion")

    st.write(f"{source} → {target}")

    promotion_labels = {
        "q": "Queen",
        "r": "Rook",
        "b": "Bishop",
        "n": "Knight",
    }

    selected = st.selectbox(
        "Piece",
        options=tuple(promotion_labels),
        format_func=promotion_labels.__getitem__,
        key=(f"promotion-{game.game_id}-{target}"),
    )

    st.button(
        "Confirm",
        key=f"confirm-promotion-{game.game_id}",
        on_click=on_promotion_selected,
        args=(
            source,
            target,
            selected,
        ),
        use_container_width=True,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )
