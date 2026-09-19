# src/chess_app/presentation/streamlit/components/players.py

from __future__ import annotations

import streamlit as st

from chess_app.application.state import GameState
from chess_app.domain.player import PlayerType


def render_players(game: GameState) -> None:
    """Render the players."""
    st.markdown("### Players")

    _render_player_card(
        symbol="♔",
        color_name="White",
        name=game.white_player.name,
        player_type=game.white_player.player_type,
    )

    _render_player_card(
        symbol="♚",
        color_name="Black",
        name=game.black_player.name,
        player_type=game.black_player.player_type,
    )


def _render_player_card(
    symbol: str,
    color_name: str,
    name: str,
    player_type: str,
) -> None:
    """Render one player card."""
    type_label = "AI" if player_type == PlayerType.AI.value else "Player"

    st.markdown(
        '<div class="player-card">'
        '<div class="player-name">'
        f"{symbol} {name}"
        "</div>"
        '<div class="player-type">'
        f"{color_name} · {type_label}"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )
