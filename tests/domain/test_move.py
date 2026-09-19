# tests/domain/test_move.py

import pytest

from chess_app.domain.move import Move
from chess_app.domain.piece import PieceType
from chess_app.domain.square import Square


def test_move_rejects_same_source_and_target() -> None:
    square = Square.from_algebraic("e4")

    with pytest.raises(ValueError):
        Move(source=square, target=square)


def test_move_uci() -> None:
    move = Move(
        source=Square.from_algebraic("e2"),
        target=Square.from_algebraic("e4"),
    )

    assert move.uci == "e2e4"


@pytest.mark.parametrize(
    ("piece_type", "suffix"),
    [
        (PieceType.QUEEN, "q"),
        (PieceType.ROOK, "r"),
        (PieceType.BISHOP, "b"),
        (PieceType.KNIGHT, "n"),
    ],
)
def test_promotion_uci(
    piece_type: PieceType,
    suffix: str,
) -> None:
    move = Move(
        source=Square.from_algebraic("e7"),
        target=Square.from_algebraic("e8"),
        promotion=piece_type,
    )

    assert move.uci == f"e7e8{suffix}"
