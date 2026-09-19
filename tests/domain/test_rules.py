import pytest

from chess_app.domain.board import Board
from chess_app.domain.move import Move
from chess_app.domain.piece import Color, Piece, PieceType
from chess_app.domain.position import Square
from chess_app.domain.rules import (
    is_pseudo_legal_move,
    pseudo_legal_moves,
)


def move(source: str, target: str) -> Move:
    """Build a move from algebraic square names."""
    return Move(
        source=Square.from_algebraic(source),
        target=Square.from_algebraic(target),
    )


def test_initial_position_has_20_white_moves() -> None:
    board = Board.initial()

    moves = pseudo_legal_moves(board, Color.WHITE)

    assert len(moves) == 20


def test_initial_position_has_20_black_moves() -> None:
    board = Board.initial()

    moves = pseudo_legal_moves(board, Color.BLACK)

    assert len(moves) == 20


def test_white_pawn_can_move_one_square() -> None:
    board = Board.initial()

    assert is_pseudo_legal_move(
        board,
        move("e2", "e3"),
        Color.WHITE,
    )


def test_white_pawn_can_move_two_squares_from_start() -> None:
    board = Board.initial()

    assert is_pseudo_legal_move(
        board,
        move("e2", "e4"),
        Color.WHITE,
    )


def test_white_pawn_cannot_move_three_squares() -> None:
    board = Board.initial()

    assert not is_pseudo_legal_move(
        board,
        move("e2", "e5"),
        Color.WHITE,
    )


def test_white_pawn_cannot_move_backwards() -> None:
    board = Board.empty().with_piece(
        Square.from_algebraic("e4"),
        Piece(Color.WHITE, PieceType.PAWN),
    )

    assert not is_pseudo_legal_move(
        board,
        move("e4", "e3"),
        Color.WHITE,
    )


def test_pawn_cannot_move_forward_into_occupied_square() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("e2"),
            Piece(Color.WHITE, PieceType.PAWN),
        )
        .with_piece(
            Square.from_algebraic("e3"),
            Piece(Color.BLACK, PieceType.PAWN),
        )
    )

    assert not is_pseudo_legal_move(
        board,
        move("e2", "e3"),
        Color.WHITE,
    )


def test_pawn_can_capture_diagonally() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("e4"),
            Piece(Color.WHITE, PieceType.PAWN),
        )
        .with_piece(
            Square.from_algebraic("f5"),
            Piece(Color.BLACK, PieceType.KNIGHT),
        )
    )

    assert is_pseudo_legal_move(
        board,
        move("e4", "f5"),
        Color.WHITE,
    )


def test_pawn_cannot_move_diagonally_without_capture() -> None:
    board = Board.empty().with_piece(
        Square.from_algebraic("e4"),
        Piece(Color.WHITE, PieceType.PAWN),
    )

    assert not is_pseudo_legal_move(
        board,
        move("e4", "f5"),
        Color.WHITE,
    )


@pytest.mark.parametrize(
    ("source", "target"),
    [
        ("b1", "a3"),
        ("b1", "c3"),
        ("d4", "f5"),
        ("d4", "f3"),
    ],
)
def test_knight_moves(source: str, target: str) -> None:
    board = Board.empty().with_piece(
        Square.from_algebraic(source),
        Piece(Color.WHITE, PieceType.KNIGHT),
    )

    assert is_pseudo_legal_move(
        board,
        move(source, target),
        Color.WHITE,
    )


def test_bishop_moves_diagonally() -> None:
    board = Board.empty().with_piece(
        Square.from_algebraic("c1"),
        Piece(Color.WHITE, PieceType.BISHOP),
    )

    assert is_pseudo_legal_move(
        board,
        move("c1", "h6"),
        Color.WHITE,
    )


def test_bishop_cannot_jump_over_piece() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("c1"),
            Piece(Color.WHITE, PieceType.BISHOP),
        )
        .with_piece(
            Square.from_algebraic("d2"),
            Piece(Color.WHITE, PieceType.PAWN),
        )
    )

    assert not is_pseudo_legal_move(
        board,
        move("c1", "h6"),
        Color.WHITE,
    )


