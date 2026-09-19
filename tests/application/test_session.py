# tests/application/test_session.py

from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from chess_app.application.session_service import (
    SessionService,
    hash_session_token,
)
from chess_app.domain.session import Session
from chess_app.infrastructure.session.in_memory_session import (
    InMemorySessionRepository,
)

NOW = datetime(
    2026,
    9,
    19,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)

SESSION_ID = UUID("11111111-1111-1111-1111-111111111111")

USER_ID = UUID("22222222-2222-2222-2222-222222222222")


def make_session() -> Session:
    """Create a deterministic test session."""
    return Session(
        session_id=SESSION_ID,
        user_id=USER_ID,
        created_at=NOW,
        last_seen_at=NOW,
        expires_at=NOW + timedelta(days=1),
    )


def test_session_is_not_expired() -> None:
    session = make_session()

    assert not session.is_expired(NOW)


def test_session_is_expired_at_expiration_time() -> None:
    session = make_session()
    expiration = NOW + timedelta(days=1)

    assert session.is_expired(expiration)


def test_touch_returns_new_session() -> None:
    session = make_session()
    later = NOW + timedelta(minutes=5)

    updated = session.touch(later)

    assert updated is not session
    assert session.last_seen_at == NOW
    assert updated.last_seen_at == later


def test_touch_cannot_move_backwards() -> None:
    session = make_session()

    with pytest.raises(ValueError):
        session.touch(NOW - timedelta(minutes=1))


def test_expired_session_cannot_be_touched() -> None:
    session = make_session()
    expiration = NOW + timedelta(days=1)

    with pytest.raises(ValueError):
        session.touch(expiration)


def test_session_requires_timezone_aware_dates() -> None:
    with pytest.raises(ValueError):
        Session(
            session_id=SESSION_ID,
            user_id=USER_ID,
            created_at=datetime(2026, 9, 19),
            last_seen_at=NOW,
            expires_at=NOW + timedelta(days=1),
        )


def test_token_hash_is_deterministic() -> None:
    token = "example-session-token"

    assert hash_session_token(token) == hash_session_token(token)


def test_token_hash_is_not_the_plain_token() -> None:
    token = "example-session-token"

    assert hash_session_token(token) != token


def test_create_session() -> None:
    repository = InMemorySessionRepository()

    session_id = UUID("33333333-3333-3333-3333-333333333333")

    service = SessionService(
        repository=repository,
        session_id_factory=lambda: session_id,
        token_factory=lambda: "secret-token",
        clock=lambda: NOW,
    )

    created = service.create(USER_ID)

    assert created.session.session_id == session_id
    assert created.session.user_id == USER_ID
    assert created.token == "secret-token"

    stored = repository.get_by_token_hash(hash_session_token("secret-token"))

    assert stored == created.session


def test_authenticate_valid_token() -> None:
    repository = InMemorySessionRepository()

    service = SessionService(
        repository=repository,
        session_id_factory=lambda: SESSION_ID,
        token_factory=lambda: "secret-token",
        clock=lambda: NOW,
    )

    created = service.create(USER_ID)

    session = service.authenticate(created.token)

    assert session == created.session


def test_authenticate_unknown_token() -> None:
    repository = InMemorySessionRepository()
    service = SessionService(
        repository=repository,
        clock=lambda: NOW,
    )

    assert service.authenticate("unknown-token") is None


def test_authenticate_expired_session() -> None:
    repository = InMemorySessionRepository()

    current_time = NOW

    service = SessionService(
        repository=repository,
        session_id_factory=lambda: SESSION_ID,
        token_factory=lambda: "secret-token",
        clock=lambda: current_time,
    )

    created = service.create(
        USER_ID,
        ttl=timedelta(hours=1),
    )

    current_time = NOW + timedelta(hours=1)

    assert service.authenticate(created.token) is None

    assert (
        repository.get_by_token_hash(hash_session_token(created.token)) is None
    )


def test_authenticate_updates_last_seen() -> None:
    repository = InMemorySessionRepository()

    current_time = NOW

    service = SessionService(
        repository=repository,
        session_id_factory=lambda: SESSION_ID,
        token_factory=lambda: "secret-token",
        clock=lambda: current_time,
    )

    created = service.create(USER_ID)

    current_time = NOW + timedelta(minutes=10)

    session = service.authenticate(created.token)

    assert session is not None
    assert session.last_seen_at == current_time


def test_revoke_session() -> None:
    repository = InMemorySessionRepository()

    service = SessionService(
        repository=repository,
        session_id_factory=lambda: SESSION_ID,
        token_factory=lambda: "secret-token",
        clock=lambda: NOW,
    )

    created = service.create(USER_ID)

    assert service.revoke(created.token)

    assert service.authenticate(created.token) is None


def test_revoke_unknown_token() -> None:
    repository = InMemorySessionRepository()

    service = SessionService(
        repository=repository,
        clock=lambda: NOW,
    )

    assert not service.revoke("unknown-token")
