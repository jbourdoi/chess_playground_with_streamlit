from __future__ import annotations

from uuid import UUID

from chess_app.application.session import Session


class InMemorySessionRepository:
    """Store sessions in process memory."""

    def __init__(self) -> None:
        """Initialize an empty session repository."""
        self._sessions: dict[UUID, Session] = {}
        self._token_index: dict[str, UUID] = {}

    def get_by_token_hash(
        self,
        token_hash: str,
    ) -> Session | None:
        """Retrieve a session by its token hash."""
        session_id = self._token_index.get(token_hash)

        if session_id is None:
            return None

        return self._sessions.get(session_id)

    def save(
        self,
        session: Session,
        token_hash: str,
    ) -> None:
        """Store or replace a session."""
        previous_token_hash = next(
            (
                current_hash
                for current_hash, session_id in self._token_index.items()
                if session_id == session.session_id
            ),
            None,
        )

        if previous_token_hash is not None:
            del self._token_index[previous_token_hash]

        existing_session_id = self._token_index.get(token_hash)

        if (
            existing_session_id is not None
            and existing_session_id != session.session_id
        ):
            raise ValueError(
                "token hash is already associated with another session"
            )

        self._sessions[session.session_id] = session
        self._token_index[token_hash] = session.session_id

    def delete(self, session_id: UUID) -> None:
        """Delete a session."""
        self._sessions.pop(session_id, None)

        token_hash = next(
            (
                current_hash
                for current_hash, current_id in self._token_index.items()
                if current_id == session_id
            ),
            None,
        )

        if token_hash is not None:
            del self._token_index[token_hash]
