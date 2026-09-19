from uuid import uuid4

from chess_app.application.queries import GetGameState


def test_get_game_state_contains_game_id() -> None:
    game_id = uuid4()

    query = GetGameState(game_id=game_id)

    assert query.game_id == game_id


def test_get_game_state_is_immutable() -> None:
    query = GetGameState(game_id=uuid4())

    try:
        query.game_id = uuid4()  # type: ignore[misc]
    except AttributeError:
        pass
    else:
        raise AssertionError("GetGameState should be immutable")
