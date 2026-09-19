# tests/application/test_commands.py

from uuid import uuid4

import pytest

from chess_app.application.commands import (
    NewGame,
    PlayerSpec,
    PlayMove,
    ResumeGame,
    SuspendGame,
)
from chess_app.domain.move import Move
from chess_app.domain.piece import Color
from chess_app.domain.player import PlayerType
from chess_app.domain.position import Square


def make_player(
    color: Color,
    player_type: PlayerType = PlayerType.HUMAN,
) -> PlayerSpec:
    """Create a test player specification."""
    return PlayerSpec(
        player_id=uuid4(),
        name=color.value,
        color=color,
        player_type=player_type,
    )


def make_move(source: str, target: str) -> Move:
    """Create a move from algebraic coordinates."""
    return Move(
        source=Square.from_algebraic(source),
        target=Square.from_algebraic(target),
    )


def test_player_spec_creation() -> None:
    player = make_player(Color.WHITE)

    assert player.color is Color.WHITE
    assert player.player_type is PlayerType.HUMAN


def test_player_spec_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        PlayerSpec(
            player_id=uuid4(),
            name="   ",
            color=Color.WHITE,
        )


def test_new_game_accepts_white_and_black() -> None:
    command = NewGame(
        white_player=make_player(Color.WHITE),
        black_player=make_player(
            Color.BLACK,
            PlayerType.AI,
        ),
    )

    assert command.white_player.color is Color.WHITE
    assert command.black_player.color is Color.BLACK


def test_new_game_rejects_invalid_white_player() -> None:
    with pytest.raises(ValueError):
        NewGame(
            white_player=make_player(Color.BLACK),
            black_player=make_player(Color.BLACK),
        )


def test_new_game_rejects_invalid_black_player() -> None:
    with pytest.raises(ValueError):
        NewGame(
            white_player=make_player(Color.WHITE),
            black_player=make_player(Color.WHITE),
        )


def test_play_move_contains_game_and_move() -> None:
    game_id = uuid4()
    move = make_move("e2", "e4")

    command = PlayMove(
        game_id=game_id,
        move=move,
    )

    assert command.game_id == game_id
    assert command.move == move


def test_suspend_game_contains_game_id() -> None:
    game_id = uuid4()

    command = SuspendGame(game_id=game_id)

    assert command.game_id == game_id


def test_resume_game_contains_game_id() -> None:
    game_id = uuid4()

    command = ResumeGame(game_id=game_id)

    assert command.game_id == game_id


def test_commands_are_immutable() -> None:
    command = SuspendGame(game_id=uuid4())

    with pytest.raises(AttributeError):
        command.game_id = uuid4()  # type: ignore[misc]
