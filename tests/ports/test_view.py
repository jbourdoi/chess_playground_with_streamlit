# tests/ports/test_view.py

from uuid import uuid4

from chess_app.application.commands import (
    PlayMove,
)
from chess_app.application.state import ApplicationState
from chess_app.domain.move import Move
from chess_app.domain.square import Square
from chess_app.ports.view import View


class StubView:
    """Minimal view implementation for testing."""

    def __init__(self) -> None:
        self.last_state: ApplicationState | None = None
        self.command: PlayMove | None = None

    def render(self, state: ApplicationState) -> None:
        """Store the rendered state."""
        self.last_state = state

    def read_command(
        self,
        state: ApplicationState,
    ) -> PlayMove | None:
        """Return the configured command."""
        return self.command


def test_stub_view_implements_view_protocol() -> None:
    view: View = StubView()

    state = ApplicationState()

    view.render(state)

    assert isinstance(view, StubView)
    assert view.last_state == state


def test_view_can_return_no_command() -> None:
    view: View = StubView()
    state = ApplicationState()

    assert view.read_command(state) is None


def test_view_can_return_play_move() -> None:
    view = StubView()

    command = PlayMove(
        game_id=uuid4(),
        move=Move(
            source=Square.from_algebraic("e2"),
            target=Square.from_algebraic("e4"),
        ),
    )

    view.command = command

    result = view.read_command(ApplicationState())

    assert result == command
