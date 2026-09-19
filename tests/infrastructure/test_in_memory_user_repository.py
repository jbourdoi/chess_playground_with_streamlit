from datetime import datetime, timezone
from uuid import uuid4

import pytest

from chess_app.domain.user import User
from chess_app.infrastructure.persistence.in_memory_user_repository import (
    InMemoryUserRepository,
)
from chess_app.ports.user import UserRepository


def make_user(
    username: str = "alice",
) -> User:
    """Create a test user."""
    return User(
        user_id=uuid4(),
        username=username,
        created_at=datetime.now(timezone.utc),
    )


def test_empty_repository_returns_none() -> None:
    repository = InMemoryUserRepository()

    assert repository.get(uuid4()) is None
    assert repository.get_by_username("alice") is None


def test_save_and_get_user() -> None:
    repository = InMemoryUserRepository()
    user = make_user()

    repository.save(user)

    assert repository.get(user.user_id) == user


def test_get_by_username() -> None:
    repository = InMemoryUserRepository()
    user = make_user("alice")

    repository.save(user)

    assert repository.get_by_username("alice") == user


def test_same_user_can_be_updated() -> None:
    repository = InMemoryUserRepository()
    user = make_user("alice")

    repository.save(user)

    updated = User(
        user_id=user.user_id,
        username="alice-updated",
        created_at=user.created_at,
    )

    repository.save(updated)

    assert repository.get(user.user_id) == updated
    assert repository.get_by_username("alice") is None
    assert repository.get_by_username("alice-updated") == updated


def test_username_cannot_be_shared() -> None:
    repository = InMemoryUserRepository()

    first = make_user("alice")
    second = make_user("alice")

    repository.save(first)

    with pytest.raises(ValueError):
        repository.save(second)


def test_repository_implements_protocol() -> None:
    repository: UserRepository = InMemoryUserRepository()

    assert repository is not None
