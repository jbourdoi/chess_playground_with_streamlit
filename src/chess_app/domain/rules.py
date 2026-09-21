# src/chess_app/domain/rules.py

from __future__ import annotations

from .board import Board
from .castling_rights import CastlingRights
from .move import Move
from .piece import Color, Piece, PieceType
from .square import Square


def is_square_attacked(
    board: Board,
    square: Square,
    by_color: Color,
) -> bool:
    """Return whether a square is attacked by a color."""
    for source, piece in board.pieces(by_color):
        if _piece_attacks_square(board, source, piece, square):
            return True

    return False


def is_in_check(board: Board, color: Color) -> bool:
    """Return whether a player's king is currently in check."""
    king_square = _find_king(board, color)

    if king_square is None:
        raise ValueError(f"{color.value} king is missing")

    return is_square_attacked(
        board,
        king_square,
        color.opposite,
    )


def is_pseudo_legal_move(
    board: Board,
    move: Move,
    color: Color,
    castling_rights: CastlingRights | None = None,
    en_passant_target: Square | None = None,
) -> bool:
    """
    Check whether a move respects piece movement rules.

    King safety is deliberately not checked here.
    """
    piece = board.piece_at(move.source)

    if piece is None or piece.color is not color:
        return False

    target_piece = board.piece_at(move.target)

    if target_piece is not None and target_piece.color is color:
        return False

    if target_piece is not None and target_piece.type is PieceType.KING:
        return False

    if not _valid_promotion(piece.type, move):
        return False

    file_delta = move.target.file - move.source.file
    rank_delta = move.target.rank - move.source.rank

    if piece.type is PieceType.PAWN:
        return _valid_pawn_move(
            board,
            move,
            color,
            file_delta,
            rank_delta,
            en_passant_target,
        )

    if piece.type is PieceType.KNIGHT:
        return (abs(file_delta), abs(rank_delta)) in {(1, 2), (2, 1)}

    if piece.type is PieceType.KING:
        if (
            abs(file_delta) <= 1
            and abs(rank_delta) <= 1
            and (file_delta != 0 or rank_delta != 0)
        ):
            return True

        if castling_rights is None:
            return False

        return _valid_castling_geometry(
            board,
            move,
            color,
            castling_rights,
        )

    if piece.type is PieceType.BISHOP:
        return abs(file_delta) == abs(rank_delta) and _path_is_clear(
            board, move
        )

    if piece.type is PieceType.ROOK:
        return (
            (file_delta == 0 or rank_delta == 0)
            and (file_delta != 0 or rank_delta != 0)
            and _path_is_clear(board, move)
        )

    if piece.type is PieceType.QUEEN:
        diagonal = abs(file_delta) == abs(rank_delta)
        straight = file_delta == 0 or rank_delta == 0

        return (
            (diagonal or straight)
            and (file_delta != 0 or rank_delta != 0)
            and _path_is_clear(board, move)
        )


def is_legal_move(
    board: Board,
    move: Move,
    color: Color,
    castling_rights: CastlingRights | None = None,
    en_passant_target: Square | None = None,
) -> bool:
    """Return whether a move is fully legal."""
    if not is_pseudo_legal_move(
        board,
        move,
        color,
        castling_rights,
        en_passant_target,
    ):
        return False

    piece = board.piece_at(move.source)

    if piece is None:
        return False

    # A castling king may not start, cross, or finish on an
    # attacked square.
    if (
        piece.type is PieceType.KING
        and abs(move.target.file - move.source.file) == 2
    ):
        opponent = color.opposite

        if is_square_attacked(
            board,
            move.source,
            opponent,
        ):
            return False

        direction = 1 if move.target.file > move.source.file else -1

        transit = move.source.offset(direction, 0)

        if transit is None:
            return False

        if is_square_attacked(
            board,
            transit,
            opponent,
        ):
            return False

    new_board = board.move_piece(
        move,
        en_passant_target,
    )

    return not is_in_check(new_board, color)


def pseudo_legal_moves(
    board: Board,
    color: Color,
    castling_rights: CastlingRights | None = None,
    en_passant_target: Square | None = None,
) -> tuple[Move, ...]:
    """Return all pseudo-legal moves for a player."""
    rights = (
        castling_rights
        if castling_rights is not None
        else CastlingRights.none()
    )

    moves: list[Move] = []

    for source, piece in board.pieces(color):
        for rank in range(8):
            for file in range(8):
                target = Square(file=file, rank=rank)

                if target == source:
                    continue

                if piece.type is PieceType.PAWN and target.rank in {0, 7}:
                    promotion_types = (
                        PieceType.QUEEN,
                        PieceType.ROOK,
                        PieceType.BISHOP,
                        PieceType.KNIGHT,
                    )

                    for promotion in promotion_types:
                        candidate = Move(
                            source=source,
                            target=target,
                            promotion=promotion,
                        )

                        if is_pseudo_legal_move(
                            board,
                            candidate,
                            color,
                            rights,
                            en_passant_target,
                        ):
                            moves.append(candidate)

                    continue

                candidate = Move(
                    source=source,
                    target=target,
                )

                if is_pseudo_legal_move(
                    board,
                    candidate,
                    color,
                    rights,
                    en_passant_target,
                ):
                    moves.append(candidate)

    return tuple(moves)


