# src/chess_app/domain/fen.py

from __future__ import annotations

from collections.abc import Sequence

from .board import Board
from .castling_rights import CastlingRights
from .game import Game
from .move import Move
from .piece import Color, PieceType
from .rules import next_en_passant_target
from .square import Square

_PIECE_LETTERS = {
    PieceType.PAWN: "p",
    PieceType.KNIGHT: "n",
    PieceType.BISHOP: "b",
    PieceType.ROOK: "r",
    PieceType.QUEEN: "q",
    PieceType.KING: "k",
}


def to_fen(game: Game) -> str:
    """Return the current position in FEN
    (en passant set after any double push)."""
    turn = "w" if game.turn is Color.WHITE else "b"

    if game.en_passant_target is None:
        en_passant = "-"
    else:
        en_passant = game.en_passant_target.algebraic

    return " ".join(
        (
            _placement(game.board),
            turn,
            _castling(game.castling_rights),
            en_passant,
            str(_halfmove_clock(game.moves)),
            str(len(game.moves) // 2 + 1),
        )
    )


def _placement(board: Board) -> str:
    ranks: list[str] = []

    for rank in range(7, -1, -1):
        cells: list[str] = []
        empty = 0

        for file in range(8):
            piece = board.piece_at(Square(file=file, rank=rank))

            if piece is None:
                empty += 1
                continue

            if empty:
                cells.append(str(empty))
                empty = 0

            letter = _PIECE_LETTERS[piece.type]
            cells.append(
                letter.upper() if piece.color is Color.WHITE else letter
            )

        if empty:
            cells.append(str(empty))

        ranks.append("".join(cells))

    return "/".join(ranks)


def _castling(rights: CastlingRights) -> str:
    result = (
        ("K" if rights.white_kingside else "")
        + ("Q" if rights.white_queenside else "")
        + ("k" if rights.black_kingside else "")
        + ("q" if rights.black_queenside else "")
    )

    return result or "-"


def _halfmove_clock(moves: Sequence[Move]) -> int:
    """Plies since the last capture or pawn move, rebuilt by replaying."""
    board = Board.initial()
    en_passant: Square | None = None
    clock = 0

    for move in moves:
        piece = board.piece_at(move.source)
        is_pawn_move = piece is not None and piece.type is PieceType.PAWN

        is_capture = board.piece_at(move.target) is not None or (
            is_pawn_move
            and move.target == en_passant
            and move.source.file != move.target.file
        )

        clock = 0 if is_pawn_move or is_capture else clock + 1

        previous_en_passant = en_passant
        en_passant = next_en_passant_target(move, board)
        board = board.move_piece(move, previous_en_passant)

    return clock
