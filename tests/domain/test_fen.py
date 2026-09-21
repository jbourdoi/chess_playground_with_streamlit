# tests/domain/test_fen.py

from uuid import uuid4

import pytest

from chess_app.domain.fen import to_fen
from chess_app.domain.game import Game
from chess_app.domain.move import Move
from chess_app.domain.piece import Color
from chess_app.domain.player import Player, PlayerType


@pytest.fixture
def new_game() -> Game:
    """Fournit une nouvelle partie d'échecs standard."""
    white = Player(
        player_id=uuid4(),
        name="White Player",
        color=Color.WHITE,
        player_type=PlayerType.HUMAN,
    )
    black = Player(
        player_id=uuid4(),
        name="Black Player",
        color=Color.BLACK,
        player_type=PlayerType.HUMAN,
    )
    return Game.new(game_id=uuid4(), white_player=white, black_player=black)


def test_to_fen_initial_position(new_game: Game) -> None:
    """Vérifie que la position initiale retourne le FEN de départ standard."""
    expected_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    assert to_fen(new_game) == expected_fen


def test_to_fen_after_pawn_move_without_adjacent_enemy(new_game: Game) -> None:
    """Vérifie que le FEN affiche '-' après une double poussée
    si aucun pion adverse n'est adjacent."""
    move = Move.from_uci("e2e4")
    game = new_game.play(move)

    # Aucun pion noir n'est présent sur d4 ou f4,
    # donc la cible en passant doit être '-'
    expected_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    assert to_fen(game) == expected_fen


def test_to_fen_after_pawn_move_with_adjacent_enemy(new_game: Game) -> None:
    """Vérifie que la case d'en passant apparaît
    lorsqu'un pion adverse est adjacent."""
    # Séquence de coups :
    # 1. e2e4 e7e6
    # 2. e4e5 f7f5 (Double poussée des Noirs.
    # Le pion blanc en e5 est adjacent au pion f5)
    game = new_game.play(Move.from_uci("e2e4"))
    game = game.play(Move.from_uci("e7e6"))
    game = game.play(Move.from_uci("e4e5"))
    game = game.play(Move.from_uci("f7f5"))

    # Le pion blanc en e5 peut capturer le pion f5 en passant sur f6
    exp_fen = "rnbqkbnr/pppp2pp/4p3/4Pp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 3"
    assert to_fen(game) == exp_fen


def test_to_fen_after_knight_move(new_game: Game) -> None:
    """Vérifie que le FEN incrémente l'horloge des demi-coups
    pour un coup de cavalier."""
    move = Move.from_uci("g1f3")
    game = new_game.play(move)

    exp_fen = "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1"
    assert to_fen(game) == exp_fen


def test_to_fen_castling_rights_loss(new_game: Game) -> None:
    """Vérifie que les droits de roque sont mis à jour
    lors du déplacement d'une tour."""
    game = new_game.play(Move.from_uci("h2h4"))
    game = game.play(Move.from_uci("a7a6"))
    game = game.play(Move.from_uci("h1h3"))
    # Déplacement de la tour petit roque

    # Les Blancs perdent le petit roque ('K'), 'KQkq' devient 'Qkq'
    fen = to_fen(game)
    assert " Qkq " in fen


def test_to_fen_fullmove_increment(new_game: Game) -> None:
    """Vérifie l'incrémentation du numéro de coup complet
    après le tour des Noirs."""
    game = new_game.play(Move.from_uci("e2e4"))
    game = game.play(Move.from_uci("e7e5"))

    # Les deux pions sont sur la même colonne (e),
    # donc aucun pion adverse n'est adjacent sur d ou f
    exp_fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
    assert to_fen(game) == exp_fen


def test_to_fen_after_double_pawn_push_c2c4(new_game: Game) -> None:
    """Vérifie le FEN généré après le coup c2c4
    avec prise en passant disponible sur c3."""
    moves = [
        "b1c3",
        "d7d5",
        "e2e4",
        "d5d4",
        "c3d5",
        "e7e5",
        "g1f3",
        "c7c6",
        "d5b4",
        "f8b4",
        "a2a3",
        "b4d6",
        "b2b4",
        "g8f6",
        "c2c4",
    ]

    game = new_game
    for move_uci in moves:
        game = game.play(Move.from_uci(move_uci))

    # Le pion noir en d4 peut capturer le pion c4 en passant sur c3
    e = "rnbqk2r/pp3ppp/2pb1n2/4p3/1PPpP3/P4N2/3P1PPP/R1BQKB1R b KQkq c3 0 8"
    assert to_fen(game) == e
