# tests/domain/test_board.py

import pytest

from chess_app.domain.board import Board
from chess_app.domain.move import Move
from chess_app.domain.piece import Color, Piece, PieceType
from chess_app.domain.square import Square


def test_empty_board_contains_no_piece() -> None:
    board = Board.empty()

    assert board.pieces() == ()


def test_initial_board_contains_32_pieces() -> None:
    board = Board.initial()

    assert len(board.pieces()) == 32


def test_initial_board_contains_16_pieces_per_color() -> None:
    board = Board.initial()

    assert len(board.pieces(Color.WHITE)) == 16
    assert len(board.pieces(Color.BLACK)) == 16


@pytest.mark.parametrize(
    ("square", "color", "piece_type"),
    [
        ("a1", Color.WHITE, PieceType.ROOK),
        ("e1", Color.WHITE, PieceType.KING),
        ("d1", Color.WHITE, PieceType.QUEEN),
        ("e8", Color.BLACK, PieceType.KING),
        ("a7", Color.BLACK, PieceType.PAWN),
    ],
)
def test_initial_piece_placement(
    square: str,
    color: Color,
    piece_type: PieceType,
) -> None:
    board = Board.initial()
    piece = board.piece_at(Square.from_algebraic(square))

    assert piece == Piece(color, piece_type)


def test_with_piece_returns_new_board() -> None:
    board = Board.empty()
    square = Square.from_algebraic("e4")
    piece = Piece(Color.WHITE, PieceType.KING)

    new_board = board.with_piece(square, piece)

    assert board.piece_at(square) is None
    assert new_board.piece_at(square) == piece


def test_move_piece_does_not_mutate_original_board() -> None:
    board = Board.initial()

    move = Move(
        source=Square.from_algebraic("e2"),
        target=Square.from_algebraic("e4"),
    )

    new_board = board.move_piece(move)

    assert board.piece_at(Square.from_algebraic("e2")) == Piece(
        Color.WHITE, PieceType.PAWN
    )

    assert board.piece_at(Square.from_algebraic("e4")) is None

    assert new_board.piece_at(Square.from_algebraic("e2")) is None

    assert new_board.piece_at(Square.from_algebraic("e4")) == Piece(
        Color.WHITE, PieceType.PAWN
    )


def test_move_piece_captures_target_piece() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("e4"),
            Piece(Color.WHITE, PieceType.ROOK),
        )
        .with_piece(
            Square.from_algebraic("e6"),
            Piece(Color.BLACK, PieceType.KNIGHT),
        )
    )

    move = Move(
        source=Square.from_algebraic("e4"),
        target=Square.from_algebraic("e6"),
    )

    new_board = board.move_piece(move)

    assert new_board.piece_at(Square.from_algebraic("e4")) is None

    assert new_board.piece_at(Square.from_algebraic("e6")) == Piece(
        Color.WHITE, PieceType.ROOK
    )


def test_move_piece_promotes_pawn() -> None:
    board = Board.empty().with_piece(
        Square.from_algebraic("e7"),
        Piece(Color.WHITE, PieceType.PAWN),
    )

    move = Move(
        source=Square.from_algebraic("e7"),
        target=Square.from_algebraic("e8"),
        promotion=PieceType.QUEEN,
    )

    new_board = board.move_piece(move)

    assert new_board.piece_at(Square.from_algebraic("e8")) == Piece(
        Color.WHITE, PieceType.QUEEN
    )


def test_move_piece_requires_source_piece() -> None:
    board = Board.empty()

    move = Move(
        source=Square.from_algebraic("e2"),
        target=Square.from_algebraic("e4"),
    )

    with pytest.raises(ValueError):
        board.move_piece(move)
