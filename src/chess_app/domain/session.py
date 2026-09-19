# src/chess_app/domain/session.py

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Session:
    """Represent an authenticated user session."""

    session_id: UUID
    user_id: UUID
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime

    def __post_init__(self) -> None:
        """Validate session timestamps."""
        timestamps = (
            self.created_at,
            self.last_seen_at,
            self.expires_at,
        )

        if any(timestamp.tzinfo is None for timestamp in timestamps):
            raise ValueError("session timestamps must be timezone-aware")

        if self.last_seen_at < self.created_at:
            raise ValueError("last_seen_at cannot be before created_at")

        if self.expires_at <= self.created_at:
            raise ValueError("expires_at must be after created_at")

    def is_expired(self, now: datetime) -> bool:
        """Return whether the session has expired."""
        return now >= self.expires_at

    def touch(self, now: datetime) -> Session:
        """Return a new session with an updated last-seen timestamp."""
        if self.is_expired(now):
            raise ValueError("cannot touch an expired session")

        if now < self.last_seen_at:
            raise ValueError("last_seen_at cannot move backwards")

        return replace(
            self,
            last_seen_at=now,
        )
