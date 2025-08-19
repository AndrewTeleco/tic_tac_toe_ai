# tests/test_ai.py

import pickle
import pytest
from colorama import Fore, Style, init
init(autoreset=True)
from random import seed
from unittest.mock import patch
from tic_tac_toe.ai.ai_player import AIPlayer
from tic_tac_toe.core.enums import Difficulty
from tic_tac_toe.core.helper_classes import Move, AIConfig
from tic_tac_toe.core.literals import AI_MARK, PLAYER_MARK, UNDERSCORE, EMPTY
from tic_tac_toe.core.logic_game import TicTacToeLogic, FIRST_USER, SECOND_USER

# ───────────────────────────────────────────────
# Dummy DB for Python 3.11+ shelve/dbm
# ───────────────────────────────────────────────

# Patch dbm.open to return DummyDB with correct keys/values
fake_db_data = {
    b"username_1": pickle.dumps({"usernames": "Alice", "animals": ["Cat"], "colors": ["Red"]}),
    b"username_2": pickle.dumps({"usernames": "Bob", "animals": ["Dog"], "colors": ["Blue"]}),
}

class DummyDB(dict):
    """Dict-like object with context manager interface for dbm/shelve."""
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

patch_dbm = patch("dbm.open", return_value=DummyDB(fake_db_data))
patch_dbm.start()


# ───────────────────────────────────────────────
# Helper Functions
# ───────────────────────────────────────────────

def winning_combos(size: int):
    """
    Returns the winning combinations for a board of given size.
    Dummy credentials are injected manually to satisfy AIPlayer requirements.
    """
    logic = TicTacToeLogic(size)

    # Dummy credentials for testing
    dummy_creds = {
        FIRST_USER: {"usernames": "Alice", "animals": ["Cat"], "colors": ["Red"]},
        SECOND_USER: {"usernames": "Bob", "animals": ["Dog"], "colors": ["Blue"]},
        "other_info": "dummy"
    }

    # Inject dummy players
    logic.players = {}
    for user_key in (FIRST_USER, SECOND_USER):
        data = dummy_creds[user_key]
        logic.players[user_key] = (data["usernames"], None)

    # Setup current type of game and current players
    logic._current_type_of_game = 0  # Player vs Player
    logic._current_players = {
        logic.players[FIRST_USER][0]: logic.players[FIRST_USER][1],
        logic.players[SECOND_USER][0]: logic.players[SECOND_USER][1],
    }

    return logic._winning_combos  # attribute expected by AIPlayer


def empty_board(size=3):
    """
    Returns an empty board and mapping for testing.
    - moves: 2D list of Move objects
    - mapping: 2D list of strings (visual board)
    """
    moves = [[Move(r, c, animal=EMPTY) for c in range(size)] for r in range(size)]
    mapping = [[UNDERSCORE for _ in range(size)] for _ in range(size)]
    return moves, mapping



# ───────────────────────────────────────────────
# AIPlayer Initialization Tests
# ───────────────────────────────────────────────

def test_aiplayer_initialization():
    moves, mapping = empty_board()
    ai = AIPlayer(size_board=3, current_moves=moves, mapping_moves=mapping,
                  winning_combos=winning_combos(3), level=Difficulty.EASY)
    assert ai.level == Difficulty.EASY
    assert ai._size_board == 3
    assert ai._mapping_moves == mapping
    assert ai._current_moves == moves
    assert isinstance(ai.cache, dict)
    assert ai.cache == {}

# ───────────────────────────────────────────────
# _get_remaining_moves Tests
# ───────────────────────────────────────────────

def test_get_remaining_moves_partial():
    moves, mapping = empty_board()
    mapping[0][0] = AI_MARK
    moves[0][0] = Move(0, 0 ,animal=AI_MARK)
    ai = AIPlayer(3, moves, mapping, winning_combos(3), Difficulty.EASY)
    remaining = ai._get_remaining_moves(all_moves=True, mapping=True)
    assert (0,0) not in remaining
    assert len(remaining) == 8

# ───────────────────────────────────────────────
# select_random_move Tests
# ───────────────────────────────────────────────

def test_select_random_move_nonempty():
    seed(42)  # For reproducibility
    moves, mapping = empty_board()
    ai = AIPlayer(3, moves, mapping, winning_combos(3), Difficulty.EASY)
    move = ai.select_random_move()
    assert move in [(r,c) for r in range(3) for c in range(3)]

# ───────────────────────────────────────────────
# select_medium_move Test (deterministic)
# ───────────────────────────────────────────────

