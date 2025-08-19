# tests/test_core.py
import pytest
from unittest.mock import patch, MagicMock

import tic_tac_toe.core.literals as literals
from enum import Enum
from tic_tac_toe.core.helper_classes import Move, Player
from tic_tac_toe.core.enums import Difficulty
from tic_tac_toe.core.logic_game import TicTacToeLogic, InvalidMoveError

class FakeDifficulty(Enum):
    IMPOSSIBLE = 99

# ------------------------
# Fixtures
# ------------------------

@pytest.fixture
def fake_credentials():
    return {
        literals.FIRST_USER: {
            literals.USERNAMES: "Alice",
            literals.ANIMALS: ("A", "Ant"),
            literals.COLORS: ("red", "Red", "\033[91m"),
        },
        literals.SECOND_USER: {
            literals.USERNAMES: "Bob",
            literals.ANIMALS: ("B", "Bear"),
            literals.COLORS: ("blue", "Blue", "\033[94m"),
        },
        "LOGS_FILE": "game.log",
    }

@pytest.fixture
def game_logic(fake_credentials):
    with patch("tic_tac_toe.core.logic_game.shelve.open", MagicMock()) as mock_shelve, \
         patch("tic_tac_toe.core.logic_game.AIPlayer", MagicMock()):
        mock_shelve.return_value.__enter__.return_value = fake_credentials
        return TicTacToeLogic(size_board=3)


# ------------------------
# Initialization
# ------------------------

def test_invalid_board_size():
    with pytest.raises(ValueError):
        TicTacToeLogic(size_board=2)


def test_missing_credentials():
    with patch("tic_tac_toe.core.logic_game.shelve.open", MagicMock()) as mock_shelve:
        mock_shelve.return_value.__enter__.return_value = {}
        with pytest.raises(RuntimeError):
            TicTacToeLogic(size_board=3)


def test_prepare_players_incomplete(fake_credentials):
    bad_creds = fake_credentials.copy()
    del bad_creds[literals.FIRST_USER][literals.ANIMALS]
    with patch("tic_tac_toe.core.logic_game.shelve.open", MagicMock()) as mock_shelve, \
         patch("tic_tac_toe.core.logic_game.AIPlayer", MagicMock()):
        mock_shelve.return_value.__enter__.return_value = bad_creds
        with pytest.raises(RuntimeError):
            TicTacToeLogic(size_board=3)


def test_init_success(game_logic):
    assert literals.MACHINE in game_logic.players
    assert isinstance(game_logic.players[literals.FIRST_USER][1], Player)

# ------------------------
# Player and turn management
# ------------------------

def test_toggle_type_of_game(game_logic):
    initial_mode = game_logic.get_play_vs_machine()
    game_logic.toggle_type_of_game()
    assert game_logic.get_play_vs_machine() != initial_mode


def test_toggle_player(game_logic):
    first = game_logic.current_player
    game_logic.toggle_player()
    second = game_logic.current_player
    assert first != second


def test_get_opponent_name(game_logic):
    name = game_logic.get_opponent_name()
    assert isinstance(name, str)


def test_get_opponent_credentials_for(game_logic):
    player_name, _ = game_logic.current_player
    creds = game_logic.get_opponent_credentials_for(player_name)
    assert creds.name != player_name
    assert hasattr(creds, "ans_clr")

# ------------------------
# Statistics
# ------------------------

def test_update_score_wrap(game_logic):
    game_logic.update_score("Alice", 999)
    game_logic.update_score("Alice", 5)
    assert game_logic.scores["Alice"] == 4


def test_update_wins_wrap(game_logic):
    game_logic.update_wins("Bob", 99)
    game_logic.update_wins("Bob", 2)
    assert game_logic.wins["Bob"] == 1


def test_update_games_wrap(game_logic):
    game_logic.update_games("Alice", 999)
    game_logic.update_games("Alice", 5)
    assert game_logic.games["Alice"] == 4

# ------------------------
# Moves and board
# ------------------------

def test_valid_and_invalid_move(game_logic):
    move = Move(row=0, col=0, animal="X", color="red")
    assert game_logic._is_valid_movement(move)
    game_logic._process_move(move)
    with pytest.raises(InvalidMoveError):
        game_logic._process_move(move)


def test_tie_detection(game_logic):
    # For simplicity, fill the board without winners
    for r in range(3):
        for c in range(3):
            game_logic._current_moves[r][c] = Move(r, c, animal="X", color="red")
    game_logic._update_board_mapping()
    assert game_logic._is_tied()


def test_check_winner(game_logic):
    combo = [(0,0),(0,1),(0,2)]
    win_comb = ["X","X","X"]
    assert game_logic._check_winner(win_comb, combo)
    assert game_logic._has_winner()

# ------------------------
# AI
# ------------------------

def test_get_ai_move_by_level(game_logic):
    for level in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD, Difficulty.VERY_HARD]:
        game_logic._ai_player.select_random_move.return_value = (0,0)
        game_logic._ai_player.select_medium_move.return_value = (0,1)
        game_logic._ai_player.select_hard_move.return_value = (1,1)
        game_logic._ai_player.select_very_hard_move.return_value = (2,2)
        result = game_logic.get_ai_move_by_level(level)
        assert isinstance(result, tuple)


def test_get_ai_move_invalid_level(game_logic):
    with pytest.raises(RuntimeError, match="Unsupported AI difficulty level"):
        game_logic.get_ai_move_by_level(FakeDifficulty.IMPOSSIBLE)

