# src/chess_app/ports/view.py

from __future__ import annotations

from typing import Protocol

from chess_app.application.commands import Command
from chess_app.application.state import ApplicationState


class View(Protocol):
    """Define the presentation interface of the application."""

    def render(
        self,
        state: ApplicationState,
    ) -> None:
        """
        Render the current application state.

        Implementations may perform presentation-related side effects.
        """
        ...

    def read_command(
        self,
        state: ApplicationState,
    ) -> Command | None:
        """
        Read the next user action.

        Return None when no action is currently requested.
        """
        ...
