from uuid import uuid4

from chess_app.application.state import game_to_state
from chess_app.domain.game import Game
from chess_app.domain.piece import Color
from chess_app.domain.player import Player


def make_game() -> Game:
    """Create a test game."""
    white = Player(
        player_id=uuid4(),
        name="Alice",
        color=Color.WHITE,
    )

    black = Player(
        player_id=uuid4(),
        name="Bob",
        color=Color.BLACK,
    )

    return Game.new(
        game_id=uuid4(),
        white_player=white,
        black_player=black,
    )


def test_game_to_state_contains_initial_board() -> None:
    game = make_game()

    state = game_to_state(game)

    assert len(state.board.pieces) == 32


def test_game_to_state_contains_players() -> None:
    game = make_game()

    state = game_to_state(game)

    assert state.white_player.name == "Alice"
    assert state.black_player.name == "Bob"


def test_initial_state_contains_no_moves() -> None:
    game = make_game()

    state = game_to_state(game)

    assert state.moves == ()
    assert state.last_move is None


def test_initial_state_is_white_turn() -> None:
    game = make_game()

    state = game_to_state(game)

    assert state.turn == "white"


def test_state_contains_legal_moves() -> None:
    game = make_game()

    state = game_to_state(game)

    assert len(state.legal_moves) == 20
    assert "e2e4" in state.legal_moves
