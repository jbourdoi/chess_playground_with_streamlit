# tests/domain/test_game.py

from uuid import uuid4

import pytest

from chess_app.domain.errors import IllegalMoveError, InvalidGameStateError
from chess_app.domain.game import Game, GameStatus
from chess_app.domain.move import Move
from chess_app.domain.piece import Color, Piece, PieceType
from chess_app.domain.player import Player, PlayerType
from chess_app.domain.square import Square


def make_players() -> tuple[Player, Player]:
    """Create a white player and a black player."""
    white = Player(
        player_id=uuid4(),
        name="Alice",
        color=Color.WHITE,
        player_type=PlayerType.HUMAN,
    )

    black = Player(
        player_id=uuid4(),
        name="AI",
        color=Color.BLACK,
        player_type=PlayerType.AI,
    )

    return white, black


def make_game() -> Game:
    """Create a new test game."""
    white, black = make_players()

    return Game.new(
        game_id=uuid4(),
        white_player=white,
        black_player=black,
    )


def make_move(source: str, target: str) -> Move:
    """Create a move from algebraic coordinates."""
    return Move(
        source=Square.from_algebraic(source),
        target=Square.from_algebraic(target),
    )


def test_new_game_starts_in_progress() -> None:
    game = make_game()

    assert game.status is GameStatus.IN_PROGRESS


def test_new_game_starts_with_white_turn() -> None:
    game = make_game()

    assert game.turn is Color.WHITE
    assert game.current_player.color is Color.WHITE


def test_new_game_has_no_moves() -> None:
    game = make_game()

    assert game.moves == ()


def test_play_returns_new_game() -> None:
    game = make_game()

    new_game = game.play(make_move("e2", "e4"))

    assert new_game is not game
    assert game.moves == ()
    assert len(new_game.moves) == 1


def test_play_updates_board() -> None:
    game = make_game()

    new_game = game.play(make_move("e2", "e4"))

    assert new_game.board.piece_at(Square.from_algebraic("e2")) is None

    assert new_game.board.piece_at(Square.from_algebraic("e4")) == Piece(
        Color.WHITE, PieceType.PAWN
    )


def test_play_changes_turn() -> None:
    game = make_game()

    new_game = game.play(make_move("e2", "e4"))

    assert new_game.turn is Color.BLACK
    assert new_game.current_player.color is Color.BLACK


def test_play_appends_move_to_history() -> None:
    game = make_game()
    move = make_move("e2", "e4")

    new_game = game.play(move)

    assert new_game.moves == (move,)


def test_illegal_move_raises() -> None:
    game = make_game()

    with pytest.raises(IllegalMoveError):
        game.play(make_move("e2", "e5"))


def test_suspend_changes_status() -> None:
    game = make_game()

    suspended = game.suspend()

    assert game.status is GameStatus.IN_PROGRESS
    assert suspended.status is GameStatus.SUSPENDED


def test_suspended_game_can_be_resumed() -> None:
    game = make_game()

    suspended = game.suspend()
    resumed = suspended.resume()

    assert suspended.status is GameStatus.SUSPENDED
    assert resumed.status is GameStatus.IN_PROGRESS


def test_suspended_game_cannot_play() -> None:
    game = make_game().suspend()

    with pytest.raises(InvalidGameStateError):
        game.play(make_move("e2", "e4"))


def test_active_game_cannot_be_resumed() -> None:
    game = make_game()

    with pytest.raises(InvalidGameStateError):
        game.resume()


def test_finished_game_cannot_be_suspended() -> None:
    game = make_game()

    finished = Game(
        game_id=game.game_id,
        white_player=game.white_player,
        black_player=game.black_player,
        board=game.board,
        moves=game.moves,
        status=GameStatus.DRAW,
    )

    with pytest.raises(InvalidGameStateError):
        finished.suspend()


def test_white_player_must_be_white() -> None:
    white, black = make_players()

    with pytest.raises(ValueError):
        Game.new(
            game_id=uuid4(),
            white_player=black,
            black_player=white,
        )


def test_black_player_must_be_black() -> None:
    white, black = make_players()

    with pytest.raises(ValueError):
        Game.new(
            game_id=uuid4(),
            white_player=black,
            black_player=white,
        )
