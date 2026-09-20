# src/chess_app/application/state.py

from __future__ import annotations

from dataclasses import dataclass

from chess_app.domain.game import Game


@dataclass(frozen=True, slots=True)
class PieceState:
    """Represent a chess piece for the presentation layer."""

    square: str
    color: str
    type: str
    symbol: str


@dataclass(frozen=True, slots=True)
class BoardState:
    """Represent the board for the presentation layer."""

    pieces: tuple[PieceState, ...]


@dataclass(frozen=True, slots=True)
class PlayerState:
    """Represent a player for the presentation layer."""

    player_id: str
    name: str
    color: str
    player_type: str


@dataclass(frozen=True, slots=True)
class MoveState:
    """Represent a move for the presentation layer."""

    source: str
    target: str
    promotion: str | None
    uci: str


@dataclass(frozen=True, slots=True)
class GameState:
    """Represent the complete state of a chess game."""

    game_id: str
    white_player: PlayerState
    black_player: PlayerState
    board: BoardState
    moves: tuple[MoveState, ...]
    last_move: MoveState | None
    turn: str
    status: str
    in_check: bool
    legal_moves: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ApplicationState:
    """Represent the state exposed by the application layer."""

    game: GameState | None = None
    message: str | None = None
    error: str | None = None


def game_to_state(game: Game) -> GameState:
    """
    Convert a domain Game into a presentation-neutral state.

    This function is pure.
    """
    pieces = tuple(
        PieceState(
            square=square.algebraic,
            color=piece.color.value,
            type=piece.type.value,
            symbol=piece.symbol,
        )
        for square, piece in game.board.pieces()
    )

    moves = tuple(
        MoveState(
            source=move.source.algebraic,
            target=move.target.algebraic,
            promotion=(
                move.promotion.value if move.promotion is not None else None
            ),
            uci=move.uci,
        )
        for move in game.moves
    )

    white_player = PlayerState(
        player_id=str(game.white_player.player_id),
        name=game.white_player.name,
        color=game.white_player.color.value,
        player_type=game.white_player.player_type.value,
    )

    black_player = PlayerState(
        player_id=str(game.black_player.player_id),
        name=game.black_player.name,
        color=game.black_player.color.value,
        player_type=game.black_player.player_type.value,
    )

    return GameState(
        game_id=str(game.game_id),
        white_player=white_player,
        black_player=black_player,
        board=BoardState(pieces=pieces),
        moves=moves,
        last_move=moves[-1] if moves else None,
        turn=game.turn.value,
        status=game.status.value,
        in_check=game.in_check,
        legal_moves=tuple(move.uci for move in game.legal_moves),
    )
