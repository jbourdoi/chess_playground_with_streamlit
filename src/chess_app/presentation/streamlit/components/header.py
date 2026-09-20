# src/chess_app/presentation/streamlit/components/header.py

import streamlit as st


def render_header() -> None:
    """Render the application header."""
    st.html(
        '<div class="app-header">'
        '<h1 class="app-title">♟ Chess</h1>'
        '<p class="app-subtitle">Play, suspend and resume your games.</p>'
        "</div>"
    )
