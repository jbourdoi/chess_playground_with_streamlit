# src/chess_app/ports/user.py

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from chess_app.domain.user import User


class UserRepository(Protocol):
    """Define persistence operations for users."""

    def get(self, user_id: UUID) -> User | None:
        """
        Retrieve a user by identifier.

        Return None when the user does not exist.
        """
        ...

    def get_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by username.

        Return None when the username does not exist.
        """
        ...

    def save(self, user: User) -> None:
        """Store or replace a user."""
        ...
