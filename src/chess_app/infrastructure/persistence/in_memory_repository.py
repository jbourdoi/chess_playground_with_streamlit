from __future__ import annotations

from uuid import UUID

from chess_app.domain.game import Game


class InMemoryGameRepository:
    """Store chess games in process memory."""

    def __init__(self) -> None:
        """Initialize an empty repository."""
        self._games: dict[UUID, Game] = {}

    def get(self, game_id: UUID) -> Game | None:
        """
        Retrieve a game by its identifier.

        Return None when the game does not exist.
        """
        return self._games.get(game_id)

    def save(self, game: Game) -> None:
        """Store or replace a game."""
        self._games[game.game_id] = game
