# src/chess_app/infrastructure/persistence/sqlite_game_repository.py

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID

from chess_app.domain.errors import (
    ChessDomainError,
)
from chess_app.domain.game import Game, GameStatus
from chess_app.domain.move import Move
from chess_app.domain.piece import (
    Color,
    PieceType,
)
from chess_app.domain.player import Player, PlayerType
from chess_app.domain.square import Square

_SCHEMA = """
CREATE TABLE IF NOT EXISTS games (
    game_id TEXT PRIMARY KEY,

    white_player_id TEXT NOT NULL,
    white_player_name TEXT NOT NULL,
    white_player_type TEXT NOT NULL,
    white_user_id TEXT,

    black_player_id TEXT NOT NULL,
    black_player_name TEXT NOT NULL,
    black_player_type TEXT NOT NULL,
    black_user_id TEXT,

    status TEXT NOT NULL
        CHECK (
            status IN (
                'in_progress',
                'suspended',
                'white_won',
                'black_won',
                'draw'
            )
        )
);

CREATE TABLE IF NOT EXISTS moves (
    game_id TEXT NOT NULL,
    ply INTEGER NOT NULL CHECK (ply > 0),
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    promotion TEXT,

    PRIMARY KEY (game_id, ply),

    FOREIGN KEY (game_id)
        REFERENCES games(game_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_moves_game_ply
    ON moves(game_id, ply);

CREATE INDEX IF NOT EXISTS idx_games_white_user
    ON games(white_user_id);

CREATE INDEX IF NOT EXISTS idx_games_black_user
    ON games(black_user_id);
"""


class SQLiteGameRepositoryError(Exception):
    """Raised when a persisted game cannot be read or written."""


