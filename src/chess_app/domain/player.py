# src/chess_app/domain/player.py

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from .piece import Color


class PlayerType(Enum):
    """Represent the type of player."""

    HUMAN = "human"
    AI = "ai"


@dataclass(frozen=True, slots=True)
class Player:
    """Represent a participant in a chess game."""

    player_id: UUID
    name: str
    color: Color
    player_type: PlayerType = PlayerType.HUMAN
    user_id: UUID | None = None

    def __post_init__(self) -> None:
        """Validate the player."""
        if not self.name.strip():
            raise ValueError("player name cannot be empty")

        if self.player_type is PlayerType.AI and self.user_id is not None:
            raise ValueError("an AI player cannot be associated with a user")
