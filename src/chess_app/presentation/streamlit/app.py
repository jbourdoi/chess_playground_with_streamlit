# src/chess_app/presentation/streamlit/app.py

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import streamlit as st

from chess_app.application.commands import (
    NewGame,
    PlayerSpec,
)
from chess_app.application.context import (
    ApplicationContext,
    UserContext,
)
from chess_app.application.controller import Controller
from chess_app.application.session_service import SessionService
from chess_app.application.state import (
    ApplicationState,
)
from chess_app.domain.piece import Color
from chess_app.domain.player import PlayerType
from chess_app.domain.user import User
from chess_app.infrastructure.persistence.sqlite_game_repository import (
    SQLiteGameRepository,
)
from chess_app.infrastructure.persistence.sqlite_user_repository import (
    SQLiteUserRepository,
)
from chess_app.infrastructure.session.sqlite_session_repository import (
    SQLiteSessionRepository,
)
from chess_app.presentation.streamlit.view import StreamlitView

DEFAULT_DB_PATH = Path("data/chess.db")
DEFAULT_USERNAME = "local-player"


@dataclass(frozen=True, slots=True)
class AppDependencies:
    """Contain the concrete dependencies of the Streamlit application."""

    controller: Controller
    session_service: SessionService
    user_repository: SQLiteUserRepository
    view: StreamlitView


def get_database_path() -> Path:
    """Return the configured SQLite database path."""
    configured_path = os.getenv(
        "CHESS_DB_PATH",
    )

    if configured_path:
        return Path(configured_path)

    return DEFAULT_DB_PATH


def get_username() -> str:
    """Return the configured local application username."""
    username = os.getenv(
        "CHESS_USERNAME",
        DEFAULT_USERNAME,
    ).strip()

    if not username:
        return DEFAULT_USERNAME

    return username


def build_dependencies(
    database_path: Path,
) -> AppDependencies:
    """Build the application dependency graph."""
    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    user_repository = SQLiteUserRepository(
        str(database_path),
    )

    session_repository = SQLiteSessionRepository(
        str(database_path),
    )

    game_repository = SQLiteGameRepository(
        str(database_path),
    )

    session_service = SessionService(
        repository=session_repository,
    )

    controller = Controller(
        game_repository=game_repository,
    )

    view = StreamlitView()

    return AppDependencies(
        controller=controller,
        session_service=session_service,
        user_repository=user_repository,
        view=view,
    )


def get_or_create_user(
    repository: SQLiteUserRepository,
    username: str,
) -> User:
    """Return the configured user, creating it when necessary."""
    user = repository.get_by_username(username)

    if user is not None:
        return user

    user = User(
        user_id=uuid4(),
        username=username,
        created_at=datetime.now(timezone.utc),
    )

    repository.save(user)

    return user


def get_application_context(
    dependencies: AppDependencies,
) -> ApplicationContext:
    """Authenticate the current Streamlit session."""
    username = get_username()

    user = get_or_create_user(
        dependencies.user_repository,
        username,
    )

    token = st.session_state.get(
        "chess_app_session_token",
    )

    if not isinstance(token, str):
        token = ""

    session = dependencies.session_service.authenticate(
        token,
    )

    if session is None or session.user_id != user.user_id:
        created = dependencies.session_service.create(
            user.user_id,
        )

        st.session_state["chess_app_session_token"] = created.token

        session = created.session

    return ApplicationContext(
        user=UserContext(
            user_id=user.user_id,
            username=user.username,
        ),
        session_id=session.session_id,
    )


def create_initial_game(
    dependencies: AppDependencies,
    context: ApplicationContext,
) -> ApplicationState:
    """Create the initial local game."""
    new_game = NewGame(
        white_player=PlayerSpec(
            player_id=context.user.user_id,
            name=context.user.username,
            color=Color.WHITE,
            player_type=PlayerType.HUMAN,
            user_id=context.user.user_id,
        ),
        black_player=PlayerSpec(
            player_id=uuid4(),
            name="ChessBot",
            color=Color.BLACK,
            player_type=PlayerType.AI,
        ),
    )

    return dependencies.controller.handle(
        context,
        new_game,
    )


def load_application_state(
    dependencies: AppDependencies,
    context: ApplicationContext,
) -> ApplicationState:
    """Load or initialize the current application state."""
    state = st.session_state.get(
        "chess_app_application_state",
    )

    if isinstance(state, ApplicationState):
        return state

    state = create_initial_game(
        dependencies,
        context,
    )

    st.session_state["chess_app_application_state"] = state

    return state


def store_application_state(
    state: ApplicationState,
) -> None:
    """Store the latest application state."""
    st.session_state["chess_app_application_state"] = state


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(
        page_title="Chess",
        page_icon="♟",
        layout="centered",
    )

    dependencies = build_dependencies(
        get_database_path(),
    )

    context = get_application_context(
        dependencies,
    )

    state = load_application_state(
        dependencies,
        context,
    )

    dependencies.view.render(state)

    command = dependencies.view.read_command(
        state,
    )

    if command is None:
        return

    new_state = dependencies.controller.handle(
        context,
        command,
    )

    store_application_state(new_state)

    st.rerun()


if __name__ == "__main__":
    main()
