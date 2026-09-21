# src/chess_app/infrastructure/engine/chess_api_engine.py

from __future__ import annotations

import http.client
import json
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

from chess_app.domain.fen import to_fen
from chess_app.domain.game import Game
from chess_app.domain.move import Move
from chess_app.ports.move_engine import EngineError

CHESS_API_URL = "https://chess-api.com/v1"
MAX_DEPTH = 18  # limites documentées du palier gratuit
MAX_THINKING_TIME_MS = 100

PostJson = Callable[[str, dict[str, Any], float], dict[str, Any]]


def post_json(
    url: str, payload: dict[str, Any], timeout: float
) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
    except (
        urllib.error.URLError,
        http.client.HTTPException,
        OSError,
    ) as exc:
        raise EngineError(f"engine request failed: {exc}") from exc

    try:
        data = json.loads(body)
    except ValueError as exc:
        raise EngineError("engine returned invalid JSON") from exc

    if not isinstance(data, dict):
        raise EngineError("engine returned an unexpected payload")

    return data


class ChessApiEngine:
    """Ask the public Stockfish REST API of chess-api.com for a move."""

    def __init__(
        self,
        depth: int = 8,  # défaut arbitraire (mon choix), ajustable
        max_thinking_time_ms: int = 50,
        timeout: float = 10.0,
        url: str = CHESS_API_URL,
        transport: PostJson = post_json,
    ) -> None:
        if not 1 <= depth <= MAX_DEPTH:
            raise ValueError(f"depth must be between 1 and {MAX_DEPTH}")

        if not 1 <= max_thinking_time_ms <= MAX_THINKING_TIME_MS:
            raise ValueError(
                "max_thinking_time_ms must be between 1 and "
                f"{MAX_THINKING_TIME_MS}"
            )

        self._depth = depth
        self._max_thinking_time_ms = max_thinking_time_ms
        self._timeout = timeout
        self._url = url
        self._transport = transport

    def choose_move(self, game: Game) -> Move:
        fen_move = to_fen(game)
        payload = {
            "fen": fen_move,
            "depth": self._depth,
            "maxThinkingTime": self._max_thinking_time_ms,
            "variants": 1,
        }
        print(f"'fen' : '{fen_move}'")
        data = self._transport(self._url, payload, self._timeout)
        uci = data.get("move")

        if data.get("type") == "info" or not isinstance(uci, str):
            detail = data.get("text", "no move in response")
            raise EngineError(f"engine did not return a move: {detail}")

        try:
            return Move.from_uci(uci)
        except ValueError as exc:
            raise EngineError(
                f"engine returned an invalid move: {uci!r}"
            ) from exc
