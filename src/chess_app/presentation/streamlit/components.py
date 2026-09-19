# src/chess_app/presentation/streamlit/components.py

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from chess_app.application.state import GameState
from chess_app.domain.player import PlayerType


def render_header() -> None:
    """Render the application header."""
    st.title("♟ Chess")
    st.caption("A clean architecture chess application")


def render_messages(
    message: str | None,
    error: str | None,
) -> None:
    """Render application messages and errors."""
    if error is not None:
        st.error(error)

    if message is not None:
        st.success(message)


def render_players(game: GameState) -> None:
    """Render the two players."""
    white = game.white_player
    black = game.black_player

    white_label = _player_label(
        white.name,
        white.player_type,
    )
    black_label = _player_label(
        black.name,
        black.player_type,
    )

    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            st.markdown("### ♔ Blancs")
            st.write(white_label)

    with right:
        with st.container(border=True):
            st.markdown("### ♚ Noirs")
            st.write(black_label)


def render_game_status(game: GameState) -> None:
    """Render the current game status."""
    status = _status_label(game.status)

    if game.status == "in_progress":
        turn = _color_label(game.turn)

        st.info(
            f"Tour des **{turn}**",
            icon="♟",
        )

    elif game.status == "suspended":
        st.warning(
            "La partie est suspendue.",
            icon="⏸️",
        )

    elif game.status == "white_won":
        st.success(
            "Les blancs ont gagné.",
            icon="🏆",
        )

    elif game.status == "black_won":
        st.success(
            "Les noirs ont gagné.",
            icon="🏆",
        )

    elif game.status == "draw":
        st.info(
            "Partie nulle.",
            icon="🤝",
        )

    else:
        st.info(status)

    if game.in_check and game.status == "in_progress":
        turn = _color_label(game.turn)

        st.warning(
            f"Les **{turn}** sont en échec.",
            icon="⚠️",
        )


def render_board(
    game: GameState,
    selected_square: str | None,
    on_square_clicked: Callable[
        [str, tuple[str, ...]],
        None,
    ],
) -> None:
    """Render the chess board."""
    pieces = {piece.square: piece for piece in game.board.pieces}

    legal_targets = _legal_targets(
        game.legal_moves,
        selected_square,
    )

    with st.container(border=True):
        st.markdown("### Échiquier")

        for rank in range(7, -1, -1):
            columns = st.columns(
                8,
                gap="small",
            )

            for file_index, column in enumerate(columns):
                square = f"{chr(ord('a') + file_index)}{rank + 1}"

                piece = pieces.get(square)

                label = piece.symbol if piece is not None else " "

                if square in legal_targets:
                    label = f"• {label}"

                if square == selected_square:
                    label = f"◆ {label}"

                with column:
                    st.button(
                        label,
                        key=(f"board_{game.game_id}_{square}"),
                        on_click=on_square_clicked,
                        args=(
                            square,
                            game.legal_moves,
                        ),
                        use_container_width=True,
                        disabled=(game.status != "in_progress"),
                    )

        st.caption("a    b    c    d    e    f    g    h")


def render_promotion(
    game: GameState,
    pending_promotion: tuple[str, str] | None,
    on_promotion_selected: Callable[
        [str, str, str],
        None,
    ],
) -> None:
    """Render the promotion selector."""
    if pending_promotion is None:
        return

    source, target = pending_promotion

    with st.container(border=True):
        st.markdown("### Promotion")

        st.write(f"Choisissez la pièce pour **{source} → {target}**.")

        promotion_labels = {
            "q": "Dame",
            "r": "Tour",
            "b": "Fou",
            "n": "Cavalier",
        }

        selected = st.selectbox(
            "Pièce",
            options=tuple(promotion_labels),
            format_func=promotion_labels.__getitem__,
            key=f"promotion_{game.game_id}_{target}",
        )

        st.button(
            "Confirmer la promotion",
            key=f"confirm_promotion_{game.game_id}",
            on_click=on_promotion_selected,
            args=(
                source,
                target,
                selected,
            ),
            use_container_width=True,
        )


def render_controls(
    game: GameState,
    on_suspend: Callable[[], None],
    on_resume: Callable[[], None],
) -> None:
    """Render game controls."""
    with st.container(border=True):
        st.markdown("### Actions")

        if game.status == "in_progress":
            st.button(
                "⏸️ Suspendre la partie",
                key=f"suspend_{game.game_id}",
                on_click=on_suspend,
                use_container_width=True,
            )

        elif game.status == "suspended":
            st.button(
                "▶️ Reprendre la partie",
                key=f"resume_{game.game_id}",
                on_click=on_resume,
                use_container_width=True,
            )


def render_move_history(game: GameState) -> None:
    """Render the move history."""
    with st.container(border=True):
        st.markdown("### Historique")

        if not game.moves:
            st.caption("Aucun coup joué.")
            return

        for number, move in _move_pairs(game):
            label = f"**{number}.** {move}"

            st.markdown(label)


def _player_label(
    name: str,
    player_type: str,
) -> str:
    """Return a human-readable player label."""
    if player_type == PlayerType.AI.value:
        return f"{name} · IA"

    return f"{name} · Joueur"


def _status_label(status: str) -> str:
    """Return a human-readable game status."""
    labels = {
        "in_progress": "En cours",
        "suspended": "Suspendue",
        "white_won": "Victoire des blancs",
        "black_won": "Victoire des noirs",
        "draw": "Match nul",
    }

    return labels.get(status, status)


def _color_label(color: str) -> str:
    """Return a human-readable color."""
    labels = {
        "white": "blancs",
        "black": "noirs",
    }

    return labels.get(color, color)


def _legal_targets(
    legal_moves: tuple[str, ...],
    selected_square: str | None,
) -> set[str]:
    """Return legal targets for the selected square."""
    if selected_square is None:
        return set()

    return {move[2:4] for move in legal_moves if move[:2] == selected_square}


def _move_pairs(
    game: GameState,
) -> tuple[tuple[int, str], ...]:
    """Return move numbers and UCI moves."""
    pairs: list[tuple[int, str]] = []

    for index, move in enumerate(
        game.moves,
        start=1,
    ):
        if index % 2 == 1:
            number = (index + 1) // 2
            pairs.append((number, move.uci))
        else:
            number = (index + 1) // 2
            pairs.append((number, move.uci))

    return tuple(pairs)
