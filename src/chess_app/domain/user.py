# src/chess_app/domain/user.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class User:
    """Represent a user account."""

    user_id: UUID
    username: str
    created_at: datetime

    def __post_init__(self) -> None:
        """Validate the user data."""
        if not self.username.strip():
            raise ValueError("username cannot be empty")

        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
