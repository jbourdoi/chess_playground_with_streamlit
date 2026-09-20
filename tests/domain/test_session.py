# tests/domain/test_session.py

from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from chess_app.domain.session import Session

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
