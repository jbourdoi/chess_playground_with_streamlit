from __future__ import annotations

from dataclasses import dataclass

from .piece import PieceType
from .position import Square


@dataclass(frozen=True, slots=True)
class Move:
    """Represent a chess move."""

    source: Square
    target: Square
    promotion: PieceType | None = None

    def __post_init__(self) -> None:
        """Validate the move structure."""
        if self.source == self.target:
            raise ValueError("source and target must be different")

    @property
    def uci(self) -> str:
        """
        Return the move in UCI-like notation.

        Examples:
            e2e4
            e7e8q
            e7e8n
        """
        result = f"{self.source.algebraic}{self.target.algebraic}"

        if self.promotion is not None:
            promotion_symbols = {
                PieceType.KNIGHT: "n",
                PieceType.BISHOP: "b",
                PieceType.ROOK: "r",
                PieceType.QUEEN: "q",
            }
            result += promotion_symbols[self.promotion]

        return result
