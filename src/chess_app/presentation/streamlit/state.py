# src/chess_app/presentation/streamlit/state.py

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StreamlitUiState:
    """Represent transient state maintained by the Streamlit interface."""

    game_id: str | None = None
    selected_square: str | None = None
    pending_move_uci: str | None = None
    pending_promotion: tuple[str, str] | None = None
    pending_action: str | None = None
