# src/chess_app/presentation/streamlit/components/header.py

import streamlit as st


def render_header() -> None:
    """Render the application header."""
    st.markdown(
        '<div class="chess-title"><h1>♟ Chess</h1></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="chess-subtitle">'
        "Play, suspend and resume your games."
        "</div>",
        unsafe_allow_html=True,
    )
