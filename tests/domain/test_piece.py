from chess_app.domain.piece import Color, Piece, PieceType


def test_color_opposite() -> None:
    assert Color.WHITE.opposite is Color.BLACK
    assert Color.BLACK.opposite is Color.WHITE


def test_piece_is_immutable() -> None:
    piece = Piece(Color.WHITE, PieceType.KING)

    try:
        piece.color = Color.BLACK  # type: ignore[misc]
    except AttributeError:
        pass
    else:
        raise AssertionError("Piece should be immutable")


def test_white_king_symbol() -> None:
    piece = Piece(Color.WHITE, PieceType.KING)

    assert piece.symbol == "♔"


def test_black_queen_symbol() -> None:
    piece = Piece(Color.BLACK, PieceType.QUEEN)

    assert piece.symbol == "♛"
