# tests/test_ai.py

import pytest
from random import seed
from tic_tac_toe.ai.ai_player import AIPlayer
from tic_tac_toe.core.enums import Difficulty
from tic_tac_toe.core.helper_classes import Move, AIConfig
from tic_tac_toe.core.literals import AI_MARK, PLAYER_MARK, UNDERSCORE, EMPTY

# ───────────────────────────────────────────────
# Helper Functions
# ───────────────────────────────────────────────

def empty_board(size=3):
    """Create an empty board of Moves and visual mapping."""
    moves = [[Move(r, c, animal=EMPTY) for c in range(size)] for r in range(size)]
    mapping = [[UNDERSCORE for _ in range(size)] for _ in range(size)]
    return moves, mapping


def winning_combos_3x3():
    """Return all winning combinations for a 3x3 board."""
    return [
        # Rows
        [(0,0),(0,1),(0,2)],
        [(1,0),(1,1),(1,2)],
        [(2,0),(2,1),(2,2)],
        # Columns
        [(0,0),(1,0),(2,0)],
        [(0,1),(1,1),(2,1)],
        [(0,2),(1,2),(2,2)],
        # Diagonals
        [(0,0),(1,1),(2,2)],
        [(0,2),(1,1),(2,0)],
    ]


def winning_combos_4x4():
    """Return all winning combinations for a 4x4 board."""
    combos = []
    # Rows
    for r in range(4):
        combos.append([(r, c) for c in range(4)])
    # Columns
    for c in range(4):
        combos.append([(r, c) for r in range(4)])
    # Diagonals
    combos.append([(i, i) for i in range(4)])
    combos.append([(i, 3-i) for i in range(4)])
    return combos

# ───────────────────────────────────────────────
# AIPlayer Initialization Tests
# ───────────────────────────────────────────────

def test_aiplayer_initialization():
    moves, mapping = empty_board()
    ai = AIPlayer(size_board=3, current_moves=moves, mapping_moves=mapping,
                  winning_combos=winning_combos_3x3(), level=Difficulty.EASY)
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
    moves[0][0] = Move(0,0,animal=AI_MARK)
    ai = AIPlayer(3, moves, mapping, winning_combos_3x3(), Difficulty.EASY)
    remaining = ai._get_remaining_moves(all_moves=True, mapping=True)
    assert (0,0) not in remaining
    assert len(remaining) == 8

# ───────────────────────────────────────────────
# select_random_move Tests
# ───────────────────────────────────────────────

def test_select_random_move_nonempty():
    seed(42)  # For reproducibility
    moves, mapping = empty_board()
    ai = AIPlayer(3, moves, mapping, winning_combos_3x3(), Difficulty.EASY)
    move = ai.select_random_move()
    assert move in [(r,c) for r in range(3) for c in range(3)]

# ───────────────────────────────────────────────
# select_medium_move Test (deterministic)
# ───────────────────────────────────────────────

from unittest.mock import patch

def test_select_medium_move_blocks_win():
    """Ensure AI blocks opponent's winning move on MEDIUM (deterministic)."""
    moves, mapping = empty_board()
    mapping[0][0] = PLAYER_MARK
    mapping[1][1] = PLAYER_MARK
    moves[0][0] = Move(0,0,animal=PLAYER_MARK)
    moves[1][1] = Move(1,1,animal=PLAYER_MARK)
    ai = AIPlayer(3, moves, mapping, winning_combos_3x3(), Difficulty.MEDIUM)

    with patch.object(AIPlayer, '_introduce_random_error', return_value=False):
        move = ai.select_medium_move()

    # Check that AI blocks any winning line
    remaining_moves = ai._get_remaining_moves(all_moves=True)
    # After AI move, player should not have a winning move
    new_moves = [row[:] for row in moves]
    new_moves[move[0]][move[1]] = Move(move[0], move[1], animal=AI_MARK)
    # Check if any winning combo is fully occupied by PLAYER_MARK
    for combo in winning_combos_3x3():
        assert not all(new_moves[r][c].animal == PLAYER_MARK for r,c in combo)


# ───────────────────────────────────────────────
# evaluate_ai_score Tests
# ───────────────────────────────────────────────

def test_evaluate_ai_score_empty_board():
    moves, mapping = empty_board()
    ai = AIPlayer(3, moves, mapping, winning_combos_3x3(), Difficulty.HARD)
    score = ai.evaluate_ai_score()
    assert score == 0


def test_evaluate_ai_score_ai_wins():
    moves, mapping = empty_board()
    mapping[0][0] = mapping[0][1] = mapping[0][2] = AI_MARK
    moves[0][0] = moves[0][1] = moves[0][2] = Move(0,0,animal=AI_MARK)
    ai = AIPlayer(3, moves, mapping, winning_combos_3x3(), Difficulty.HARD)
    score = ai.evaluate_ai_score()
    assert score == 10


def test_evaluate_ai_score_player_wins():
    moves, mapping = empty_board()
    mapping[1][0] = mapping[1][1] = mapping[1][2] = PLAYER_MARK
    moves[1][0] = moves[1][1] = moves[1][2] = Move(1,0,animal=PLAYER_MARK)
    ai = AIPlayer(3, moves, mapping, winning_combos_3x3(), Difficulty.HARD)
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
    moves[0][0] = Move(0,0,animal=PLAYER_MARK)
    moves[1][1] = Move(1,1,animal=PLAYER_MARK)
    ai = AIPlayer(3, moves, mapping, winning_combos_3x3(), Difficulty.HARD)
    move = ai.select_hard_move()
    assert move == (2,2)  # AI should block


def test_select_very_hard_move_blocks_win():
    moves, mapping = empty_board()
    mapping[0][0] = PLAYER_MARK
    mapping[1][1] = PLAYER_MARK
    moves[0][0] = Move(0,0,animal=PLAYER_MARK)
    moves[1][1] = Move(1,1,animal=PLAYER_MARK)
    ai = AIPlayer(3, moves, mapping, winning_combos_3x3(), Difficulty.VERY_HARD)
    move = ai.select_very_hard_move()
    assert move == (2,2)  # AI should block

# ───────────────────────────────────────────────
# 4x4 Board Early Opening Tests
# ───────────────────────────────────────────────

def test_should_skip_minimax_opening_true():
    """Ensure AI skips minimax in early 4x4 opening moves (deterministic)."""
    moves = [[Move(r, c, animal=EMPTY) for c in range(4)] for r in range(4)]
    mapping = [[UNDERSCORE]*4 for _ in range(4)]
    ai = AIPlayer(4, moves, mapping, winning_combos_4x4(), Difficulty.MEDIUM)
    
    # Get remaining empty cells for 4x4
    remaining = ai._get_remaining_moves(all_moves=True)
    
    # Directly test _should_skip_minimax_opening with >12 empty cells
    assert ai._should_skip_minimax_opening(remaining) is True


def test_should_skip_minimax_opening_false_late_game():
    """Ensure AI does not skip minimax in late 4x4 game."""
    moves = [[Move(r, c, animal=EMPTY) for c in range(4)] for r in range(4)]
    mapping = [[UNDERSCORE]*4 for _ in range(4)]
    # Fill 13 cells, only 3 empty left
    for r in range(4):
        for c in range(4):
            if r*4+c < 13:
                moves[r][c] = Move(r,c,animal=PLAYER_MARK)
                mapping[r][c] = PLAYER_MARK
    ai = AIPlayer(4, moves, mapping, winning_combos_4x4(), Difficulty.MEDIUM)
    remaining = ai._get_remaining_moves(all_moves=True)
    assert ai._should_skip_minimax_opening(remaining) is False
