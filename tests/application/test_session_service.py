# tests/application/test_session_service.py

from datetime import datetime, timedelta, timezone
from uuid import UUID

from chess_app.application.session_service import (
    SessionService,
    hash_session_token,
)
from chess_app.domain.user import User
from chess_app.infrastructure.persistence.sqlite_user_repository import (
    SQLiteUserRepository,
)
from chess_app.infrastructure.session.in_memory_session_repository import (
    InMemorySessionRepository,
)
from chess_app.infrastructure.session.sqlite_session_repository import (
    SQLiteSessionRepository,
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


def test_session_service_works_with_sqlite(
    tmp_path,
) -> None:
    """Use SessionService with the SQLite adapter."""
    from uuid import uuid4

    database_path = tmp_path / "chess.db"

    user_repository = SQLiteUserRepository(database_path)

    user_id = uuid4()

    user = User(
        user_id=user_id,
        username="alice",
        created_at=NOW,
    )

    user_repository.save(user)

    session_repository = SQLiteSessionRepository(database_path)

    service = SessionService(
        repository=session_repository,
        session_id_factory=lambda: SESSION_ID,
        token_factory=lambda: "secret-token",
        clock=lambda: NOW,
    )

    created = service.create(user_id)

    restored = service.authenticate(created.token)

    assert restored == created.session
