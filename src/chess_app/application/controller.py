# src/chess_app/application/controller.py

from __future__ import annotations

from collections.abc import Callable
from uuid import UUID, uuid4

from chess_app.application.commands import (
    Command,
    NewGame,
    PlayerSpec,
    PlayMove,
    ResumeGame,
    SuspendGame,
)
from chess_app.application.context import ApplicationContext
from chess_app.application.queries import (
    GetGameState,
    Query,
)
from chess_app.application.state import (
    ApplicationState,
    game_to_state,
)
from chess_app.domain.errors import ChessDomainError
from chess_app.domain.game import Game
from chess_app.domain.player import Player, PlayerType
from chess_app.ports.repository import GameRepository


class Controller:
    """Coordinate application commands and the domain."""

    def __init__(
        self,
        game_repository: GameRepository,
        game_id_factory: Callable[[], UUID] = uuid4,
    ) -> None:
        """
        Initialize the controller.

        The repository and identifier factory are injected to keep
        the controller independent from infrastructure.
        """
        self._game_repository = game_repository
        self._game_id_factory = game_id_factory

    def handle(
        self, context: ApplicationContext, command: Command
    ) -> ApplicationState:
        """
        Execute an application command.

        The returned state can be consumed by any view.
        """
        match command:
            case NewGame():
                return self._handle_new_game(
                    context,
                    command,
                )

            case PlayMove():
                return self._handle_play_move(
                    context,
                    command,
                )

            case SuspendGame():
                return self._handle_suspend_game(
                    context,
                    command,
                )

            case ResumeGame():
                return self._handle_resume_game(
                    context,
                    command,
                )

    def handle_query(
        self, context: ApplicationContext, query: Query
    ) -> ApplicationState:
        """
        Execute an application query.

        Queries do not modify the application state.
        """
        match query:
            case GetGameState():
                return self._handle_get_game_state(
                    context,
                    query,
                )

    @staticmethod
    def _validate_player_identity(
        context: ApplicationContext,
        spec: PlayerSpec,
    ) -> None:
        """Validate the identity represented by a player specification."""
        if spec.player_type is PlayerType.AI:
            if spec.user_id is not None:
                raise ValueError("AI player cannot have a user identity")
            return

        if spec.user_id != context.user.user_id:
            raise ValueError("human player does not match authenticated user")

    def _handle_get_game_state(
        self,
        context: ApplicationContext,
        query: GetGameState,
    ) -> ApplicationState:
        """Retrieve the current state of a game."""
        game = self._get_game(query.game_id)

        if game is None:
            return ApplicationState(error=f"game not found: {query.game_id}")

        access_error = self._validate_game_access(
            context,
            game,
        )

        if access_error is not None:
            return ApplicationState(error=access_error)

        return ApplicationState(
            game=game_to_state(game),
        )

    def _handle_new_game(
        self,
        context: ApplicationContext,
        command: NewGame,
    ) -> ApplicationState:
        """Create and persist a new game."""
        try:
            self._validate_player_identity(
                context,
                command.white_player,
            )
            self._validate_player_identity(
                context,
                command.black_player,
            )

            white_player = self._build_player(command.white_player)
            black_player = self._build_player(command.black_player)

            game = Game.new(
                game_id=self._game_id_factory(),
                white_player=white_player,
                black_player=black_player,
            )

        except ValueError as exc:
            return ApplicationState(error=str(exc))

        self._game_repository.save(game)

        return ApplicationState(
            game=game_to_state(game),
            message="Game created.",
        )

    def _handle_play_move(
        self,
        context: ApplicationContext,
        command: PlayMove,
    ) -> ApplicationState:
        """Play a move in an existing game."""
        game = self._get_game(command.game_id)

        if game is None:
            return ApplicationState(error=f"game not found: {command.game_id}")

        access_error = self._validate_game_access(
            context,
            game,
        )

        if access_error is not None:
            return ApplicationState(error=access_error)

        if not game.is_current_player(context.user.user_id):
            return ApplicationState(
                game=game_to_state(game),
                error="it is not the user's turn",
            )

        try:
            updated_game = game.play(command.move)

        except ChessDomainError as exc:
            return ApplicationState(
                game=game_to_state(game),
                error=str(exc),
            )

        self._game_repository.save(updated_game)

        return ApplicationState(
            game=game_to_state(updated_game),
            message=f"Move played: {command.move.uci}",
        )

    def _handle_suspend_game(
        self,
        context: ApplicationContext,
        command: SuspendGame,
    ) -> ApplicationState:
        """Suspend an existing game."""
        game = self._get_game(command.game_id)

        if game is None:
            return ApplicationState(error=f"game not found: {command.game_id}")

        access_error = self._validate_game_access(
            context,
            game,
        )

        if access_error is not None:
            return ApplicationState(error=access_error)
        try:
            suspended_game = game.suspend()

        except ChessDomainError as exc:
            return ApplicationState(
                game=game_to_state(game),
                error=str(exc),
            )

        self._game_repository.save(suspended_game)

        return ApplicationState(
            game=game_to_state(suspended_game),
            message="Game suspended.",
        )

    def _handle_resume_game(
        self,
        context: ApplicationContext,
        command: ResumeGame,
    ) -> ApplicationState:
        """Resume an existing game."""
        game = self._get_game(command.game_id)

        if game is None:
            return ApplicationState(error=f"game not found: {command.game_id}")

        access_error = self._validate_game_access(
            context,
            game,
        )

        if access_error is not None:
            return ApplicationState(error=access_error)
        try:
            resumed_game = game.resume()

        except ChessDomainError as exc:
            return ApplicationState(
                game=game_to_state(game),
                error=str(exc),
            )

        self._game_repository.save(resumed_game)

        return ApplicationState(
            game=game_to_state(resumed_game),
            message="Game resumed.",
        )

    def _get_game(self, game_id: UUID) -> Game | None:
        """Retrieve a game from the repository."""
        return self._game_repository.get(game_id)

    @staticmethod
    def _build_player(spec: PlayerSpec) -> Player:
        """Build a domain player from an application specification."""
        return Player(
            player_id=spec.player_id,
            name=spec.name,
            color=spec.color,
            player_type=spec.player_type,
            user_id=spec.user_id,
        )

    def _validate_game_access(
        self,
        context: ApplicationContext,
        game: Game,
    ) -> str | None:
        """
        Validate that the current user participates in the game.

        Return an error message when access is denied.
        """
        if not game.has_player(context.user.user_id):
            return "user does not participate in this game"

        return None