class SQLiteGameRepository:
    """Persist chess games and move histories in SQLite."""

    def __init__(self, database_path: str | Path) -> None:
        """
        Initialize the SQLite game repository.

        The database schema is created when the repository is
        initialized if it does not already exist.
        """
        self._database_path = Path(database_path)

        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_schema()

    def get(self, game_id: UUID) -> Game | None:
        """
        Retrieve and reconstruct a game.

        Return None when the game does not exist.
        """
        try:
            with self._connect() as connection:
                game_row = connection.execute(
                    """
                    SELECT
                        game_id,
                        white_player_id,
                        white_player_name,
                        white_player_type,
                        white_user_id,
                        black_player_id,
                        black_player_name,
                        black_player_type,
                        black_user_id,
                        status
                    FROM games
                    WHERE game_id = ?
                    """,
                    (str(game_id),),
                ).fetchone()

                if game_row is None:
                    return None

                move_rows = connection.execute(
                    """
                    SELECT
                        ply,
                        source,
                        target,
                        promotion
                    FROM moves
                    WHERE game_id = ?
                    ORDER BY ply
                    """,
                    (str(game_id),),
                ).fetchall()

        except sqlite3.Error as exc:
            raise SQLiteGameRepositoryError(
                f"failed to read game: {game_id}"
            ) from exc

        return self._reconstruct_game(
            game_row,
            move_rows,
        )

    def save(self, game: Game) -> None:
        """
        Persist a complete game aggregate.

        The game metadata is upserted and its move history is
        replaced atomically.
        """
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO games (
                        game_id,
                        white_player_id,
                        white_player_name,
                        white_player_type,
                        white_user_id,
                        black_player_id,
                        black_player_name,
                        black_player_type,
                        black_user_id,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(game_id) DO UPDATE SET
                        white_player_id =
                            excluded.white_player_id,
                        white_player_name =
                            excluded.white_player_name,
                        white_player_type =
                            excluded.white_player_type,
                        white_user_id =
                            excluded.white_user_id,
                        black_player_id =
                            excluded.black_player_id,
                        black_player_name =
                            excluded.black_player_name,
                        black_player_type =
                            excluded.black_player_type,
                        black_user_id =
                            excluded.black_user_id,
                        status =
                            excluded.status
                    """,
                    self._game_row(game),
                )

                connection.execute(
                    """
                    DELETE FROM moves
                    WHERE game_id = ?
                    """,
                    (str(game.game_id),),
                )

                connection.executemany(
                    """
                    INSERT INTO moves (
                        game_id,
                        ply,
                        source,
                        target,
                        promotion
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    self._move_rows(game),
                )

        except sqlite3.Error as exc:
            raise SQLiteGameRepositoryError(
                f"failed to save game: {game.game_id}"
            ) from exc

    def _initialize_schema(self) -> None:
        """Create the database schema if needed."""
        try:
            with self._connect() as connection:
                connection.executescript(_SCHEMA)
        except sqlite3.Error as exc:
            raise SQLiteGameRepositoryError(
                "failed to initialize SQLite schema"
            ) from exc

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        """Open a short-lived SQLite connection."""
        connection = sqlite3.connect(
            self._database_path,
        )
        connection.row_factory = sqlite3.Row

        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _game_row(
        game: Game,
    ) -> tuple[
        str,
        str,
        str,
        str,
        str | None,
        str,
        str,
        str,
        str | None,
        str,
    ]:
        """Convert a game into a SQLite row."""
        return (
            str(game.game_id),
            str(game.white_player.player_id),
            game.white_player.name,
            game.white_player.player_type.value,
            (
                str(game.white_player.user_id)
                if game.white_player.user_id is not None
                else None
            ),
            str(game.black_player.player_id),
            game.black_player.name,
            game.black_player.player_type.value,
            (
                str(game.black_player.user_id)
                if game.black_player.user_id is not None
                else None
            ),
            game.status.value,
        )

    @staticmethod
    def _move_rows(
        game: Game,
    ) -> list[tuple[str, int, str, str, str | None]]:
        """Convert a game's move history into SQLite rows."""
        return [
            (
                str(game.game_id),
                ply,
                move.source.algebraic,
                move.target.algebraic,
                (move.promotion.value if move.promotion is not None else None),
            )
            for ply, move in enumerate(
                game.moves,
                start=1,
            )
        ]

    @classmethod
    def _reconstruct_game(
        cls,
        game_row: sqlite3.Row,
        move_rows: list[sqlite3.Row],
    ) -> Game:
        """Reconstruct a domain game from database rows."""
        try:
            white_player = cls._build_player(
                game_row,
                "white",
                Color.WHITE,
            )

            black_player = cls._build_player(
                game_row,
                "black",
                Color.BLACK,
            )

            game = Game.new(
                game_id=UUID(game_row["game_id"]),
                white_player=white_player,
                black_player=black_player,
            )

            for move_row in move_rows:
                move = cls._build_move(move_row)
                game = game.play(move)

            stored_status = GameStatus(game_row["status"])

            if stored_status is GameStatus.SUSPENDED:
                if game.status is not GameStatus.IN_PROGRESS:
                    raise SQLiteGameRepositoryError(
                        "suspended game has a terminal position"
                    )

                game = game.suspend()

            elif stored_status is not game.status:
                raise SQLiteGameRepositoryError(
                    "persisted game status does not match reconstructed game"
                )

            return game

        except (
            ValueError,
            ChessDomainError,
        ) as exc:
            raise SQLiteGameRepositoryError(
                "persisted game contains invalid domain data"
            ) from exc

    @staticmethod
    def _build_player(
        row: sqlite3.Row,
        color_name: str,
        color: Color,
    ) -> Player:
        """Build a domain player from a database row."""
        player_id = UUID(row[f"{color_name}_player_id"])

        user_id_value = row[f"{color_name}_user_id"]

        user_id = UUID(user_id_value) if user_id_value is not None else None

        return Player(
            player_id=player_id,
            name=row[f"{color_name}_player_name"],
            color=color,
            player_type=PlayerType(row[f"{color_name}_player_type"]),
            user_id=user_id,
        )

    @staticmethod
    def _build_move(
        row: sqlite3.Row,
    ) -> Move:
        """Build a domain move from a database row."""
        promotion_value = row["promotion"]

        promotion = (
            PieceType(promotion_value) if promotion_value is not None else None
        )

        return Move(
            source=Square.from_algebraic(row["source"]),
            target=Square.from_algebraic(row["target"]),
            promotion=promotion,
        )
