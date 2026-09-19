# tests/application/test_controller.py

from uuid import UUID, uuid4

from chess_app.application.commands import (
    NewGame,
    PlayerSpec,
    PlayMove,
    ResumeGame,
    SuspendGame,
)
from chess_app.application.context import (
    ApplicationContext,
    UserContext,
)
from chess_app.application.controller import Controller
from chess_app.application.queries import GetGameState
from chess_app.domain.move import Move
from chess_app.domain.piece import Color
from chess_app.domain.player import PlayerType
from chess_app.domain.square import Square
from chess_app.infrastructure.persistence.in_memory_game_repository import (
    InMemoryGameRepository,
)


def make_context(
    user_id: UUID | None = None,
) -> ApplicationContext:
    """Create a test application context."""
    current_user_id = user_id if user_id is not None else uuid4()

    return ApplicationContext(
        user=UserContext(
            user_id=current_user_id,
            username="Alice",
        ),
        session_id=uuid4(),
    )


def make_new_game_command(
    user_id: UUID,
) -> NewGame:
    """Create a new game command."""
    return NewGame(
        white_player=PlayerSpec(
            player_id=uuid4(),
            user_id=user_id,
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
    user_id = UUID("22222222-2222-2222-2222-222222222222")
    context = make_context(user_id)

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    state = controller.handle(
        context,
        make_new_game_command(user_id),
    )

    assert state.error is None
    assert state.game is not None
    assert state.game.game_id == str(game_id)

    stored_game = repository.get(game_id)

    assert stored_game is not None
    assert stored_game.game_id == game_id


def test_play_move_updates_game() -> None:
    repository = InMemoryGameRepository()
    game_id = UUID("11111111-1111-1111-1111-111111111111")
    context = make_context()

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    state = controller.handle(
        context,
        make_new_game_command(context.user.user_id),
    )

    assert state.game is not None

    state = controller.handle(
        context,
        PlayMove(
            game_id=game_id,
            move=make_move("e2", "e4"),
        ),
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
    context = make_context()

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    controller.handle(
        context,
        make_new_game_command(context.user.user_id),
    )

    state = controller.handle(
        context,
        PlayMove(
            game_id=game_id,
            move=make_move("e2", "e5"),
        ),
    )

    assert state.error is not None
    assert state.game is not None
    assert state.game.moves == ()
    assert state.game.turn == "white"


def test_suspend_game() -> None:
    repository = InMemoryGameRepository()
    game_id = UUID("11111111-1111-1111-1111-111111111111")
    context = make_context()

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    controller.handle(
        context,
        make_new_game_command(context.user.user_id),
    )

    state = controller.handle(
        context,
        SuspendGame(game_id=game_id),
    )

    assert state.error is None
    assert state.game is not None
    assert state.game.status == "suspended"


def test_resume_game() -> None:
    repository = InMemoryGameRepository()
    game_id = UUID("11111111-1111-1111-1111-111111111111")
    context = make_context()

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    controller.handle(
        context,
        make_new_game_command(context.user.user_id),
    )

    controller.handle(
        context,
        SuspendGame(game_id=game_id),
    )

    state = controller.handle(
        context,
        ResumeGame(game_id=game_id),
    )

    assert state.error is None
    assert state.game is not None
    assert state.game.status == "in_progress"


def test_command_for_missing_game_returns_error() -> None:
    repository = InMemoryGameRepository()
    context = make_context()
    controller = Controller(repository)

    state = controller.handle(
        context,
        SuspendGame(game_id=uuid4()),
    )

    assert state.game is None
    assert state.error is not None


def test_get_game_state_returns_current_game() -> None:
    repository = InMemoryGameRepository()
    game_id = UUID("11111111-1111-1111-1111-111111111111")
    context = make_context()

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    controller.handle(
        context,
        make_new_game_command(context.user.user_id),
    )

    state = controller.handle_query(
        context,
        GetGameState(game_id=game_id),
    )

    assert state.error is None
    assert state.game is not None
    assert state.game.game_id == str(game_id)
    assert state.game.turn == "white"
    assert state.game.moves == ()


def test_get_game_state_returns_updated_game() -> None:
    repository = InMemoryGameRepository()
    game_id = UUID("11111111-1111-1111-1111-111111111111")
    context = make_context()

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    controller.handle(
        context,
        make_new_game_command(context.user.user_id),
    )

    controller.handle(
        context,
        PlayMove(
            game_id=game_id,
            move=make_move("e2", "e4"),
        ),
    )

    state = controller.handle_query(
        context,
        GetGameState(game_id=game_id),
    )

    assert state.error is None
    assert state.game is not None
    assert state.game.turn == "black"
    assert len(state.game.moves) == 1
    assert state.game.last_move is not None
    assert state.game.last_move.uci == "e2e4"


def test_get_game_state_for_missing_game_returns_error() -> None:
    repository = InMemoryGameRepository()
    context = make_context()
    controller = Controller(repository)
    game_id = uuid4()

    state = controller.handle_query(
        context,
        GetGameState(game_id=game_id),
    )

    assert state.game is None
    assert state.error is not None


def test_new_game_rejects_another_human_user() -> None:
    repository = InMemoryGameRepository()
    authenticated_user = uuid4()
    other_user = uuid4()

    context = make_context(authenticated_user)

    controller = Controller(
        game_repository=repository,
    )

    command = NewGame(
        white_player=PlayerSpec(
            player_id=other_user,
            name="Bob",
            color=Color.WHITE,
        ),
        black_player=PlayerSpec(
            player_id=uuid4(),
            name="ChessBot",
            color=Color.BLACK,
            player_type=PlayerType.AI,
        ),
    )

    state = controller.handle(
        context,
        command,
    )

    assert state.game is None
    assert state.error is not None
    assert state.error == "human player does not match authenticated user"


def test_user_cannot_play_another_users_game() -> None:
    repository = InMemoryGameRepository()

    owner_id = uuid4()
    attacker_id = uuid4()

    owner_context = make_context(owner_id)
    attacker_context = make_context(attacker_id)

    game_id = UUID("11111111-1111-1111-1111-111111111111")

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    controller.handle(
        owner_context,
        make_new_game_command(owner_id),
    )

    state = controller.handle(
        attacker_context,
        PlayMove(
            game_id=game_id,
            move=make_move("e2", "e4"),
        ),
    )

    assert state.error == ("user does not participate in this game")


def test_user_cannot_read_another_users_game() -> None:
    repository = InMemoryGameRepository()

    owner_id = uuid4()
    attacker_id = uuid4()

    owner_context = make_context(owner_id)
    attacker_context = make_context(attacker_id)

    game_id = UUID("11111111-1111-1111-1111-111111111111")

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    controller.handle(
        owner_context,
        make_new_game_command(owner_id),
    )

    state = controller.handle_query(
        attacker_context,
        GetGameState(game_id=game_id),
    )

    assert state.game is None
    assert state.error == ("user does not participate in this game")


def test_user_cannot_play_when_it_is_not_their_turn() -> None:
    repository = InMemoryGameRepository()

    user_id = uuid4()

    context = make_context(user_id)

    game_id = UUID("11111111-1111-1111-1111-111111111111")

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    controller.handle(
        context,
        make_new_game_command(user_id),
    )

    controller.handle(
        context,
        PlayMove(
            game_id=game_id,
            move=make_move("e2", "e4"),
        ),
    )

    state = controller.handle(
        context,
        PlayMove(
            game_id=game_id,
            move=make_move("e4", "e5"),
        ),
    )

    assert state.error == "it is not the user's turn"


def test_user_cannot_suspend_another_users_game() -> None:
    repository = InMemoryGameRepository()

    owner_id = uuid4()
    other_id = uuid4()

    owner_context = make_context(owner_id)
    other_context = make_context(other_id)

    game_id = UUID("11111111-1111-1111-1111-111111111111")

    controller = Controller(
        game_repository=repository,
        game_id_factory=lambda: game_id,
    )

    controller.handle(
        owner_context,
        make_new_game_command(owner_id),
    )

    state = controller.handle(
        other_context,
        SuspendGame(game_id=game_id),
    )

    assert state.game is None
    assert state.error == ("user does not participate in this game")
