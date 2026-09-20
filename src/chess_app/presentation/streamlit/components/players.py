# src/chess_app/presentation/streamlit/components/players.py

from __future__ import annotations

from html import escape

import streamlit as st

from chess_app.application.state import GameState, PlayerState
from chess_app.domain.player import PlayerType


def render_players(game: GameState) -> None:
    """Render the two players, highlighting the one whose turn it is."""
    active_color = game.turn if game.status == "in_progress" else None

    cards = "".join(
        _player_card(player, is_active=(player.color == active_color))
        for player in (game.white_player, game.black_player)
    )

    st.html(f'<div class="players">{cards}</div>')


def _player_card(player: PlayerState, is_active: bool) -> str:
    """Return the HTML of one player card."""
    type_label = "AI" if player.player_type == PlayerType.AI.value else "Player"
    modifier = " player-card--active" if is_active else ""
    turn = '<span class="player-turn">To move</span>' if is_active else ""

    return (
        f'<div class="player-card{modifier}">'
        f'<span class="player-avatar player-avatar--{player.color}" '
        f'role="img" aria-label="{player.color} king"></span>'
        '<div class="player-info">'
        f'<div class="player-name">{escape(player.name)}</div>'
        f'<div class="player-color">'
        f"{player.color.capitalize()} · {type_label}</div>"
        "</div>"
        f"{turn}"
        "</div>"
    )
