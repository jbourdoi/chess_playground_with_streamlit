# tests/infrastructure/test_in_memory_session_repository.py

from datetime import timedelta
from uuid import uuid4

from chess_app.domain.session import Session
from chess_app.infrastructure.session.in_memory_session_repository import (
    InMemorySessionRepository,
)
from chess_app.ports.session_repository import SessionRepository


def make_session() -> Session:
    """Create a test session."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    return Session(
        session_id=uuid4(),
        user_id=uuid4(),
        created_at=now,
        last_seen_at=now,
        expires_at=now + timedelta(days=1),
    )


def test_unknown_token_hash_returns_none() -> None:
    repository = InMemorySessionRepository()

    assert repository.get_by_token_hash("unknown") is None


def test_save_and_get_session() -> None:
    repository = InMemorySessionRepository()
    session = make_session()

    repository.save(session, "hash")

    assert repository.get_by_token_hash("hash") == session


def test_delete_session() -> None:
    repository = InMemorySessionRepository()
    session = make_session()

    repository.save(session, "hash")
    repository.delete(session.session_id)

    assert repository.get_by_token_hash("hash") is None


def test_same_session_can_update_token_hash() -> None:
    repository = InMemorySessionRepository()
    session = make_session()

    repository.save(session, "old-hash")
    repository.save(session, "new-hash")

    assert repository.get_by_token_hash("old-hash") is None
    assert repository.get_by_token_hash("new-hash") == session


def test_token_hash_cannot_be_shared() -> None:
    repository = InMemorySessionRepository()

    first = make_session()
    second = make_session()

    repository.save(first, "same-hash")

    try:
        repository.save(second, "same-hash")
    except ValueError:
        pass
    else:
        raise AssertionError("a token hash cannot belong to two sessions")


def test_repository_implements_protocol() -> None:
    repository: SessionRepository = InMemorySessionRepository()

    assert repository is not None
