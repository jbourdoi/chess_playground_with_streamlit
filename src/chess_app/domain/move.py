# src/chess_app/domain/move.py

from __future__ import annotations

from dataclasses import dataclass

from .piece import PieceType
from .square import Square

_PROMOTION_BY_SYMBOL = {
    "n": PieceType.KNIGHT,
    "b": PieceType.BISHOP,
    "r": PieceType.ROOK,
    "q": PieceType.QUEEN,
}


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

    @classmethod
    def from_uci(cls, uci: str) -> Move:
        """Create a move from UCI notation (raise ValueError if invalid)."""
        if len(uci) not in {4, 5}:
            raise ValueError(f"invalid UCI move: {uci!r}")

        promotion = None

        if len(uci) == 5:
            promotion = _PROMOTION_BY_SYMBOL.get(uci[4].lower())

            if promotion is None:
                raise ValueError(f"invalid promotion in UCI move: {uci!r}")

        return cls(
            source=Square.from_algebraic(uci[:2]),
            target=Square.from_algebraic(uci[2:4]),
            promotion=promotion,
        )