def legal_moves(
    board: Board,
    color: Color,
    castling_rights: CastlingRights | None = None,
    en_passant_target: Square | None = None,
) -> tuple[Move, ...]:
    """Return all fully legal moves for a player."""
    rights = (
        castling_rights
        if castling_rights is not None
        else CastlingRights.none()
    )

    candidates = pseudo_legal_moves(
        board,
        color,
        rights,
        en_passant_target,
    )

    return tuple(
        move
        for move in candidates
        if is_legal_move(
            board,
            move,
            color,
            rights,
            en_passant_target,
        )
    )


def is_checkmate(
    board: Board,
    color: Color,
    castling_rights: CastlingRights | None = None,
    en_passant_target: Square | None = None,
) -> bool:
    """Return whether a player is checkmated."""
    if not is_in_check(board, color):
        return False

    return not legal_moves(
        board,
        color,
        castling_rights,
        en_passant_target,
    )


def is_stalemate(
    board: Board,
    color: Color,
    castling_rights: CastlingRights | None = None,
    en_passant_target: Square | None = None,
) -> bool:
    """Return whether a player is stalemated."""
    if is_in_check(board, color):
        return False

    return not legal_moves(
        board,
        color,
        castling_rights,
        en_passant_target,
    )


def next_castling_rights(
    board: Board,
    move: Move,
    rights: CastlingRights,
) -> CastlingRights:
    """Return the castling rights after a move."""
    piece = board.piece_at(move.source)

    if piece is None:
        raise ValueError("source square is empty")

    updated = rights

    if piece.type is PieceType.KING:
        updated = updated.without_king_rights(piece.color)

    elif piece.type is PieceType.ROOK:
        updated = _remove_rook_right(
            updated,
            piece.color,
            move.source,
        )

    captured = board.piece_at(move.target)

    if captured is not None and captured.type is PieceType.ROOK:
        updated = _remove_rook_right(
            updated,
            captured.color,
            move.target,
        )

    return updated


# def next_en_passant_target(
#     move: Move,
#     board: Board,
# ) -> Square | None:
#     """Return the en passant target produced by a move."""
#     piece = board.piece_at(move.source)

#     if piece is None or piece.type is not PieceType.PAWN:
#         return None

#     if abs(move.target.rank - move.source.rank) != 2:
#         return None

#     direction = 1 if piece.color is Color.WHITE else -1

#     return move.source.offset(0, direction)


def next_en_passant_target(
    move: Move,
    board: Board,
) -> Square | None:
    """
    Return the en passant target produced by a move.

    The target square is set ONLY if an opponent pawn is on an adjacent
    file at the destination rank, making an en passant capture possible.
    """
    piece = board.piece_at(move.source)

    if piece is None or piece.type is not PieceType.PAWN:
        return None

    if abs(move.target.rank - move.source.rank) != 2:
        return None

    target_file = move.target.file
    target_rank = move.target.rank
    opponent_color = piece.color.opposite

    # Vérifier s'il y a au moins un pion adverse sur les colonnes adjacentes
    has_adjacent_enemy_pawn = False
    for adj_file in (target_file - 1, target_file + 1):
        if 0 <= adj_file <= 7:
            adj_square = Square(file=adj_file, rank=target_rank)
            adj_piece = board.piece_at(adj_square)
            if (
                adj_piece is not None
                and adj_piece.type is PieceType.PAWN
                and adj_piece.color is opponent_color
            ):
                has_adjacent_enemy_pawn = True
                break

    if not has_adjacent_enemy_pawn:
        return None

    direction = 1 if piece.color is Color.WHITE else -1

    return move.source.offset(0, direction)


def _find_king(
    board: Board,
    color: Color,
) -> Square | None:
    """Return the square containing a player's king."""
    for square, piece in board.pieces(color):
        if piece.type is PieceType.KING:
            return square

    return None


