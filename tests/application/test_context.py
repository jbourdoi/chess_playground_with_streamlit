# tests/application/test_context.py

from uuid import uuid4

import pytest

from chess_app.application.context import (
    ApplicationContext,
    UserContext,
)


def test_user_context_creation() -> None:
    user_id = uuid4()

    context = UserContext(
        user_id=user_id,
        username="alice",
    )

    assert context.user_id == user_id
    assert context.username == "alice"


def test_user_context_rejects_empty_username() -> None:
    with pytest.raises(ValueError):
        UserContext(
            user_id=uuid4(),
            username="   ",
        )


def test_user_context_is_immutable() -> None:
    context = UserContext(
        user_id=uuid4(),
        username="alice",
    )

    with pytest.raises(AttributeError):
        context.username = "bob"  # type: ignore[misc]


def test_application_context_creation() -> None:
    user_context = UserContext(
        user_id=uuid4(),
        username="alice",
    )
    session_id = uuid4()

    context = ApplicationContext(
        user=user_context,
        session_id=session_id,
    )

    assert context.user == user_context
    assert context.session_id == session_id


def test_application_context_is_immutable() -> None:
    context = ApplicationContext(
        user=UserContext(
            user_id=uuid4(),
            username="alice",
        ),
        session_id=uuid4(),
    )

    with pytest.raises(AttributeError):
        context.session_id = uuid4()  # type: ignore[misc]
