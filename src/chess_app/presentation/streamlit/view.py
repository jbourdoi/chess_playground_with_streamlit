# src/chess_app/presentation/streamlit/view.py
from __future__ import annotations

from dataclasses import replace
from uuid import UUID

import streamlit as st

from chess_app.application.commands import (
    Command,
    PlayMove,
    ResumeGame,
    SuspendGame,
)
from chess_app.application.state import (
    ApplicationState,
    GameState,
)
from chess_app.domain.move import Move
from chess_app.domain.piece import PieceType
from chess_app.domain.square import Square
from chess_app.ports.view import View

from .components import (
    render_board,
    render_controls,
    render_game_status,
    render_header,
    render_messages,
    render_move_history,
    render_players,
    render_promotion,
    render_styles,
)
from .state import StreamlitUiState

UI_STATE_KEY = "chess_app_ui_state"


class StreamlitView(View):
    """Render the chess application using Streamlit."""

    def render(self, state: ApplicationState) -> None:
        """Render the complete application."""
        render_styles()

        left, right = st.columns(
            [5, 8],
            gap="medium",
        )

        with left, st.container(key="side_panel"):
            render_header()

            render_messages(
                message=state.message,
                error=state.error,
            )

            if state.game is not None:
                self._synchronize_ui_state(
                    state.game,
                )

                ui_state = self._get_ui_state()

                render_players(state.game)
                render_game_status(state.game)

                render_promotion(
                    game=state.game,
                    pending_promotion=(ui_state.pending_promotion),
                    on_promotion_selected=(self._on_promotion_selected),
                )

                render_controls(
                    game=state.game,
                    on_suspend=self._queue_suspend,
                    on_resume=self._queue_resume,
                )

                render_move_history(state.game)

        with right:
            if state.game is None:
                st.info("No game in progress.")
                return

            ui_state = self._get_ui_state()

            render_board(
                game=state.game,
                selected_square=ui_state.selected_square,
                on_square_clicked=self._on_square_clicked,
            )

    def read_command(
        self,
        state: ApplicationState,
    ) -> Command | None:
        """Translate pending UI actions into an application command."""
        if state.game is None:
            return None

        ui_state = self._get_ui_state()
        game_id = UUID(state.game.game_id)

        if ui_state.pending_action == "suspend":
            self._clear_pending_action()

            return SuspendGame(
                game_id=game_id,
            )

        if ui_state.pending_action == "resume":
            self._clear_pending_action()

            return ResumeGame(
                game_id=game_id,
            )

        if ui_state.pending_move_uci is None:
            return None

        uci = ui_state.pending_move_uci

        move = self._move_from_uci(uci)

        self._set_ui_state(
            replace(
                ui_state,
                selected_square=None,
                pending_move_uci=None,
                pending_promotion=None,
            )
        )

        return PlayMove(
            game_id=game_id,
            move=move,
        )

    def _get_ui_state(self) -> StreamlitUiState:
        """Return the current transient UI state."""
        value = st.session_state.get(UI_STATE_KEY)

        if isinstance(value, StreamlitUiState):
            return value

        ui_state = StreamlitUiState()

        st.session_state[UI_STATE_KEY] = ui_state

        return ui_state

    def _set_ui_state(
        self,
        ui_state: StreamlitUiState,
    ) -> None:
        """Persist the transient UI state."""
        st.session_state[UI_STATE_KEY] = ui_state

    def _clear_pending_action(self) -> None:
        """Clear the pending application action."""
        ui_state = self._get_ui_state()

        self._set_ui_state(
            replace(
                ui_state,
                pending_action=None,
            )
        )

    def _on_square_clicked(
        self,
        square: str,
        legal_moves: tuple[str, ...],
    ) -> None:
        """Handle a chess-board square click."""
        ui_state = self._get_ui_state()

        if ui_state.pending_promotion is not None:
            return

        selected = ui_state.selected_square

        if selected is None:
            if self._is_move_source(
                square,
                legal_moves,
            ):
                self._set_ui_state(
                    replace(
                        ui_state,
                        selected_square=square,
                    )
                )

            return

        if selected == square:
            self._set_ui_state(
                replace(
                    ui_state,
                    selected_square=None,
                )
            )

            return

        candidates = tuple(
            move
            for move in legal_moves
            if move[:2] == selected and move[2:4] == square
        )

        if len(candidates) == 1:
            self._set_ui_state(
                replace(
                    ui_state,
                    selected_square=None,
                    pending_move_uci=candidates[0],
                )
            )

            return

        if len(candidates) > 1:
            self._set_ui_state(
                replace(
                    ui_state,
                    selected_square=None,
                    pending_promotion=(
                        selected,
                        square,
                    ),
                )
            )

            return

        if self._is_move_source(
            square,
            legal_moves,
        ):
            self._set_ui_state(
                replace(
                    ui_state,
                    selected_square=square,
                )
            )

            return

        self._set_ui_state(
            replace(
                ui_state,
                selected_square=None,
            )
        )

    def _on_promotion_selected(
        self,
        source: str,
        target: str,
        promotion: str,
    ) -> None:
        """Queue a promotion move."""
        ui_state = self._get_ui_state()

        self._set_ui_state(
            replace(
                ui_state,
                selected_square=None,
                pending_move_uci=(f"{source}{target}{promotion}"),
                pending_promotion=None,
            )
        )

    def _queue_suspend(self) -> None:
        """Queue a suspend-game command."""
        ui_state = self._get_ui_state()

        self._set_ui_state(
            replace(
                ui_state,
                pending_action="suspend",
            )
        )

    def _queue_resume(self) -> None:
        """Queue a resume-game command."""
        ui_state = self._get_ui_state()

        self._set_ui_state(
            replace(
                ui_state,
                pending_action="resume",
            )
        )

    def _synchronize_ui_state(
        self,
        game: GameState,
    ) -> None:
        """Reset UI state when the current game changes."""
        ui_state = self._get_ui_state()

        if ui_state.game_id == game.game_id:
            return

        self._set_ui_state(
            StreamlitUiState(
                game_id=game.game_id,
            )
        )

    @staticmethod
    def _is_move_source(
        square: str,
        legal_moves: tuple[str, ...],
    ) -> bool:
        """Return whether a square starts a legal move."""
        return any(move[:2] == square for move in legal_moves)

    @staticmethod
    def _move_from_uci(uci: str) -> Move:
        """Build a domain Move from a UCI move."""
        if len(uci) not in {4, 5}:
            raise ValueError(f"invalid UCI move: {uci}")

        source = Square.from_algebraic(uci[:2])
        target = Square.from_algebraic(uci[2:4])

        promotion = None

        if len(uci) == 5:
            promotion_types = {
                "q": PieceType.QUEEN,
                "r": PieceType.ROOK,
                "b": PieceType.BISHOP,
                "n": PieceType.KNIGHT,
            }

            promotion = promotion_types.get(uci[4].lower())

            if promotion is None:
                raise ValueError(f"invalid promotion: {uci}")

        return Move(
            source=source,
            target=target,
            promotion=promotion,
        )
