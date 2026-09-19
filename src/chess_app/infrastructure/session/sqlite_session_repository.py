# src/chess_app/infrastructure/session/sqlite_session_repository.py

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from uuid import UUID

from chess_app.domain.session import Session

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_token_hash
    ON sessions(token_hash);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id
    ON sessions(user_id);
"""


class SQLiteSessionRepositoryError(Exception):
    """Raised when a persisted session cannot be read or written."""


class SQLiteSessionRepository:
    """Persist user sessions in SQLite."""

    def __init__(self, database_path: str | Path) -> None:
        """
        Initialize the SQLite session repository.

        The users table must exist before a session can be saved.
        """
        self._database_path = Path(database_path)

        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_schema()

    def get_by_token_hash(
        self,
        token_hash: str,
    ) -> Session | None:
        """
        Retrieve a session by token hash.

        Return None when the token is unknown.
        """
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT
                        session_id,
                        user_id,
                        created_at,
                        last_seen_at,
                        expires_at
                    FROM sessions
                    WHERE token_hash = ?
                    """,
                    (token_hash,),
                ).fetchone()

        except sqlite3.Error as exc:
            raise SQLiteSessionRepositoryError(
                "failed to read session"
            ) from exc

        if row is None:
            return None

        return self._build_session(row)

    def save(
        self,
        session: Session,
        token_hash: str,
    ) -> None:
        """Store or replace a session."""
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO sessions (
                        session_id,
                        user_id,
                        token_hash,
                        created_at,
                        last_seen_at,
                        expires_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(session_id) DO UPDATE SET
                        user_id = excluded.user_id,
                        token_hash = excluded.token_hash,
                        created_at = excluded.created_at,
                        last_seen_at = excluded.last_seen_at,
                        expires_at = excluded.expires_at
                    """,
                    (
                        str(session.session_id),
                        str(session.user_id),
                        token_hash,
                        session.created_at.isoformat(),
                        session.last_seen_at.isoformat(),
                        session.expires_at.isoformat(),
                    ),
                )

        except sqlite3.IntegrityError as exc:
            if "token_hash" in str(exc):
                raise ValueError(
                    "token hash is already associated with another session"
                ) from exc

            if "FOREIGN KEY" in str(exc):
                raise ValueError(
                    f"user does not exist: {session.user_id}"
                ) from exc

            raise SQLiteSessionRepositoryError(
                f"failed to save session: {session.session_id}"
            ) from exc

        except sqlite3.Error as exc:
            raise SQLiteSessionRepositoryError(
                f"failed to save session: {session.session_id}"
            ) from exc

    def delete(self, session_id: UUID) -> None:
        """Delete a session by identifier."""
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    DELETE FROM sessions
                    WHERE session_id = ?
                    """,
                    (str(session_id),),
                )

        except sqlite3.Error as exc:
            raise SQLiteSessionRepositoryError(
                f"failed to delete session: {session_id}"
            ) from exc

    def _initialize_schema(self) -> None:
        """Create the SQLite schema if necessary."""
        try:
            with self._connect() as connection:
                connection.executescript(_SCHEMA)

        except sqlite3.Error as exc:
            raise SQLiteSessionRepositoryError(
                "failed to initialize session schema"
            ) from exc

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        """Open a short-lived SQLite connection."""
        connection = sqlite3.connect(
            self._database_path,
        )
        connection.row_factory = sqlite3.Row

        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")

        try:
            yield connection
            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    @staticmethod
    def _build_session(
        row: sqlite3.Row,
    ) -> Session:
        """Build a domain session from a database row."""
        try:
            return Session(
                session_id=UUID(row["session_id"]),
                user_id=UUID(row["user_id"]),
                created_at=_parse_datetime(row["created_at"]),
                last_seen_at=_parse_datetime(row["last_seen_at"]),
                expires_at=_parse_datetime(row["expires_at"]),
            )

        except ValueError as exc:
            raise SQLiteSessionRepositoryError(
                "persisted session contains invalid data"
            ) from exc


def _parse_datetime(value: str) -> datetime:
    """Parse a stored ISO-8601 datetime."""
    return datetime.fromisoformat(value)
