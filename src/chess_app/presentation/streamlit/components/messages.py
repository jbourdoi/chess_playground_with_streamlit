# src/chess_app/presentation/streamlit/components/messages.py

import streamlit as st


def render_messages(
    message: str | None,
    error: str | None,
) -> None:
    """Render application messages and errors."""
    if error is not None:
        st.error(error)

    if message is not None:
        st.success(message)
