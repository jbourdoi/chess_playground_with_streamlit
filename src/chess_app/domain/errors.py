# src/chess_app/domain/errors.py


class ChessDomainError(Exception):
    """Base exception for domain errors."""


class IllegalMoveError(ChessDomainError):
    """Raised when a move is not allowed."""


class InvalidGameStateError(ChessDomainError):
    """Raised when an operation is incompatible with the game state."""
