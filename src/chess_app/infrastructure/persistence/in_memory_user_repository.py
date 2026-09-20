# src/chess_app/infrastructure/persistence/in_memory_user_repository.py

from __future__ import annotations

from uuid import UUID

from chess_app.domain.user import User


class InMemoryUserRepository:
    """Store users in process memory."""

    def __init__(self) -> None:
        """Initialize an empty repository."""
        self._users: dict[UUID, User] = {}
        self._username_index: dict[str, UUID] = {}

    def get(self, user_id: UUID) -> User | None:
        """Retrieve a user by identifier."""
        return self._users.get(user_id)

    def get_by_username(
        self,
        username: str,
    ) -> User | None:
        """Retrieve a user by username."""
        user_id = self._username_index.get(username)

        if user_id is None:
            return None

        return self._users.get(user_id)

    def save(self, user: User) -> None:
        """Store or replace a user."""
        existing_id = self._username_index.get(user.username)

        if existing_id is not None and existing_id != user.user_id:
            raise ValueError(f"username already exists: {user.username}")

        previous_user = self._users.get(user.user_id)

        if (
            previous_user is not None
            and previous_user.username != user.username
        ):
            del self._username_index[previous_user.username]

        self._users[user.user_id] = user
        self._username_index[user.username] = user.user_id
