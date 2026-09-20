# tests/infrastructure/test_sqlite_user_repository.py

import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from chess_app.domain.user import User
from chess_app.infrastructure.persistence.sqlite_user_repository import (
    SQLiteUserRepository,
)
from chess_app.ports.user_repository import UserRepository


def make_user(
    username: str = "alice",
) -> User:
    """Create a test user."""
    return User(
        user_id=uuid4(),
        username=username,
        created_at=datetime(
            2026,
            9,
            19,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )


def test_repository_implements_protocol(
    tmp_path,
) -> None:
    """Verify the repository implements the port."""
    repository: UserRepository = SQLiteUserRepository(tmp_path / "chess.db")

    assert repository is not None


def test_database_contains_users_table(
    tmp_path,
) -> None:
    """Verify the users table is created."""
    database_path = tmp_path / "chess.db"

    SQLiteUserRepository(database_path)

    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            )
        }

    assert "users" in tables


def test_get_unknown_user_returns_none(
    tmp_path,
) -> None:
    """Return None when the user does not exist."""
    repository = SQLiteUserRepository(tmp_path / "chess.db")

    assert repository.get(uuid4()) is None


def test_get_unknown_username_returns_none(
    tmp_path,
) -> None:
    """Return None when the username does not exist."""
    repository = SQLiteUserRepository(tmp_path / "chess.db")

    assert repository.get_by_username("alice") is None


def test_save_and_get_user(
    tmp_path,
) -> None:
    """Persist and retrieve a user."""
    repository = SQLiteUserRepository(tmp_path / "chess.db")

    user = make_user()

    repository.save(user)

    assert repository.get(user.user_id) == user


def test_get_by_username(
    tmp_path,
) -> None:
    """Retrieve a user by username."""
    repository = SQLiteUserRepository(tmp_path / "chess.db")

    user = make_user("alice")

    repository.save(user)

    assert repository.get_by_username("alice") == user


def test_save_updates_existing_user(
    tmp_path,
) -> None:
    """Update a user without creating a second row."""
    repository = SQLiteUserRepository(tmp_path / "chess.db")

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


def test_username_must_be_unique(
    tmp_path,
) -> None:
    """Reject two users with the same username."""
    repository = SQLiteUserRepository(tmp_path / "chess.db")

    first = make_user("alice")
    second = make_user("alice")

    repository.save(first)

    with pytest.raises(ValueError):
        repository.save(second)


def test_repository_can_be_reopened(
    tmp_path,
) -> None:
    """Verify persistence across repository instances."""
    database_path = tmp_path / "chess.db"

    user = make_user()

    first_repository = SQLiteUserRepository(database_path)

    first_repository.save(user)

    second_repository = SQLiteUserRepository(database_path)

    assert second_repository.get(user.user_id) == user
