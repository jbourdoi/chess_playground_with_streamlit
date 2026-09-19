# src/chess_app/domain/game.py

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from uuid import UUID

from .board import Board
from .castling_rights import CastlingRights
from .errors import IllegalMoveError, InvalidGameStateError
from .move import Move
from .piece import Color
from .player import Player
from .rules import (
    is_checkmate,
    is_in_check,
    is_legal_move,
    is_stalemate,
    legal_moves,
    next_castling_rights,
    next_en_passant_target,
)
from .square import Square


class GameStatus(Enum):
    """Represent the state of a chess game."""

    IN_PROGRESS = "in_progress"
    SUSPENDED = "suspended"
    WHITE_WON = "white_won"
    BLACK_WON = "black_won"
    DRAW = "draw"


@dataclass(frozen=True, slots=True)
class Game:
    """Represent a chess game."""

    game_id: UUID
    white_player: Player
    black_player: Player
    board: Board
    moves: tuple[Move, ...]
    status: GameStatus
    castling_rights: CastlingRights = field(
        default_factory=CastlingRights.initial
    )
    en_passant_target: Square | None = None

    @classmethod
    def new(
        cls,
        game_id: UUID,
        white_player: Player,
        black_player: Player,
    ) -> Game:
        """Create a new chess game."""
        if white_player.color is not Color.WHITE:
            raise ValueError("white_player must be white")

        if black_player.color is not Color.BLACK:
            raise ValueError("black_player must be black")

        return cls(
            game_id=game_id,
            white_player=white_player,
            black_player=black_player,
            board=Board.initial(),
            moves=(),
            status=GameStatus.IN_PROGRESS,
            castling_rights=CastlingRights.initial(),
            en_passant_target=None,
        )

    @property
    def turn(self) -> Color:
        """Return the color whose turn it is."""
        if len(self.moves) % 2 == 0:
            return Color.WHITE

        return Color.BLACK

    @property
    def current_player(self) -> Player:
        """Return the player whose turn it is."""
        if self.turn is Color.WHITE:
            return self.white_player

        return self.black_player

    @property
    def in_check(self) -> bool:
        """Return whether the current player is in check."""
        return is_in_check(self.board, self.turn)

    @property
    def legal_moves(self) -> tuple[Move, ...]:
        """Return all legal moves for the current player."""
        return legal_moves(
            self.board,
            self.turn,
            self.castling_rights,
            self.en_passant_target,
        )

    def play(self, move: Move) -> Game:
        """
        Return a new game after playing a legal move.

        The current game remains unchanged.
        """
        if self.status is not GameStatus.IN_PROGRESS:
            raise InvalidGameStateError(
                "cannot play a move in the current game state"
            )

        color = self.turn

        if not is_legal_move(
            self.board,
            move,
            color,
            self.castling_rights,
            self.en_passant_target,
        ):
            raise IllegalMoveError(f"illegal move: {move.uci}")

        new_board = self.board.move_piece(
            move,
            self.en_passant_target,
        )

        new_moves = self.moves + (move,)

        new_rights = next_castling_rights(
            self.board,
            move,
            self.castling_rights,
        )

        new_en_passant_target = next_en_passant_target(
            move,
            self.board,
        )

        opponent = color.opposite

        if is_checkmate(
            new_board,
            opponent,
            new_rights,
            new_en_passant_target,
        ):
            if opponent is Color.WHITE:
                new_status = GameStatus.BLACK_WON
            else:
                new_status = GameStatus.WHITE_WON

        elif is_stalemate(
            new_board,
            opponent,
            new_rights,
            new_en_passant_target,
        ):
            new_status = GameStatus.DRAW

        else:
            new_status = GameStatus.IN_PROGRESS

        return replace(
            self,
            board=new_board,
            moves=new_moves,
            status=new_status,
            castling_rights=new_rights,
            en_passant_target=new_en_passant_target,
        )

    def suspend(self) -> Game:
        """Return a new game marked as suspended."""
        if self.status is not GameStatus.IN_PROGRESS:
            raise InvalidGameStateError("only an active game can be suspended")

        return replace(
            self,
            status=GameStatus.SUSPENDED,
        )

    def resume(self) -> Game:
        """Return a new game marked as active."""
        if self.status is not GameStatus.SUSPENDED:
            raise InvalidGameStateError("only a suspended game can be resumed")

        return replace(
            self,
            status=GameStatus.IN_PROGRESS,
        )

    def has_player(self, user_id: UUID) -> bool:
        """
        Return whether a user participates in the game.

        AI players are ignored because they are not associated with
        a user account.
        """
        return (
            self.white_player.user_id == user_id
            or self.black_player.user_id == user_id
        )

    def is_current_player(self, user_id: UUID) -> bool:
        """
        Return whether a user controls the player whose turn it is.
        """
        return self.current_player.user_id == user_id