def test_select_medium_move_blocks_win():
    """Ensure AI blocks opponent's winning move on MEDIUM (deterministic)."""
    moves, mapping = empty_board()
    mapping[0][0] = PLAYER_MARK
    mapping[1][1] = PLAYER_MARK
    moves[0][0] = Move(0,0,animal=PLAYER_MARK)
    moves[1][1] = Move(1,1,animal=PLAYER_MARK)
    ai = AIPlayer(3, moves, mapping, winning_combos(3), Difficulty.MEDIUM)

    with patch.object(AIPlayer, '_introduce_random_error', return_value=False):
        move = ai.select_medium_move()

    # After AI move, player should not have a winning move
    new_moves = [row[:] for row in moves]
    new_moves[move[0]][move[1]] = Move(move[0], move[1], animal=AI_MARK)

    # Check if any winning combo is fully occupied by PLAYER_MARK
    for combo in winning_combos(3):
        assert not all(new_moves[r][c].animal == PLAYER_MARK for r,c in combo)


# ───────────────────────────────────────────────
# evaluate_ai_score Tests
# ───────────────────────────────────────────────

def test_evaluate_ai_score_empty_board():
    moves, mapping = empty_board()
    ai = AIPlayer(3, moves, mapping, winning_combos(3), Difficulty.HARD)
    score = ai.evaluate_ai_score()
    assert score == 0


def test_evaluate_ai_score_ai_wins():
    moves, mapping = empty_board()
    mapping[0][0] = mapping[0][1] = mapping[0][2] = AI_MARK
    moves[0][0] = moves[0][1] = moves[0][2] = Move(0,0,animal=AI_MARK)
    ai = AIPlayer(3, moves, mapping, winning_combos(3), Difficulty.HARD)
    score = ai.evaluate_ai_score()
    assert score == 10


def test_evaluate_ai_score_player_wins():
    moves, mapping = empty_board()
    mapping[1][0] = mapping[1][1] = mapping[1][2] = PLAYER_MARK
    moves[1][0] = moves[1][1] = moves[1][2] = Move(1,0,animal=PLAYER_MARK)
    ai = AIPlayer(3, moves, mapping, winning_combos(3), Difficulty.HARD)
    score = ai.evaluate_ai_score()
    assert score == -10

# ───────────────────────────────────────────────
# AIConfig Tests
# ───────────────────────────────────────────────

def test_aiconfig_get_valid():
    val = AIConfig.get(Difficulty.MEDIUM, "depth")
    assert val == 3


def test_aiconfig_get_invalid_key():
    with pytest.raises(KeyError):
        AIConfig.get(Difficulty.MEDIUM, "nonexistent")


def test_aiconfig_get_invalid_level():
    with pytest.raises(KeyError):
        AIConfig.get("INVALID_LEVEL", "depth")

# ───────────────────────────────────────────────
# select_hard_move and select_very_hard_move Tests
# ───────────────────────────────────────────────

def test_select_hard_move_blocks_win():
    moves, mapping = empty_board()
    mapping[0][0] = PLAYER_MARK
    mapping[1][1] = PLAYER_MARK
    moves[0][0] = Move(0, 0, animal=PLAYER_MARK)
    moves[1][1] = Move(1, 1, animal=PLAYER_MARK)
    ai = AIPlayer(3, moves, mapping, winning_combos(3), Difficulty.HARD)
    move = ai.select_hard_move()
    assert move == (2,2)  # AI should block


def test_select_very_hard_move_blocks_win():
    moves, mapping = empty_board()
    mapping[0][0] = PLAYER_MARK
    mapping[1][1] = PLAYER_MARK
    moves[0][0] = Move(0, 0, animal=PLAYER_MARK)
    moves[1][1] = Move(1, 1, animal=PLAYER_MARK)
    ai = AIPlayer(3, moves, mapping, winning_combos(3), Difficulty.VERY_HARD)
    move = ai.select_very_hard_move()
    assert move == (2,2)  # AI should block

# ───────────────────────────────────────────────
# 4x4 Board Early Opening Tests
# ───────────────────────────────────────────────

def test_should_skip_minimax_opening_true():
    """Ensure AI skips minimax in early 4x4 opening moves (deterministic)."""
    moves = [[Move(r, c, animal=EMPTY) for c in range(4)] for r in range(4)]
    mapping = [[UNDERSCORE] * 4 for _ in range(4)]
    ai = AIPlayer(4, moves, mapping, winning_combos(4), Difficulty.MEDIUM)
    
    # Get remaining empty cells for 4x4
    remaining = ai._get_remaining_moves(all_moves=True)
    
    # Directly test _should_skip_minimax_opening with >12 empty cells
    assert ai._should_skip_minimax_opening(remaining) is True


