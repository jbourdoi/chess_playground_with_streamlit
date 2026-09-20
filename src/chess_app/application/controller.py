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
from chess_app.ports.game_repository import GameRepository


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
        result = self._load_authorized_game(
            context,
            query.game_id,
        )

        if isinstance(result, ApplicationState):
            return result

        return ApplicationState(
            game=game_to_state(result),
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
        result = self._load_authorized_game(
            context,
            command.game_id,
        )

        if isinstance(result, ApplicationState):
            return result

        game = result

        if not game.is_current_player(context.user.user_id):
            return ApplicationState(
                game=game_to_state(game),
                error="it is not the user's turn",
            )

        return self._apply_game_update(
            game,
            lambda current_game: current_game.play(command.move),
            f"Move played: {command.move.uci}",
        )

    def _handle_suspend_game(
        self,
        context: ApplicationContext,
        command: SuspendGame,
    ) -> ApplicationState:
        """Suspend an existing game."""
        result = self._load_authorized_game(
            context,
            command.game_id,
        )

        if isinstance(result, ApplicationState):
            return result

        return self._apply_game_update(
            result,
            lambda game: game.suspend(),
            "Game suspended.",
        )

    def _handle_resume_game(
        self,
        context: ApplicationContext,
        command: ResumeGame,
    ) -> ApplicationState:
        """Resume an existing game."""
        result = self._load_authorized_game(
            context,
            command.game_id,
        )

        if isinstance(result, ApplicationState):
            return result

        return self._apply_game_update(
            result,
            lambda game: game.resume(),
            "Game resumed.",
        )

    def _load_authorized_game(
        self,
        context: ApplicationContext,
        game_id: UUID,
    ) -> Game | ApplicationState:
        """
        Retrieve a game and validate user access.

        Return an ApplicationState containing an error when the game
        cannot be accessed.
        """
        game = self._game_repository.get(game_id)

        if game is None:
            return ApplicationState(error=f"game not found: {game_id}")

        if not game.has_player(context.user.user_id):
            return ApplicationState(
                error="user does not participate in this game"
            )

        return game

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

    def _apply_game_update(
        self,
        game: Game,
        update: Callable[[Game], Game],
        message: str,
    ) -> ApplicationState:
        """
        Apply a pure game update and persist the resulting game.

        The update callable must return a new Game.
        """
        try:
            updated_game = update(game)

        except ChessDomainError as exc:
            return ApplicationState(
                game=game_to_state(game),
                error=str(exc),
            )

        self._game_repository.save(updated_game)

        return ApplicationState(
            game=game_to_state(updated_game),
            message=message,
        )
