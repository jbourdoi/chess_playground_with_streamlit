# tests/infrastructure/test_sqlite_game_repository.py

import sqlite3
from uuid import uuid4

from chess_app.domain.game import Game
from chess_app.domain.move import Move
from chess_app.domain.piece import Color
from chess_app.domain.player import Player, PlayerType
from chess_app.domain.square import Square
from chess_app.infrastructure.persistence.sqlite_game_repository import (
    SQLiteGameRepository,
)
from chess_app.ports.game_repository import GameRepository


def make_game() -> Game:
    """Create a test game."""
    white = Player(
        player_id=uuid4(),
        name="Alice",
        color=Color.WHITE,
        player_type=PlayerType.HUMAN,
        user_id=uuid4(),
    )

    black = Player(
        player_id=uuid4(),
        name="ChessBot",
        color=Color.BLACK,
        player_type=PlayerType.AI,
    )

    return Game.new(
        game_id=uuid4(),
        white_player=white,
        black_player=black,
    )


def make_move(
    source: str,
    target: str,
) -> Move:
    """Create a move from algebraic notation."""
    return Move(
        source=Square.from_algebraic(source),
        target=Square.from_algebraic(target),
    )


def test_repository_implements_protocol(
    tmp_path,
) -> None:
    """Verify the repository implements the port."""
    repository: GameRepository = SQLiteGameRepository(tmp_path / "chess.db")

    assert repository is not None


def test_database_contains_games_and_moves(
    tmp_path,
) -> None:
    """Verify the SQLite schema."""
    database_path = tmp_path / "chess.db"

    SQLiteGameRepository(database_path)

    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            )
        }

    assert "games" in tables
    assert "moves" in tables


def test_get_unknown_game_returns_none(
    tmp_path,
) -> None:
    """Return None when a game does not exist."""
    repository = SQLiteGameRepository(tmp_path / "chess.db")

    assert repository.get(uuid4()) is None


def test_save_and_get_game(
    tmp_path,
) -> None:
    """Persist and reconstruct a game."""
    repository = SQLiteGameRepository(tmp_path / "chess.db")

    game = make_game()

    repository.save(game)

    restored = repository.get(game.game_id)

    assert restored == game


def test_save_and_get_game_with_moves(
    tmp_path,
) -> None:
    """Persist and reconstruct a game's move history."""
    repository = SQLiteGameRepository(tmp_path / "chess.db")

    game = make_game()

    game = game.play(make_move("e2", "e4"))

    game = game.play(make_move("e7", "e5"))

    game = game.play(make_move("g1", "f3"))

    repository.save(game)

    restored = repository.get(game.game_id)

    assert restored == game
    assert restored is not None
    assert restored.moves == game.moves


def test_save_replaces_existing_game(
    tmp_path,
) -> None:
    """Save an updated game without duplicating moves."""
    repository = SQLiteGameRepository(tmp_path / "chess.db")

    game = make_game()

    repository.save(game)

    updated_game = game.play(make_move("e2", "e4"))

    repository.save(updated_game)

    restored = repository.get(game.game_id)

    assert restored == updated_game
    assert restored is not None
    assert len(restored.moves) == 1


def test_suspended_game_is_preserved(
    tmp_path,
) -> None:
    """Persist and reconstruct a suspended game."""
    repository = SQLiteGameRepository(tmp_path / "chess.db")

    game = make_game()
    game = game.play(make_move("e2", "e4"))

    suspended = game.suspend()

    repository.save(suspended)

    restored = repository.get(game.game_id)

    assert restored == suspended
    assert restored is not None
    assert restored.status.value == "suspended"


def test_castling_position_is_reconstructed(
    tmp_path,
) -> None:
    """Reconstruct a game containing a castling move."""
    repository = SQLiteGameRepository(tmp_path / "chess.db")

    game = make_game()

    moves = (
        ("e2", "e4"),
        ("e7", "e5"),
        ("g1", "f3"),
        ("b8", "c6"),
        ("f1", "e2"),
        ("g8", "f6"),
        ("e1", "g1"),
    )

    for source, target in moves:
        game = game.play(make_move(source, target))

    repository.save(game)

    restored = repository.get(game.game_id)

    assert restored == game
    assert restored is not None
    assert restored.moves[-1].uci == "e1g1"


def test_en_passant_position_is_reconstructed(
    tmp_path,
) -> None:
    """Reconstruct a game containing an en passant capture."""
    repository = SQLiteGameRepository(tmp_path / "chess.db")

    game = make_game()

    moves = (
        ("e2", "e4"),
        ("a7", "a6"),
        ("e4", "e5"),
        ("d7", "d5"),
        ("e5", "d6"),
    )

    for source, target in moves:
        game = game.play(make_move(source, target))

    repository.save(game)

    restored = repository.get(game.game_id)

    assert restored == game
    assert restored is not None
    assert restored.moves[-1].uci == "e5d6"


def test_repository_can_be_reopened(
    tmp_path,
) -> None:
    """Verify that data survives repository recreation."""
    database_path = tmp_path / "chess.db"

    game = make_game()

    first_repository = SQLiteGameRepository(database_path)
    first_repository.save(game)

    second_repository = SQLiteGameRepository(database_path)

    restored = second_repository.get(game.game_id)

    assert restored == game
