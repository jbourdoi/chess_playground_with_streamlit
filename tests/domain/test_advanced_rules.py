from uuid import uuid4

from chess_app.domain.board import Board
from chess_app.domain.castling import CastlingRights
from chess_app.domain.game import Game, GameStatus
from chess_app.domain.move import Move
from chess_app.domain.piece import Color, Piece, PieceType
from chess_app.domain.player import Player
from chess_app.domain.position import Square
from chess_app.domain.rules import (
    is_in_check,
    is_legal_move,
    is_stalemate,
)


def move(source: str, target: str) -> Move:
    """Build a move from algebraic notation."""
    return Move(
        source=Square.from_algebraic(source),
        target=Square.from_algebraic(target),
    )


def test_king_is_in_check() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("e1"),
            Piece(Color.WHITE, PieceType.KING),
        )
        .with_piece(
            Square.from_algebraic("e8"),
            Piece(Color.BLACK, PieceType.ROOK),
        )
    )

    assert is_in_check(board, Color.WHITE)


def test_king_is_not_in_check() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("e1"),
            Piece(Color.WHITE, PieceType.KING),
        )
        .with_piece(
            Square.from_algebraic("a8"),
            Piece(Color.BLACK, PieceType.ROOK),
        )
    )

    assert not is_in_check(board, Color.WHITE)


def test_king_cannot_move_into_check() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("e1"),
            Piece(Color.WHITE, PieceType.KING),
        )
        .with_piece(
            Square.from_algebraic("e8"),
            Piece(Color.BLACK, PieceType.ROOK),
        )
    )

    assert not is_legal_move(
        board,
        move("e1", "e2"),
        Color.WHITE,
    )


def test_pinned_piece_cannot_expose_king() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("e1"),
            Piece(Color.WHITE, PieceType.KING),
        )
        .with_piece(
            Square.from_algebraic("e2"),
            Piece(Color.WHITE, PieceType.ROOK),
        )
        .with_piece(
            Square.from_algebraic("e8"),
            Piece(Color.BLACK, PieceType.ROOK),
        )
    )

    assert not is_legal_move(
        board,
        move("e2", "a2"),
        Color.WHITE,
    )


def test_white_can_castle_kingside() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("e1"),
            Piece(Color.WHITE, PieceType.KING),
        )
        .with_piece(
            Square.from_algebraic("h1"),
            Piece(Color.WHITE, PieceType.ROOK),
        )
    )

    assert is_legal_move(
        board,
        move("e1", "g1"),
        Color.WHITE,
        CastlingRights.initial(),
    )


def test_white_can_castle_queenside() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("e1"),
            Piece(Color.WHITE, PieceType.KING),
        )
        .with_piece(
            Square.from_algebraic("a1"),
            Piece(Color.WHITE, PieceType.ROOK),
        )
    )

    assert is_legal_move(
        board,
        move("e1", "c1"),
        Color.WHITE,
        CastlingRights.initial(),
    )


def test_castling_cannot_cross_attacked_square() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("e1"),
            Piece(Color.WHITE, PieceType.KING),
        )
        .with_piece(
            Square.from_algebraic("h1"),
            Piece(Color.WHITE, PieceType.ROOK),
        )
        .with_piece(
            Square.from_algebraic("f8"),
            Piece(Color.BLACK, PieceType.ROOK),
        )
    )

    assert not is_legal_move(
        board,
        move("e1", "g1"),
        Color.WHITE,
        CastlingRights.initial(),
    )


def test_en_passant_is_legal() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("e1"),
            Piece(Color.WHITE, PieceType.KING),
        )
        .with_piece(
            Square.from_algebraic("e5"),
            Piece(Color.WHITE, PieceType.PAWN),
        )
        .with_piece(
            Square.from_algebraic("d5"),
            Piece(Color.BLACK, PieceType.PAWN),
        )
        .with_piece(
            Square.from_algebraic("e8"),
            Piece(Color.BLACK, PieceType.KING),
        )
    )

    assert is_legal_move(
        board,
        move("e5", "d6"),
        Color.WHITE,
        CastlingRights.none(),
        Square.from_algebraic("d6"),
    )


def test_en_passant_removes_captured_pawn() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("e5"),
            Piece(Color.WHITE, PieceType.PAWN),
        )
        .with_piece(
            Square.from_algebraic("d5"),
            Piece(Color.BLACK, PieceType.PAWN),
        )
    )

    new_board = board.move_piece(
        move("e5", "d6"),
        Square.from_algebraic("d6"),
    )

    assert new_board.piece_at(Square.from_algebraic("d5")) is None

    assert new_board.piece_at(Square.from_algebraic("d6")) == Piece(
        Color.WHITE, PieceType.PAWN
    )


def test_fools_mate_is_checkmate() -> None:

    white = Player(
        player_id=uuid4(),
        name="White",
        color=Color.WHITE,
    )

    black = Player(
        player_id=uuid4(),
        name="Black",
        color=Color.BLACK,
    )

    game = Game.new(
        game_id=uuid4(),
        white_player=white,
        black_player=black,
    )

    game = game.play(move("f2", "f3"))
    game = game.play(move("e7", "e5"))
    game = game.play(move("g2", "g4"))
    game = game.play(move("d8", "h4"))

    assert game.status is GameStatus.BLACK_WON
    assert game.in_check
    assert game.legal_moves == ()


def test_stalemate() -> None:
    board = (
        Board.empty()
        .with_piece(
            Square.from_algebraic("h1"),
            Piece(Color.WHITE, PieceType.KING),
        )
        .with_piece(
            Square.from_algebraic("f2"),
            Piece(Color.BLACK, PieceType.KING),
        )
        .with_piece(
            Square.from_algebraic("g3"),
            Piece(Color.BLACK, PieceType.QUEEN),
        )
    )

    assert not is_in_check(board, Color.WHITE)

    assert is_stalemate(
        board,
        Color.WHITE,
        CastlingRights.none(),
    )
