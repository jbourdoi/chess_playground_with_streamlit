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
from chess_app.domain.player import Player
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

    def handle(self, command: Command) -> ApplicationState:
        """
        Execute an application command.

        The returned state can be consumed by any view.
        """
        match command:
            case NewGame():
                return self._handle_new_game(command)

            case PlayMove():
                return self._handle_play_move(command)

            case SuspendGame():
                return self._handle_suspend_game(command)

            case ResumeGame():
                return self._handle_resume_game(command)

    def handle_query(self, query: Query) -> ApplicationState:
        """
        Execute an application query.

        Queries do not modify the application state.
        """
        match query:
            case GetGameState():
                return self._handle_get_game_state(query)

    def _handle_get_game_state(
        self,
        query: GetGameState,
    ) -> ApplicationState:
        """Retrieve the current state of a game."""
        game = self._get_game(query.game_id)

        if game is None:
            return ApplicationState(error=f"game not found: {query.game_id}")

        return ApplicationState(
            game=game_to_state(game),
        )

    def _handle_new_game(
        self,
        command: NewGame,
    ) -> ApplicationState:
        """Create and persist a new game."""
        try:
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
        command: PlayMove,
    ) -> ApplicationState:
        """Play a move in an existing game."""
        game = self._get_game(command.game_id)

        if game is None:
            return ApplicationState(error=f"game not found: {command.game_id}")

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
        command: SuspendGame,
    ) -> ApplicationState:
        """Suspend an existing game."""
        game = self._get_game(command.game_id)

        if game is None:
            return ApplicationState(error=f"game not found: {command.game_id}")

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
        command: ResumeGame,
    ) -> ApplicationState:
        """Resume an existing game."""
        game = self._get_game(command.game_id)

        if game is None:
            return ApplicationState(error=f"game not found: {command.game_id}")

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
        )
