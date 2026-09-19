from __future__ import annotations

import hashlib
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from chess_app.domain.session import Session
from chess_app.ports.session import SessionRepository

DEFAULT_SESSION_TTL = timedelta(days=30)
SESSION_TOKEN_BYTES = 32


@dataclass(frozen=True, slots=True)
class CreatedSession:
    """Represent a newly created session and its secret token."""

    session: Session
    token: str


def generate_session_token() -> str:
    """Generate a cryptographically secure opaque session token."""
    return secrets.token_urlsafe(SESSION_TOKEN_BYTES)


def hash_session_token(token: str) -> str:
    """Return the SHA-256 hash of a session token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def utc_now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


class SessionService:
    """Coordinate session creation, authentication and revocation."""

    def __init__(
        self,
        repository: SessionRepository,
        session_id_factory: Callable[[], UUID] = uuid4,
        token_factory: Callable[[], str] = generate_session_token,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        """
        Initialize the session service.

        External dependencies are injected to keep the service
        deterministic and easy to test.
        """
        self._repository = repository
        self._session_id_factory = session_id_factory
        self._token_factory = token_factory
        self._clock = clock

    def create(
        self,
        user_id: UUID,
        ttl: timedelta = DEFAULT_SESSION_TTL,
    ) -> CreatedSession:
        """Create and persist a new user session."""
        if ttl <= timedelta(0):
            raise ValueError("session TTL must be positive")

        now = self._clock()
        token = self._token_factory()

        session = Session(
            session_id=self._session_id_factory(),
            user_id=user_id,
            created_at=now,
            last_seen_at=now,
            expires_at=now + ttl,
        )

        self._repository.save(
            session,
            hash_session_token(token),
        )

        return CreatedSession(
            session=session,
            token=token,
        )

    def authenticate(
        self,
        token: str,
    ) -> Session | None:
        """
        Resolve a session token to an active session.

        Return None when the token is invalid or expired.
        """
        if not token:
            return None

        token_hash = hash_session_token(token)
        session = self._repository.get_by_token_hash(token_hash)

        if session is None:
            return None

        now = self._clock()

        if session.is_expired(now):
            self._repository.delete(session.session_id)
            return None

        updated_session = session.touch(now)

        self._repository.save(
            updated_session,
            token_hash,
        )

        return updated_session

    def revoke(self, token: str) -> bool:
        """
        Revoke a session token.

        Return True when a session was found and deleted.
        """
        if not token:
            return False

        token_hash = hash_session_token(token)
        session = self._repository.get_by_token_hash(token_hash)

        if session is None:
            return False

        self._repository.delete(session.session_id)

        return True
