from uuid import UUID, uuid4

from chess_app.application.commands import (
    NewGame,
    PlayerSpec,
    PlayMove,
    ResumeGame,
    SuspendGame,
)
from chess_app.application.controller import Controller
from chess_app.application.queries import GetGameState
from chess_app.domain.move import Move
from chess_app.domain.piece import Color
from chess_app.domain.player import PlayerType
from chess_app.domain.position import Square
from chess_app.infrastructure.persistence.in_memory_repository import (
    InMemoryGameRepository,
)

# class FakeGameRepository:
#     """In-memory repository used by application tests."""

#     def __init__(self) -> None:
#         self.games: dict[UUID, Game] = {}

#     def get(self, game_id: UUID) -> Game | None:
#         """Retrieve a game."""
#         return self.games.get(game_id)

#     def save(self, game: Game) -> None:
#         """Store a game."""
#         self.games[game.game_id] = game


def make_new_game_command() -> NewGame:
    """Create a new game command."""
    return NewGame(
        white_player=PlayerSpec(
            player_id=uuid4(),
            name="Alice",
            color=Color.WHITE,
        ),
        black_player=PlayerSpec(
            player_id=uuid4(),
            name="ChessBot",
            color=Color.BLACK,
            player_type=PlayerType.AI,
        ),
    )


def make_move(source: str, target: str) -> Move:
    """Create a move from algebraic coordinates."""
    return Move(
        source=Square.from_algebraic(source),
        target=Square.from_algebraic(target),
    )


def test_new_game_creates_and_saves_game() -> None:
    repository = InMemoryGameRepository()

    game_id = UUID("11111111-1111-1111-1111-111111111111")

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    state = controller.handle(make_new_game_command())

    assert state.error is None
    assert state.game is not None
    assert state.game.game_id == str(game_id)

    stored_game = repository.get(game_id)

    assert stored_game is not None
    assert stored_game.game_id == game_id


def test_play_move_updates_game() -> None:
    repository = InMemoryGameRepository()
    game_id = UUID("11111111-1111-1111-1111-111111111111")

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    state = controller.handle(make_new_game_command())

    assert state.game is not None

    state = controller.handle(
        PlayMove(
            game_id=game_id,
            move=make_move("e2", "e4"),
        )
    )

    assert state.error is None
    assert state.game is not None
    assert len(state.game.moves) == 1
    assert state.game.last_move is not None
    assert state.game.last_move.uci == "e2e4"
    assert state.game.turn == "black"


def test_illegal_move_preserves_previous_state() -> None:
    repository = InMemoryGameRepository()
    game_id = UUID("11111111-1111-1111-1111-111111111111")

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    controller.handle(make_new_game_command())

    state = controller.handle(
        PlayMove(
            game_id=game_id,
            move=make_move("e2", "e5"),
        )
    )

    assert state.error is not None
    assert state.game is not None
    assert state.game.moves == ()
    assert state.game.turn == "white"


def test_suspend_game() -> None:
    repository = InMemoryGameRepository()
    game_id = UUID("11111111-1111-1111-1111-111111111111")

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    controller.handle(make_new_game_command())

    state = controller.handle(SuspendGame(game_id=game_id))

    assert state.error is None
    assert state.game is not None
    assert state.game.status == "suspended"


def test_resume_game() -> None:
    repository = InMemoryGameRepository()
    game_id = UUID("11111111-1111-1111-1111-111111111111")

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    controller.handle(make_new_game_command())
    controller.handle(SuspendGame(game_id=game_id))

    state = controller.handle(ResumeGame(game_id=game_id))

    assert state.error is None
    assert state.game is not None
    assert state.game.status == "in_progress"


def test_command_for_missing_game_returns_error() -> None:
    repository = InMemoryGameRepository()
    controller = Controller(repository)

    state = controller.handle(SuspendGame(game_id=uuid4()))

    assert state.game is None
    assert state.error is not None


def test_get_game_state_returns_current_game() -> None:
    repository = InMemoryGameRepository()
    game_id = UUID("11111111-1111-1111-1111-111111111111")

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    controller.handle(make_new_game_command())

    state = controller.handle_query(GetGameState(game_id=game_id))

    assert state.error is None
    assert state.game is not None
    assert state.game.game_id == str(game_id)
    assert state.game.turn == "white"
    assert state.game.moves == ()


def test_get_game_state_returns_updated_game() -> None:
    repository = InMemoryGameRepository()
    game_id = UUID("11111111-1111-1111-1111-111111111111")

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    controller.handle(make_new_game_command())

    controller.handle(
        PlayMove(
            game_id=game_id,
            move=make_move("e2", "e4"),
        )
    )

    state = controller.handle_query(GetGameState(game_id=game_id))

    assert state.error is None
    assert state.game is not None
    assert state.game.turn == "black"
    assert len(state.game.moves) == 1
    assert state.game.last_move is not None
    assert state.game.last_move.uci == "e2e4"


def test_get_game_state_for_missing_game_returns_error() -> None:
    repository = InMemoryGameRepository()
    controller = Controller(repository)

    game_id = uuid4()

    state = controller.handle_query(GetGameState(game_id=game_id))

    assert state.game is None
    assert state.error is not None