def _piece_attacks_square(
    board: Board,
    source: Square,
    piece: Piece,
    target: Square,
) -> bool:
    """Return whether one piece attacks one square."""
    file_delta = target.file - source.file
    rank_delta = target.rank - source.rank

    if piece.type is PieceType.PAWN:
        direction = 1 if piece.color is Color.WHITE else -1

        return abs(file_delta) == 1 and rank_delta == direction

    if piece.type is PieceType.KNIGHT:
        return (abs(file_delta), abs(rank_delta)) in {(1, 2), (2, 1)}

    if piece.type is PieceType.KING:
        return max(abs(file_delta), abs(rank_delta)) == 1

    if piece.type is PieceType.BISHOP:
        return abs(file_delta) == abs(rank_delta) and _path_is_clear(
            board,
            Move(source, target),
        )

    if piece.type is PieceType.ROOK:
        return (
            (file_delta == 0 or rank_delta == 0)
            and (file_delta != 0 or rank_delta != 0)
            and _path_is_clear(
                board,
                Move(source, target),
            )
        )

    if piece.type is PieceType.QUEEN:
        diagonal = abs(file_delta) == abs(rank_delta)
        straight = file_delta == 0 or rank_delta == 0

        return (
            (diagonal or straight)
            and (file_delta != 0 or rank_delta != 0)
            and _path_is_clear(
                board,
                Move(source, target),
            )
        )


def _valid_castling_geometry(
    board: Board,
    move: Move,
    color: Color,
    rights: CastlingRights,
) -> bool:
    """Validate the static geometry of a castling move."""
    expected_rank = 0 if color is Color.WHITE else 7

    if move.source != Square(file=4, rank=expected_rank):
        return False

    if move.target.rank != expected_rank:
        return False

    empty_squares: tuple[Square, ...]

    if move.target.file == 6:
        if not rights.can_castle_kingside(color):
            return False

        rook_square = Square(
            file=7,
            rank=expected_rank,
        )

        empty_squares = (
            Square(file=5, rank=expected_rank),
            Square(file=6, rank=expected_rank),
        )

    elif move.target.file == 2:
        if not rights.can_castle_queenside(color):
            return False

        rook_square = Square(
            file=0,
            rank=expected_rank,
        )

        empty_squares = (
            Square(file=1, rank=expected_rank),
            Square(file=2, rank=expected_rank),
            Square(file=3, rank=expected_rank),
        )

    else:
        return False

    rook = board.piece_at(rook_square)

    if rook != Piece(color, PieceType.ROOK):
        return False

    return all(board.piece_at(square) is None for square in empty_squares)


def _valid_pawn_move(
    board: Board,
    move: Move,
    color: Color,
    file_delta: int,
    rank_delta: int,
    en_passant_target: Square | None,
) -> bool:
    """Validate a pawn move."""
    direction = 1 if color is Color.WHITE else -1
    start_rank = 1 if color is Color.WHITE else 6

    target_piece = board.piece_at(move.target)

    if file_delta == 0 and rank_delta == direction:
        return target_piece is None

    if (
        file_delta == 0
        and rank_delta == 2 * direction
        and move.source.rank == start_rank
    ):
        intermediate = move.source.offset(0, direction)

        if intermediate is None:
            return False

        return board.piece_at(intermediate) is None and target_piece is None

    if abs(file_delta) == 1 and rank_delta == direction:
        if target_piece is not None:
            return True

        if en_passant_target != move.target:
            return False

        captured_square = Square(
            file=move.target.file,
            rank=move.source.rank,
        )

        captured = board.piece_at(captured_square)

        return (
            captured is not None
            and captured.color is color.opposite
            and captured.type is PieceType.PAWN
        )

    return False


def _valid_promotion(
    piece_type: PieceType,
    move: Move,
) -> bool:
    """Validate the promotion component of a move."""
    final_rank = move.target.rank in {0, 7}

    if piece_type is not PieceType.PAWN:
        return move.promotion is None

    if final_rank:
        return move.promotion in {
            PieceType.KNIGHT,
            PieceType.BISHOP,
            PieceType.ROOK,
            PieceType.QUEEN,
        }

    return move.promotion is None


def _path_is_clear(
    board: Board,
    move: Move,
) -> bool:
    """Check whether all intermediate squares are empty."""
    file_delta = move.target.file - move.source.file
    rank_delta = move.target.rank - move.source.rank

    file_step = 0 if file_delta == 0 else (1 if file_delta > 0 else -1)
    rank_step = 0 if rank_delta == 0 else (1 if rank_delta > 0 else -1)

    current = move.source.offset(
        file_step,
        rank_step,
    )

    while current is not None and current != move.target:
        if board.piece_at(current) is not None:
            return False

        current = current.offset(
            file_step,
            rank_step,
        )

    return current == move.target


def _remove_rook_right(
    rights: CastlingRights,
    color: Color,
    square: Square,
) -> CastlingRights:
    """Remove the castling right associated with a rook square."""
    if color is Color.WHITE:
        if square == Square.from_algebraic("a1"):
            return rights.without_queenside(color)

        if square == Square.from_algebraic("h1"):
            return rights.without_kingside(color)

    if color is Color.BLACK:
        if square == Square.from_algebraic("a8"):
            return rights.without_queenside(color)

        if square == Square.from_algebraic("h8"):
            return rights.without_kingside(color)

    return rights