def test_rook_moves_straight() -> None:
    board = Board.empty().with_piece(
        Square.from_algebraic("a1"),
        Piece(Color.WHITE, PieceType.ROOK),
    )

    assert is_pseudo_legal_move(
        board,
        move("a1", "a8"),
        Color.WHITE,
    )


def test_rook_cannot_move_diagonally() -> None:
    board = Board.empty().with_piece(
        Square.from_algebraic("a1"),
        Piece(Color.WHITE, PieceType.ROOK),
    )

    assert not is_pseudo_legal_move(
        board,
        move("a1", "b2"),
        Color.WHITE,
    )


def test_queen_moves_diagonally() -> None:
    board = Board.empty().with_piece(
        Square.from_algebraic("d1"),
        Piece(Color.WHITE, PieceType.QUEEN),
    )

    assert is_pseudo_legal_move(
        board,
        move("d1", "h5"),
        Color.WHITE,
    )


def test_queen_moves_straight() -> None:
    board = Board.empty().with_piece(
        Square.from_algebraic("d1"),
        Piece(Color.WHITE, PieceType.QUEEN),
    )

    assert is_pseudo_legal_move(
        board,
        move("d1", "d8"),
        Color.WHITE,
    )


def test_king_moves_one_square() -> None:
    board = Board.empty().with_piece(
        Square.from_algebraic("e4"),
        Piece(Color.WHITE, PieceType.KING),
    )

    assert is_pseudo_legal_move(
        board,
        move("e4", "f5"),
        Color.WHITE,
    )


def test_king_cannot_move_two_squares() -> None:
    board = Board.empty().with_piece(
        Square.from_algebraic("e4"),
        Piece(Color.WHITE, PieceType.KING),
    )

    assert not is_pseudo_legal_move(
        board,
        move("e4", "g5"),
        Color.WHITE,
    )


def test_piece_cannot_capture_own_piece() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("e4"),
            Piece(Color.WHITE, PieceType.ROOK),
        )
        .with_piece(
            Square.from_algebraic("e6"),
            Piece(Color.WHITE, PieceType.PAWN),
        )
    )

    assert not is_pseudo_legal_move(
        board,
        move("e4", "e6"),
        Color.WHITE,
    )


def test_player_can_only_move_own_piece() -> None:
    board = Board.initial()

    assert not is_pseudo_legal_move(
        board,
        move("e7", "e5"),
        Color.WHITE,
    )


def test_cannot_capture_king() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("e4"),
            Piece(Color.WHITE, PieceType.ROOK),
        )
        .with_piece(
            Square.from_algebraic("e8"),
            Piece(Color.BLACK, PieceType.KING),
        )
    )

    assert not is_pseudo_legal_move(
        board,
        move("e4", "e8"),
        Color.WHITE,
    )


@pytest.mark.parametrize(
    "promotion",
    [
        PieceType.QUEEN,
        PieceType.ROOK,
        PieceType.BISHOP,
        PieceType.KNIGHT,
    ],
)
def test_pawn_promotion_requires_valid_piece(
    promotion: PieceType,
) -> None:
    board = Board.empty().with_piece(
        Square.from_algebraic("e7"),
        Piece(Color.WHITE, PieceType.PAWN),
    )

    candidate = Move(
        source=Square.from_algebraic("e7"),
        target=Square.from_algebraic("e8"),
        promotion=promotion,
    )

    assert is_pseudo_legal_move(
        board,
        candidate,
        Color.WHITE,
    )


def test_pawn_cannot_reach_last_rank_without_promotion() -> None:
    board = Board.empty().with_piece(
        Square.from_algebraic("e7"),
        Piece(Color.WHITE, PieceType.PAWN),
    )

    assert not is_pseudo_legal_move(
        board,
        move("e7", "e8"),
        Color.WHITE,
    )
