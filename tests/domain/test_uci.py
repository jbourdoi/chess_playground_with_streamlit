# tests/domain/test_uci.py

import pytest

from chess_app.domain.move import Move
from chess_app.domain.piece import PieceType
from chess_app.domain.square import Square


def test_move_to_uci_standard() -> None:
    """Ensure a standard move serializes correctly to UCI."""
    move = Move(
        source=Square.from_algebraic("e2"), target=Square.from_algebraic("e4")
    )
    assert move.uci == "e2e4"


def test_move_to_uci_promotion() -> None:
    """Ensure a promotion move includes the correct piece symbol in UCI."""
    move = Move(
        source=Square.from_algebraic("e7"),
        target=Square.from_algebraic("e8"),
        promotion=PieceType.QUEEN,
    )
    assert move.uci == "e7e8q"


def test_move_from_uci_standard() -> None:
    """Ensure a standard 4-character UCI string parses to a Move."""
    move = Move.from_uci("g1f3")
    assert move.source == Square.from_algebraic("g1")
    assert move.target == Square.from_algebraic("f3")
    assert move.promotion is None


def test_move_from_uci_promotion() -> None:
    """Ensure a 5-character UCI string parses to a promotion Move."""
    move = Move.from_uci("a7a8r")
    assert move.source == Square.from_algebraic("a7")
    assert move.target == Square.from_algebraic("a8")
    assert move.promotion is PieceType.ROOK


def test_move_from_uci_invalid_length() -> None:
    """Ensure parsing fails for strings of invalid length."""
    with pytest.raises(ValueError, match="invalid UCI move"):
        Move.from_uci("e2e4q2")

    with pytest.raises(ValueError, match="invalid UCI move"):
        Move.from_uci("e2e")


def test_move_from_uci_invalid_promotion() -> None:
    """Ensure parsing fails when the promotion character is unrecognized."""
    with pytest.raises(ValueError, match="invalid promotion in UCI move"):
        Move.from_uci("e7e8k")  # King is not a valid promotion
