# tests/infrastructure/test_in_memory_game_repository.py

from uuid import UUID, uuid4

from chess_app.domain.game import Game
from chess_app.domain.piece import Color
from chess_app.domain.player import Player
from chess_app.infrastructure.persistence.in_memory_game_repository import (
    InMemoryGameRepository,
)
from chess_app.ports.game_repository import GameRepository


def make_game(game_id: UUID | None = None) -> Game:
    """Create a test game."""
    white = Player(
        player_id=uuid4(),
        name="Alice",
        color=Color.WHITE,
    )

    black = Player(
        player_id=uuid4(),
        name="Bob",
        color=Color.BLACK,
    )

    return Game.new(
        game_id=game_id if game_id is not None else uuid4(),
        white_player=white,
        black_player=black,
    )


def test_empty_repository_returns_none() -> None:
    repository = InMemoryGameRepository()

    assert repository.get(uuid4()) is None


def test_save_and_get_game() -> None:
    repository = InMemoryGameRepository()
    game = make_game()

    repository.save(game)

    assert repository.get(game.game_id) == game


def test_save_replaces_existing_game() -> None:
    repository = InMemoryGameRepository()

    game_id = UUID("11111111-1111-1111-1111-111111111111")

    first_game = make_game(game_id)
    second_game = make_game(game_id)

    repository.save(first_game)
    repository.save(second_game)

    assert repository.get(game_id) == second_game


def test_repository_implements_protocol() -> None:
    repository: GameRepository = InMemoryGameRepository()

    assert repository is not None
