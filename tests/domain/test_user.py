# tests/domain/test_user.py

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from chess_app.domain.user import User


def test_user_creation() -> None:
    created_at = datetime.now(timezone.utc)
    user_id = uuid4()

    user = User(
        user_id=user_id,
        username="alice",
        created_at=created_at,
    )

    assert user.user_id == user_id
    assert user.username == "alice"
    assert user.created_at == created_at


def test_user_rejects_empty_username() -> None:
    with pytest.raises(ValueError):
        User(
            user_id=uuid4(),
            username="   ",
            created_at=datetime.now(timezone.utc),
        )


def test_user_requires_timezone_aware_created_at() -> None:
    with pytest.raises(ValueError):
        User(
            user_id=uuid4(),
            username="alice",
            created_at=datetime(2026, 9, 19),
        )


def test_user_is_immutable() -> None:
    user = User(
        user_id=uuid4(),
        username="alice",
        created_at=datetime.now(timezone.utc),
    )

    with pytest.raises(AttributeError):
        user.username = "bob"  # type: ignore[misc]
