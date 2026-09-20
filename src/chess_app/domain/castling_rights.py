# src/chess_app/domain/castling_rights.py

from __future__ import annotations

from dataclasses import dataclass, replace

from .piece import Color


@dataclass(frozen=True, slots=True)
class CastlingRights:
    """Represent the castling rights of both players."""

    white_kingside: bool = False
    white_queenside: bool = False
    black_kingside: bool = False
    black_queenside: bool = False

    @classmethod
    def initial(cls) -> CastlingRights:
        """Return the initial castling rights."""
        return cls(
            white_kingside=True,
            white_queenside=True,
            black_kingside=True,
            black_queenside=True,
        )

    @classmethod
    def none(cls) -> CastlingRights:
        """Return an object with no castling rights."""
        return cls()

    def without_king_rights(self, color: Color) -> CastlingRights:
        """Remove both castling rights for one color."""
        if color is Color.WHITE:
            return replace(
                self,
                white_kingside=False,
                white_queenside=False,
            )

        return replace(
            self,
            black_kingside=False,
            black_queenside=False,
        )

    def without_kingside(self, color: Color) -> CastlingRights:
        """Remove kingside castling rights."""
        if color is Color.WHITE:
            return replace(self, white_kingside=False)

        return replace(self, black_kingside=False)

    def without_queenside(self, color: Color) -> CastlingRights:
        """Remove queenside castling rights."""
        if color is Color.WHITE:
            return replace(self, white_queenside=False)

        return replace(self, black_queenside=False)

    def can_castle_kingside(self, color: Color) -> bool:
        """Return whether kingside castling is still available."""
        if color is Color.WHITE:
            return self.white_kingside

        return self.black_kingside

    def can_castle_queenside(self, color: Color) -> bool:
        """Return whether queenside castling is still available."""
        if color is Color.WHITE:
            return self.white_queenside

        return self.black_queenside
