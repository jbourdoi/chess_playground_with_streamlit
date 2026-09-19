import pytest

from chess_app.domain.position import Square


@pytest.mark.parametrize(
    ("notation", "file", "rank"),
    [
        ("a1", 0, 0),
        ("e4", 4, 3),
        ("h8", 7, 7),
    ],
)
def test_from_algebraic(
    notation: str,
    file: int,
    rank: int,
) -> None:
    square = Square.from_algebraic(notation)

    assert square.file == file
    assert square.rank == rank
    assert square.algebraic == notation


@pytest.mark.parametrize(
    "notation",
    [
        "",
        "a",
        "a10",
        "abc",
    ],
)
def test_invalid_algebraic_length(notation: str) -> None:
    with pytest.raises(ValueError):
        Square.from_algebraic(notation)


@pytest.mark.parametrize(
    "notation",
    [
        "i1",
        "a0",
        "a9",
        "z8",
    ],
)
def test_invalid_algebraic_coordinates(notation: str) -> None:
    with pytest.raises(ValueError):
        Square.from_algebraic(notation)


def test_square_is_immutable() -> None:
    square = Square.from_algebraic("e4")

    with pytest.raises(AttributeError):
        square.file = 3  # type: ignore[misc]


@pytest.mark.parametrize(
    ("notation", "file_delta", "rank_delta", "expected"),
    [
        ("e4", 1, 0, "f4"),
        ("e4", -1, 2, "d6"),
        ("e4", 0, -3, "e1"),
        ("a1", -1, 0, None),
        ("h8", 0, 1, None),
    ],
)
def test_offset(
    notation: str,
    file_delta: int,
    rank_delta: int,
    expected: str | None,
) -> None:
    square = Square.from_algebraic(notation)
    result = square.offset(file_delta, rank_delta)

    if expected is None:
        assert result is None
    else:
        assert result is not None
        assert result.algebraic == expected
