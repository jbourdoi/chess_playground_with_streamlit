# src/chess_app/application/context.py

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserContext:
    """Represent the identity of the current user."""

    user_id: UUID
    username: str

    def __post_init__(self) -> None:
        """Validate the user context."""
        if not self.username.strip():
            raise ValueError("username cannot be empty")


@dataclass(frozen=True, slots=True)
class ApplicationContext:
    """Represent the execution context of an application request."""

    user: UserContext
    session_id: UUID
