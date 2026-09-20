# tests/domain/test_player.py

from uuid import uuid4

import pytest

from chess_app.domain.piece import Color
from chess_app.domain.player import Player, PlayerType


def test_ai_player_has_no_user() -> None:
    player = Player(
        player_id=uuid4(),
        name="ChessBot",
        color=Color.BLACK,
        player_type=PlayerType.AI,
    )

    assert player.user_id is None


def test_ai_player_cannot_have_user() -> None:
    with pytest.raises(ValueError):
        Player(
            player_id=uuid4(),
            name="ChessBot",
            color=Color.BLACK,
            player_type=PlayerType.AI,
            user_id=uuid4(),
        )


def test_human_player_can_reference_user() -> None:
    user_id = uuid4()

    player = Player(
        player_id=uuid4(),
        name="Alice",
        color=Color.WHITE,
        player_type=PlayerType.HUMAN,
        user_id=user_id,
    )

    assert player.user_id == user_id
