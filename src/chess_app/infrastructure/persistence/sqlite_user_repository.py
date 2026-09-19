# src/chess_app/infrastructure/persistence/sqlite_user_repository.py

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from uuid import UUID

from chess_app.domain.user import User

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username
    ON users(username);
"""


class SQLiteUserRepositoryError(Exception):
    """Raised when a persisted user cannot be read or written."""


class SQLiteUserRepository:
    """Persist users in SQLite."""

    def __init__(self, database_path: str | Path) -> None:
        """
        Initialize the SQLite user repository.

        Create the database directory and schema when necessary.
        """
        self._database_path = Path(database_path)

        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_schema()

    def get(self, user_id: UUID) -> User | None:
        """
        Retrieve a user by identifier.

        Return None when the user does not exist.
        """
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT
                        user_id,
                        username,
                        created_at
                    FROM users
                    WHERE user_id = ?
                    """,
                    (str(user_id),),
                ).fetchone()

        except sqlite3.Error as exc:
            raise SQLiteUserRepositoryError(
                f"failed to read user: {user_id}"
            ) from exc

        if row is None:
            return None

        return self._build_user(row)

    def get_by_username(
        self,
        username: str,
    ) -> User | None:
        """
        Retrieve a user by username.

        Return None when the username does not exist.
        """
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT
                        user_id,
                        username,
                        created_at
                    FROM users
                    WHERE username = ?
                    """,
                    (username,),
                ).fetchone()

        except sqlite3.Error as exc:
            raise SQLiteUserRepositoryError(
                f"failed to read user: {username}"
            ) from exc

        if row is None:
            return None

        return self._build_user(row)

    def save(self, user: User) -> None:
        """Store or replace a user."""
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO users (
                        user_id,
                        username,
                        created_at
                    )
                    VALUES (?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        username = excluded.username,
                        created_at = excluded.created_at
                    """,
                    (
                        str(user.user_id),
                        user.username,
                        user.created_at.isoformat(),
                    ),
                )

        except sqlite3.IntegrityError as exc:
            raise ValueError(
                f"username already exists: {user.username}"
            ) from exc

        except sqlite3.Error as exc:
            raise SQLiteUserRepositoryError(
                f"failed to save user: {user.user_id}"
            ) from exc

    def _initialize_schema(self) -> None:
        """Create the SQLite schema if necessary."""
        try:
            with self._connect() as connection:
                connection.executescript(_SCHEMA)

        except sqlite3.Error as exc:
            raise SQLiteUserRepositoryError(
                "failed to initialize user schema"
            ) from exc

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        """Open a short-lived SQLite connection."""
        connection = sqlite3.connect(
            self._database_path,
        )
        connection.row_factory = sqlite3.Row

        try:
            yield connection
            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    @staticmethod
    def _build_user(
        row: sqlite3.Row,
    ) -> User:
        """Build a domain user from a database row."""
        try:
            created_at = _parse_datetime(row["created_at"])

            return User(
                user_id=UUID(row["user_id"]),
                username=row["username"],
                created_at=created_at,
            )

        except ValueError as exc:
            raise SQLiteUserRepositoryError(
                "persisted user contains invalid data"
            ) from exc


def _parse_datetime(value: str) -> datetime:
    """Parse a stored ISO-8601 datetime."""

    return datetime.fromisoformat(value)
