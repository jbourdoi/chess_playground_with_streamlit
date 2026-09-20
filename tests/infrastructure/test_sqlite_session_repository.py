# tests/infrastructure/test_sqlite_session_repository.py

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from chess_app.domain.session import Session
from chess_app.domain.user import User
from chess_app.infrastructure.persistence.sqlite_user_repository import (
    SQLiteUserRepository,
)
from chess_app.infrastructure.session.sqlite_session_repository import (
    SQLiteSessionRepository,
)
from chess_app.ports.session_repository import SessionRepository

NOW = datetime(
    2026,
    9,
    19,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)


def make_user() -> User:
    """Create a test user."""
    return User(
        user_id=uuid4(),
        username="alice",
        created_at=NOW,
    )


def make_session(
    user_id,
) -> Session:
    """Create a test session."""
    return Session(
        session_id=uuid4(),
        user_id=user_id,
        created_at=NOW,
        last_seen_at=NOW,
        expires_at=NOW + timedelta(days=1),
    )


def setup_repositories(tmp_path):
    """Create user and session repositories."""
    database_path = tmp_path / "chess.db"

    user_repository = SQLiteUserRepository(database_path)

    session_repository = SQLiteSessionRepository(database_path)

    return user_repository, session_repository


def test_repository_implements_protocol(
    tmp_path,
) -> None:
    """Verify the repository implements the port."""
    _, session_repository = setup_repositories(tmp_path)

    repository: SessionRepository = session_repository

    assert repository is not None


def test_unknown_token_hash_returns_none(
    tmp_path,
) -> None:
    """Return None for an unknown token."""
    _, repository = setup_repositories(tmp_path)

    assert repository.get_by_token_hash("unknown") is None


def test_save_and_get_session(
    tmp_path,
) -> None:
    """Persist and retrieve a session."""
    user_repository, session_repository = setup_repositories(tmp_path)

    user = make_user()
    user_repository.save(user)

    session = make_session(user.user_id)

    session_repository.save(
        session,
        "token-hash",
    )

    restored = session_repository.get_by_token_hash("token-hash")

    assert restored == session


def test_delete_session(
    tmp_path,
) -> None:
    """Delete a session."""
    user_repository, session_repository = setup_repositories(tmp_path)

    user = make_user()
    user_repository.save(user)

    session = make_session(user.user_id)

    session_repository.save(
        session,
        "token-hash",
    )

    session_repository.delete(session.session_id)

    assert session_repository.get_by_token_hash("token-hash") is None


def test_save_updates_session(
    tmp_path,
) -> None:
    """Update an existing session."""
    user_repository, session_repository = setup_repositories(tmp_path)

    user = make_user()
    user_repository.save(user)

    session = make_session(user.user_id)

    session_repository.save(
        session,
        "old-token",
    )

    updated = Session(
        session_id=session.session_id,
        user_id=session.user_id,
        created_at=session.created_at,
        last_seen_at=NOW + timedelta(minutes=5),
        expires_at=session.expires_at,
    )

    session_repository.save(
        updated,
        "new-token",
    )

    assert session_repository.get_by_token_hash("old-token") is None

    assert session_repository.get_by_token_hash("new-token") == updated


def test_token_hash_must_be_unique(
    tmp_path,
) -> None:
    """Reject reuse of a token hash."""
    user_repository, session_repository = setup_repositories(tmp_path)

    user = make_user()
    user_repository.save(user)

    first = make_session(user.user_id)
    second = make_session(user.user_id)

    session_repository.save(
        first,
        "same-token",
    )

    with pytest.raises(ValueError):
        session_repository.save(
            second,
            "same-token",
        )


def test_session_requires_existing_user(
    tmp_path,
) -> None:
    """Reject a session referencing an unknown user."""
    _, session_repository = setup_repositories(tmp_path)

    session = make_session(uuid4())

    with pytest.raises(ValueError):
        session_repository.save(
            session,
            "token-hash",
        )


def test_repository_can_be_reopened(
    tmp_path,
) -> None:
    """Verify persistence across repository instances."""
    database_path = tmp_path / "chess.db"

    user = make_user()
    session = make_session(user.user_id)

    user_repository = SQLiteUserRepository(database_path)
    user_repository.save(user)

    first_repository = SQLiteSessionRepository(database_path)
    first_repository.save(
        session,
        "token-hash",
    )

    second_repository = SQLiteSessionRepository(database_path)

    restored = second_repository.get_by_token_hash("token-hash")

    assert restored == session
