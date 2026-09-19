# src/chess_app/ports/session_repository.py

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from chess_app.domain.session import Session


class SessionRepository(Protocol):
    """Define persistence operations for user sessions."""

    def get_by_token_hash(
        self,
        token_hash: str,
    ) -> Session | None:
        """
        Retrieve a session by its token hash.

        Return None when the token is unknown.
        """
        ...

    def save(
        self,
        session: Session,
        token_hash: str,
    ) -> None:
        """Store or replace a session."""
        ...

    def delete(self, session_id: UUID) -> None:
        """Delete a session by its identifier."""
        ...
