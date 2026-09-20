# src/chess_app/domain/board.py

from __future__ import annotations

from dataclasses import dataclass

from .move import Move
from .piece import Color, Piece, PieceType
from .square import Square


@dataclass(frozen=True, slots=True)
class Board:
    """Represent an immutable chess board."""

    _cells: tuple[Piece | None, ...]

    def __post_init__(self) -> None:
        """Validate the board representation."""
        if len(self._cells) != 64:
            raise ValueError("a chess board must contain 64 cells")

    @classmethod
    def empty(cls) -> Board:
        """Create an empty board."""
        return cls(_cells=(None,) * 64)

    @classmethod
    def initial(cls) -> Board:
        """Create a board in the initial chess position."""
        board = cls.empty()

        for file in range(8):
            board = board.with_piece(
                Square(file=file, rank=1),
                Piece(Color.WHITE, PieceType.PAWN),
            )
            board = board.with_piece(
                Square(file=file, rank=6),
                Piece(Color.BLACK, PieceType.PAWN),
            )

        white_back_rank = (
            PieceType.ROOK,
            PieceType.KNIGHT,
            PieceType.BISHOP,
            PieceType.QUEEN,
            PieceType.KING,
            PieceType.BISHOP,
            PieceType.KNIGHT,
            PieceType.ROOK,
        )

        for file, piece_type in enumerate(white_back_rank):
            board = board.with_piece(
                Square(file=file, rank=0),
                Piece(Color.WHITE, piece_type),
            )
            board = board.with_piece(
                Square(file=file, rank=7),
                Piece(Color.BLACK, piece_type),
            )

        return board

    @staticmethod
    def _index(square: Square) -> int:
        """Convert a square into the internal board index."""
        return square.rank * 8 + square.file

    def piece_at(self, square: Square) -> Piece | None:
        """Return the piece located on a square."""
        return self._cells[self._index(square)]

    def with_piece(self, square: Square, piece: Piece | None) -> Board:
        """Return a new board with one cell replaced."""
        cells = list(self._cells)
        cells[self._index(square)] = piece

        return Board(_cells=tuple(cells))

    def move_piece(
        self,
        move: Move,
        en_passant_target: Square | None = None,
    ) -> Board:
        """
        Return a new board after applying a move.

        This method performs the mechanical board update only.
        Legality is handled by the rules module.
        """
        piece = self.piece_at(move.source)

        if piece is None:
            raise ValueError("source square is empty")

        board = self.with_piece(move.source, None)

        # Castling.
        if piece.type is PieceType.KING:
            file_delta = move.target.file - move.source.file

            if abs(file_delta) == 2:
                board = self._move_castling_rook(
                    board,
                    move,
                )

        # En passant capture.
        if (
            piece.type is PieceType.PAWN
            and en_passant_target == move.target
            and move.source.file != move.target.file
            and self.piece_at(move.target) is None
        ):
            captured_square = Square(
                file=move.target.file,
                rank=move.source.rank,
            )

            board = board.with_piece(captured_square, None)

        # Promotion.
        if move.promotion is not None:
            piece = Piece(
                color=piece.color,
                type=move.promotion,
            )

        return board.with_piece(move.target, piece)

    def pieces(
        self, color: Color | None = None
    ) -> tuple[tuple[Square, Piece], ...]:
        """
        Return all pieces, optionally filtered by color.
        """
        result: list[tuple[Square, Piece]] = []

        for rank in range(8):
            for file in range(8):
                square = Square(file=file, rank=rank)
                piece = self.piece_at(square)

                if piece is None:
                    continue

                if color is not None and piece.color is not color:
                    continue

                result.append((square, piece))

        return tuple(result)

    def _move_castling_rook(
        self,
        board: Board,
        move: Move,
    ) -> Board:
        """Move the rook associated with a castling move."""
        if move.target.file > move.source.file:
            rook_source = Square(
                file=7,
                rank=move.source.rank,
            )
            rook_target = Square(
                file=5,
                rank=move.source.rank,
            )
        else:
            rook_source = Square(
                file=0,
                rank=move.source.rank,
            )
            rook_target = Square(
                file=3,
                rank=move.source.rank,
            )

        rook = board.piece_at(rook_source)

        if rook is None or rook.type is not PieceType.ROOK:
            raise ValueError("castling rook is missing")

        board = board.with_piece(rook_source, None)

        return board.with_piece(rook_target, rook)