def test_should_skip_minimax_opening_false_late_game():
    """Ensure AI does not skip minimax in late 4x4 game."""
    moves = [[Move(r, c, animal=EMPTY) for c in range(4)] for r in range(4)]
    mapping = [[UNDERSCORE] * 4 for _ in range(4)]
    # Fill 13 cells, only 3 empty left
    for r in range(4):
        for c in range(4):
            if r * 4 + c < 13:
                moves[r][c] = Move(r, c, animal=PLAYER_MARK)
                mapping[r][c] = PLAYER_MARK
    ai = AIPlayer(4, moves, mapping, winning_combos(4), Difficulty.MEDIUM)
    remaining = ai._get_remaining_moves(all_moves=True)
    assert ai._should_skip_minimax_opening(remaining) is False


def print_score_board(mapping, scores, best_move, cell_width=9):
    """
    Generic function to print board with scores.
    - mapping: current mapping board (symbols)
    - scores: dict {(r,c): score}
    - best_move: tuple (r,c) with best move
    """
    max_score = max(scores.values(), default=1)
    min_score = min(scores.values(), default=0)
    score_range = max_score - min_score if max_score != min_score else 1

    for r in range(len(mapping)):
        row_cells = []
        for c in range(len(mapping[0])):
            if (r,c) in scores:
                val = scores[(r,c)]
                text = f"{val}"
                if (r,c) == best_move:
                    text = f">>{text}<<"
                ratio = (val - min_score)/score_range
                if ratio > 0.66:
                    color = Fore.GREEN
                elif ratio > 0.33:
                    color = Fore.YELLOW
                else:
                    color = Fore.RED
                row_cells.append(color + text.center(cell_width) + Style.RESET_ALL)
            else:
                row_cells.append(mapping[r][c].center(cell_width))
        print("|".join(row_cells))
    print("Best move:", best_move, "\n")


# ───────────────────────────────────────────────
# Visual 3x3 VERY_HARD Boost Test
# ───────────────────────────────────────────────

def test_evaluate_ai_score_very_hard_3x3_boost_desempata_visual():
    size = 3
    moves, mapping = empty_board(size=size)

    mapping[0][0] = PLAYER_MARK
    mapping[1][2] = AI_MARK
    mapping[2][1] = PLAYER_MARK
    moves[0][0] = Move(0,0,animal=PLAYER_MARK)
    moves[1][2] = Move(1,2,animal=AI_MARK)
    moves[2][1] = Move(2,1,animal=PLAYER_MARK)

    ai = AIPlayer(size_board=size, current_moves=moves, mapping_moves=mapping,
                  winning_combos=winning_combos(size), level=Difficulty.VERY_HARD)

    remaining = ai._get_remaining_moves(all_moves=True)
    scores = {}
    for r, c in remaining:
        mapping[r][c] = AI_MARK
        scores[(r,c)] = ai.evaluate_ai_score(boost=True, map=mapping)
        mapping[r][c] = UNDERSCORE

    best_move = max(scores, key=scores.get)

    print("\n3x3 Board Scores (boost=True):")
    print_score_board(mapping, scores, best_move)


# ───────────────────────────────────────────────
# Visual 4x4 VERY_HARD Boost Test
# ───────────────────────────────────────────────

def test_evaluate_ai_score_very_hard_4x4_boost_desempata_visual():
    size = 4
    moves, mapping = empty_board(size=size)

    mapping[0][0] = PLAYER_MARK
    mapping[0][3] = PLAYER_MARK
    mapping[1][1] = AI_MARK
    mapping[1][2] = AI_MARK
    mapping[2][2] = PLAYER_MARK
    moves[0][0] = Move(0,0,animal=PLAYER_MARK)
    moves[0][3] = Move(0,3,animal=PLAYER_MARK)
    moves[1][1] = Move(1,1,animal=AI_MARK)
    moves[1][2] = Move(1,2,animal=AI_MARK)
    moves[2][2] = Move(2,2,animal=PLAYER_MARK)

    ai = AIPlayer(size_board=size, current_moves=moves, mapping_moves=mapping,
                  winning_combos=winning_combos(size), level=Difficulty.VERY_HARD)

    remaining = ai._get_remaining_moves(all_moves=True)
    scores = {}
    for r, c in remaining:
        mapping[r][c] = AI_MARK
        scores[(r,c)] = ai.evaluate_ai_score(boost=True, map=mapping)
        mapping[r][c] = UNDERSCORE

    best_move = max(scores, key=scores.get)

    print("\n4x4 Board Scores (boost=True):")
    print_score_board(mapping, scores, best_move)







