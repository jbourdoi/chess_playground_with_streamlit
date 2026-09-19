# src/chess_app/ports/repository.py

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from chess_app.domain.game import Game


class GameRepository(Protocol):
    """Define persistence operations for chess games."""

    def get(self, game_id: UUID) -> Game | None:
        """
        Retrieve a game by its identifier.

        Return None when the game does not exist.
        """
        ...

    def save(self, game: Game) -> None:
        """Persist a game."""
        ...
