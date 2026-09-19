from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GetGameState:
    """Request the current state of a chess game."""

    game_id: UUID


Query = GetGameState
