# src/chess_app/domain/square.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Square:
    """Represent a square on the chess board."""

    file: int
    rank: int

    def __post_init__(self) -> None:
        """Validate the coordinates of the square."""
        if not 0 <= self.file <= 7:
            raise ValueError("file must be between 0 and 7")

        if not 0 <= self.rank <= 7:
            raise ValueError("rank must be between 0 and 7")

    @classmethod
    def from_algebraic(cls, notation: str) -> Square:
        """
        Create a square from algebraic notation.

        Examples:
            "a1" -> Square(file=0, rank=0)
            "e4" -> Square(file=4, rank=3)
        """
        if len(notation) != 2:
            raise ValueError("invalid square notation")

        file = ord(notation[0].lower()) - ord("a")
        rank = ord(notation[1]) - ord("1")

        return cls(file=file, rank=rank)

    @property
    def algebraic(self) -> str:
        """Return the square using algebraic notation."""
        return f"{chr(ord('a') + self.file)}{chr(ord('1') + self.rank)}"

    def offset(self, file_delta: int, rank_delta: int) -> Square | None:
        """
        Return an offset square.

        Return None when the resulting coordinates are outside
        the board.
        """
        file = self.file + file_delta
        rank = self.rank + rank_delta

        if not 0 <= file <= 7 or not 0 <= rank <= 7:
            return None

        return Square(file=file, rank=rank)

    def __str__(self) -> str:
        """Return the algebraic notation."""
        return self.algebraic
