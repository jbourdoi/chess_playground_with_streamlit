# src/chess_app/application/commands.py

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from chess_app.domain.move import Move
from chess_app.domain.piece import Color
from chess_app.domain.player import PlayerType


@dataclass(frozen=True, slots=True)
class PlayerSpec:
    """Describe a player when creating a new game."""

    player_id: UUID
    name: str
    color: Color
    player_type: PlayerType = PlayerType.HUMAN
    user_id: UUID | None = None

    def __post_init__(self) -> None:
        """Validate the player specification."""
        if not self.name.strip():
            raise ValueError("player name cannot be empty")

        if self.player_type is PlayerType.AI and self.user_id is not None:
            raise ValueError("an AI player cannot be associated with a user")


@dataclass(frozen=True, slots=True)
class NewGame:
    """Request the creation of a new chess game."""

    white_player: PlayerSpec
    black_player: PlayerSpec

    def __post_init__(self) -> None:
        """Validate the new game command."""
        if self.white_player.color is not Color.WHITE:
            raise ValueError("white_player must be white")

        if self.black_player.color is not Color.BLACK:
            raise ValueError("black_player must be black")


@dataclass(frozen=True, slots=True)
class PlayMove:
    """Request that a move be played in a game."""

    game_id: UUID
    move: Move


@dataclass(frozen=True, slots=True)
class SuspendGame:
    """Request that a game be suspended."""

    game_id: UUID


@dataclass(frozen=True, slots=True)
class ResumeGame:
    """Request that a suspended game be resumed."""

    game_id: UUID


@dataclass(frozen=True, slots=True)
class PlayEngineMove:
    """Request that the engine plays the move of the AI player to move."""

    game_id: UUID


Command = NewGame | PlayMove | PlayEngineMove | SuspendGame | ResumeGame
