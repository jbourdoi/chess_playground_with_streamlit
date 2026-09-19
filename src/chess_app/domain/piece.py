from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Color(Enum):
    """Represent a chess player color."""

    WHITE = "white"
    BLACK = "black"

    @property
    def opposite(self) -> Color:
        """Return the opposite color."""
        if self is Color.WHITE:
            return Color.BLACK

        return Color.WHITE


class PieceType(Enum):
    """Represent a chess piece type."""

    PAWN = "pawn"
    KNIGHT = "knight"
    BISHOP = "bishop"
    ROOK = "rook"
    QUEEN = "queen"
    KING = "king"


@dataclass(frozen=True, slots=True)
class Piece:
    """Represent a chess piece."""

    color: Color
    type: PieceType

    @property
    def symbol(self) -> str:
        """Return the Unicode symbol of the piece."""
        symbols = {
            Color.WHITE: {
                PieceType.PAWN: "♙",
                PieceType.KNIGHT: "♘",
                PieceType.BISHOP: "♗",
                PieceType.ROOK: "♖",
                PieceType.QUEEN: "♕",
                PieceType.KING: "♔",
            },
            Color.BLACK: {
                PieceType.PAWN: "♟",
                PieceType.KNIGHT: "♞",
                PieceType.BISHOP: "♝",
                PieceType.ROOK: "♜",
                PieceType.QUEEN: "♛",
                PieceType.KING: "♚",
            },
        }

        return symbols[self.color][self.type]
