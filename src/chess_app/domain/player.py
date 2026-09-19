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
    """Represent a chess player."""

    player_id: UUID
    name: str
    color: Color
    player_type: PlayerType = PlayerType.HUMAN

    def __post_init__(self) -> None:
        """Validate the player."""
        if not self.name.strip():
            raise ValueError("player name cannot be empty")
