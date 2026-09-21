# src/chess_app/ports/move_engine.py

from __future__ import annotations

from typing import Protocol

from chess_app.domain.game import Game
from chess_app.domain.move import Move


class EngineError(Exception):
    """Raised when an engine cannot provide a move."""


class MoveEngine(Protocol):
    def choose_move(self, game: Game) -> Move:
        """Return the engine's move. NOT guaranteed legal: the caller
        must play it through the domain. Raise EngineError on failure."""
        ...
