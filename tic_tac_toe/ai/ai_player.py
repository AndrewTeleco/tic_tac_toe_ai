#!/usr/bin/env python3

"""
AI Player Engine - Intelligent Move Selection for Tic Tac Toe

This module implements the AI logic for the Tic Tac Toe game, 
adapting its strategy according to the selected difficulty level. 

It integrates advanced algorithms such as Minimax with alpha-beta pruning, 
strategic heuristics, and time-limited evaluation for optimal move selection.

Main features:

    - Multiple AI difficulty levels from Easy to Very Hard
    - Strategic evaluation with heuristic scoring functions
    - Minimax algorithm with alpha-beta pruning and depth/time constraints
    - Centralized AI configuration via AIConfig for flexibility
    - Move scoring considering board symmetry and positional advantages
    - Caching system (transposition table) to speed up recursive tree traversal

Compatible with Linux environments and other POSIX-compliant systems.

Author: Andrés David Aguilar Aguilar  
Date: 2025-07-15
"""

from random import choice, random
import time
from typing import List, Union, Literal, Tuple, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from helper_classes import Move

from tic_tac_toe.core.enums import Difficulty
from tic_tac_toe.core.helper_classes import AIConfig
from tic_tac_toe.core.helper_methods import (
    is_winning_combo,
    board_to_str,
    score_combo,
    str_to_board
)

from tic_tac_toe.core.literals import *


class AIPlayer:
    """
    AIPlayer evaluates the current board state and selects moves 
    based on the configured difficulty level using strategies 
    ranging from random to advanced Minimax with heuristics.

    Attributes:
        _current_moves (List[List[Move]]): Logical state of the board,
            each cell contains a Move object with detailed info.
        _mapping_moves (List[List[str]]): Visual representation of the board,
            a matrix of symbols like 'X', 'O', or '_' to evaluate/display.
        _size_board (int): The size of the board (e.g., 3 or 4).
        _winning_combos (List[List[Tuple[int, int]]]): Winning cell sequences.
        _level (Difficulty): AI difficulty level.
        cache (dict[str, int]): Cache for storing evaluated board states.
    """

    # ───────────────────────────────────────────────
    # 1. Initialization and Configuration
    # ───────────────────────────────────────────────

    def __init__(
        self,
        size_board: int,
        current_moves: List[List['Move']],
        mapping_moves: List[List[str]],
        winning_combos: List[List[Tuple[int, int]]],
        level: Difficulty = Difficulty.EASY
    ) -> None:
        """
        Initialize the AIPlayer with the board configuration and difficulty.

        Args:
            size_board (int): Size of the board (e.g., 3 or 4).
            current_moves (List[List[Move]]): Logical board state, each cell is a Move object.
            mapping_moves (List[List[str]]): Visual board state with symbols ('X', 'O', '_').
            winning_combos (List[List[Tuple[int, int]]]): List of winning combinations.
            level (Difficulty): AI difficulty level (default is EASY).
        """
        if not isinstance(level, Difficulty):
            raise ValueError("level must be a Difficulty instance.")
        
        self._size_board = size_board
        self._current_moves = current_moves  # Logical state: Move objects with detailed info
        self._mapping_moves = mapping_moves  # Visual state: symbols for evaluation/display
        self._winning_combos = winning_combos
        self._level = level
        self.cache: dict[str, int] = {}


    def set_current_state(
        self,
        size_board: int,
        current_moves: List[List['Move']],
        mapping_moves: List[List[str]],
        winning_combos: List[List[Tuple[int, int]]]
    ) -> None:
        """
        Update the AI's internal state (used when the board resets or changes).

        Args:
            size_board (int): Updated board size.
            current_moves (List[List[Move]]): Updated logical state of the board.
            mapping_moves (List[List[str]]): Updated visual state of the board.
            winning_combos (List[List[Tuple[int, int]]]): Updated winning combinations.
        """
        self._size_board = size_board
        self._current_moves = current_moves
        self._mapping_moves = mapping_moves
        self._winning_combos = winning_combos
        self.cache.clear()


    @property
    def level(self) -> Difficulty:
        """
        Returns the current difficulty level of the AI.

        Returns:
            Difficulty: The current difficulty enum value.
        """
        return self._level


    @level.setter
    def level(self, value: Difficulty) -> None:
        """
        Sets a new difficulty level for the AI and clears the cache.

        Args:
            value (Difficulty): New difficulty to set.

        Raises:
            ValueError: If value is not an instance of Difficulty.
        """
        if not isinstance(value, Difficulty):
            raise ValueError("level must be a Difficulty instance.")
        self._level = value
        self.cache.clear()


    # ───────────────────────────────────────────────
    # 2. Random AI Logic (EASY level) 😄
    # ───────────────────────────────────────────────

    def select_random_move(self) -> Tuple[int, int]:
        """
        Selects a random available cell from the board.

        Returns:
            Tuple[int, int]: Coordinates (row, col) of the selected move.

        Raises:
            RuntimeError: If no empty cells are available for the AI to move.
        """
        empty_cells: List[Tuple[int, int]] = self._get_remaining_moves(all_moves=True)
        if not empty_cells:
            raise RuntimeError("AI attempted to play, but no empty cells were available.")
        return choice(empty_cells)


    # ───────────────────────────────────────────────
    # 3. Minimax AI Logic 🤔😨🤖
    # ───────────────────────────────────────────────

    # ── 3A. Medium Level

    def select_medium_move(self) -> Tuple[int, int]:
        """
        Selects the next move using basic Minimax (no pruning),
        with a 20% chance to make a random mistake to simulate imperfection.

        Returns:
            Tuple[int, int]: Coordinates (row, col) of the selected move.

        Raises:
            RuntimeError: If no empty cells are available.
        """
        empty_cells: List[Tuple[int, int]] = self._get_remaining_moves(all_moves=True)
        if not empty_cells:
            raise RuntimeError("AI attempted to move but no valid cells are available.")

        # In early 4x4 openings, skip Minimax to reduce computation
        if self._should_skip_minimax_opening(empty_cells):
            return self.select_random_move()

        if self._introduce_random_error(chance=AIConfig.get(self._level, "error")):
            return self.select_random_move()

        return self._evaluate_all_moves_minimax(
            candidates=empty_cells,
            depth=AIConfig.get(self._level, "depth")
        )


    def _introduce_random_error(self, chance: Union[float, None]) -> bool:
        """
        Randomly decides whether to simulate a mistake based on probability.

        Args:
            chance (float | None): Probability between 0 and 1, or None for never.

        Returns:
            bool: True if an error should be simulated.
        """
        return False if chance is None else random() < chance


    def _should_skip_minimax_opening(self, empty_cells: List[Tuple[int, int]]) -> bool:
        """
        Avoids Minimax in early stages of 4x4 games (performance safeguard).

        Args:
            empty_cells (List[Tuple[int, int]]): All current available cells.

        Returns:
            bool: True if early move should be random.
        """
        return self._size_board == 4 and len(empty_cells) > self._size_board ** 2 - 4
    

    def min_max_medium(
        self,
        depth: int,
        turn_max: bool,
        max_depth: int = 3
    ) -> int:
        """
        Basic Minimax algorithm for MEDIUM level.
        No alpha-beta pruning, no heuristics, fixed depth.

        Args:
            depth (int): Current depth in the tree.
            turn_max (bool): Whether it's the AI's turn.
            max_depth (int): Maximum recursion depth.

        Returns:
            int: Evaluation score of the board state.

        Raises:
            TypeError: If depth or max_depth is not integer or turn_max is not boolean.
        """

        if not isinstance(depth, int) or not isinstance(max_depth, int) or not isinstance(turn_max, bool):
            raise TypeError("depth and max_depth must be int, turn_max must be bool")

        score = self.evaluate_ai_score()
        if score in (10, -10):
            return score - depth if turn_max else score + depth

        if not self._get_remaining_moves(mapping=True) or depth >= max_depth:
            return 0

        best = float('-inf') if turn_max else float('inf')

        for row in range(self._size_board):
            for col in range(self._size_board):
                if self._mapping_moves[row][col] != UNDERSCORE:
                    continue

                self._mapping_moves[row][col] = AI_MARK if turn_max else PLAYER_MARK
                eval = self.min_max_medium(depth + 1, not turn_max, max_depth)
                self._mapping_moves[row][col] = UNDERSCORE

                best = max(best, eval) if turn_max else min(best, eval)

        return best
    

    def _evaluate_all_moves_minimax(
        self,
        candidates: List[Tuple[int, int]],
        depth: int
    ) -> Tuple[int, int]:
        """
        Evaluates all valid moves using basic Minimax and selects the best.

        Args:
            candidates (List[Tuple[int, int]]): Available cells.
            depth (int): Maximum depth to evaluate.

        Returns:
            Tuple[int, int]: Best move found using Minimax.
        """
        best_score = float('-inf')
        best_moves: List[Tuple[int, int]] = []

        for r, c in candidates:
            self._mapping_moves[r][c] = AI_MARK
            score = self.min_max_medium(0, turn_max=False, max_depth=depth)
            self._mapping_moves[r][c] = UNDERSCORE

            if score > best_score:
                best_score = score
                best_moves = [(r, c)]
            elif score == best_score:
                best_moves.append((r, c))

        return choice(best_moves)
    

    # ── 3B. Hard Level

    def select_hard_move(self) -> Tuple[int, int]:
        """
        Selects the optimal move using Minimax with alpha-beta pruning.

        Returns:
            Tuple[int, int]: Coordinates (row, col) of the best move.

        Raises:
            RuntimeError: If no valid cells are available.
        """
        best_value = float('-inf')
        best_moves: List[Tuple[int, int]] = []
        candidates = self._get_remaining_moves(all_moves=True)

        if not candidates:
            raise RuntimeError("AI attempted to move but no valid cells are available.")

        for row, col in candidates:
            self._mapping_moves[row][col] = AI_MARK
            value = self.min_max_hard(
                depth=0,
                turn_max=False,
                alpha=float('-inf'),
                beta=float('inf')
            )
            self._mapping_moves[row][col] = UNDERSCORE

            if value > best_value:
                best_value = value
                best_moves = [(row, col)]
            elif value == best_value:
                best_moves.append((row, col))

        # Fallback in case no optimal move found (should not happen, safety net)
        return choice(best_moves) if best_moves else self.select_random_move()


    def min_max_hard(
        self,
        depth: int,
        turn_max: bool,
        alpha: float,
        beta: float
    ) -> int:
        """
        Wrapper for HARD-level Minimax with alpha-beta pruning.

        Args:
            depth (int): Current recursion depth.
            turn_max (bool): Whether it's the AI's turn.
            alpha (float): Alpha cutoff value.
            beta (float): Beta cutoff value.

        Returns:
            int: Evaluation score for the current state.

        Raises:
            TypeError: If inputs are not of expected types.
        """

        if not isinstance(depth, int) or not isinstance(turn_max, bool):
            raise TypeError("depth must be int and turn_max must be bool")
        if not isinstance(alpha, (float, int)) or not isinstance(beta, (float, int)):
            raise TypeError("alpha and beta must be float or int")
            
        return self._minimax_core(
            depth=depth,
            turn_max=turn_max,
            alpha=alpha,
            beta=beta,
            max_depth=AIConfig.get(Difficulty.HARD, "depth"),
            use_time_limit=False
        )


    # ── 3C. Very Hard Level

    def select_very_hard_move(self) -> Tuple[int, int]:
        """
        Selects the best move using full Minimax with pruning, 
        time limit, heuristic boosts, and strategic tie-breaking.

        Returns:
            Tuple[int, int]: Coordinates (row, col) of the chosen move.
        """
        self._start_time = time.perf_counter()
        self._time_limit = AIConfig.get(Difficulty.VERY_HARD, "time_limit")

        best_value = float('-inf')
        best_coords: Tuple[int, int] = (-1, -1)
        candidates: List[Tuple[int, int]] = self._get_remaining_moves(all_moves=True)
        registry: dict[str, Tuple[int, int, int]] = {}

        for row, col in candidates:
            self._mapping_moves[row][col] = AI_MARK
            
            value = self.min_max_very_hard(0, turn_max=False, alpha=float('-inf'), beta=float('inf'))

            if value >= best_value:
                best_value = value
                registry[board_to_str(self._mapping_moves)] = (value, row, col)

            self._mapping_moves[row][col] = UNDERSCORE

        # Filter all top moves with best value
        top_moves = [
            (board_str, val, row, col)
            for board_str, (val, row, col) in registry.items()
            if val == best_value
        ]

        if len(top_moves) == 1:
            _, _, row, col = top_moves[0]
            return (row, col)

        # Use heuristic scoring to break ties
        best_score = float('-inf')
        for board_str, _, row, col in top_moves:
            board = str_to_board(board_str, self._size_board)
            score = self.evaluate_ai_score(boost=True, map=board)
            if score > best_score:
                best_score = score
                best_coords = (row, col)

        return best_coords


    def min_max_very_hard(
        self,
        depth: int,
        turn_max: bool,
        alpha: float,
        beta: float
    ) -> int:
        """
        Performs Minimax with alpha-beta pruning and a time constraint.

        Args:
            depth (int): Current search depth.
            turn_max (bool): Whether it's AI's turn.
            alpha (float): Alpha cutoff.
            beta (float): Beta cutoff.

        Returns:
            int: Score from evaluation function.

        Raises:
            TypeError: If inputs are not of expected types.
        """

        if not isinstance(depth, int) or not isinstance(turn_max, bool):
            raise TypeError("depth must be int and turn_max must be bool")
        if not isinstance(alpha, (float, int)) or not isinstance(beta, (float, int)):
            raise TypeError("alpha and beta must be float or int")

        return self._minimax_core(
            depth=depth,
            turn_max=turn_max,
            alpha=alpha,
            beta=beta,
            max_depth=None,
            use_time_limit=True
        )


    # ───────────────────────────────────────────────
    # 4. Scoring and Heuristics 🎯📈
    # ───────────────────────────────────────────────

    def evaluate_ai_score(self, boost: bool = False, map: Union[List[List[str]], None] = None) -> int:
        """
        Evaluates the current board and returns a numeric score.

        Args:
            boost (bool): Whether to apply strategic heuristics.
            map (list[list[str]] | None): Optional board override.

        Returns:
            int: Heuristic score.
        """
        if map is not None and not isinstance(map, list):
            raise TypeError("Expected map to be a list of lists or None")

        base_score = self._calculate_base_score(map=map)
        return self._apply_boost(base_score, map=map) if boost else base_score


    def _calculate_base_score(self, map: Union[List[List[str]], None] = None) -> int:
        """
        Calculates the base score without strategic boosts.

        Args:
            map (list[list[str]] | None): Optional board.

        Returns:
            int: +10 if AI wins, -10 if player wins, or cumulative neutral score.
        """
        map = map or self._mapping_moves

        total_score = 0
        for combo in self._winning_combos:
            values = [map[r][c] for r, c in combo]
            score = score_combo(
                values, combo, boost=False,
                size_board=self._size_board,
                board=self._mapping_moves
            )
            if score in (10, -10):
                return score  # Immediate win/loss
            total_score += score

        return total_score


    def _apply_boost(self, base_score: int, map: Union[List[List[str]], None] = None) -> int:
        """
        Applies strategic heuristics to boost base score.

        Args:
            base_score (int): Original score.
            map (list[list[str]] | None): Board for evaluation.

        Returns:
            int: Boosted score.
        """
        map = map or self._mapping_moves
        boost_scores: List[float] = []

        for combo in self._winning_combos:
            values = [map[r][c] for r, c in combo]
            if not is_winning_combo(values):
                score = score_combo(
                    values, combo, boost=True,
                    size_board=self._size_board,
                    board=self._mapping_moves
                )
                boost_scores.append(score)

        if not boost_scores:
            return base_score

        max_boost = max(boost_scores)
        other_boosts = sum(s for s in boost_scores if s != max_boost)
        final_boost = max_boost + 0.2 * other_boosts

        return int(round(base_score + final_boost))


    # ───────────────────────────────────────────────
    # 5. Minimax Engine Core ♟️
    # ───────────────────────────────────────────────

    def _is_time_exceeded(self) -> bool:
        """
        Checks whether the AI has exceeded its allowed computation time.

        Returns:
            bool: True if the elapsed time since start exceeds the AI's time limit.
        """
        return (time.perf_counter() - self._start_time) > self._time_limit


    def _get_cache_key(self) -> str:
        """
        Generates a unique string key for the current board state to use in the cache.

        Returns:
            str: Flattened string representation of the current visual board.
        """
        return board_to_str(self._mapping_moves)


    def _evaluate_terminal_state(self, depth: int) -> Union[int, None]:
        """
        Evaluates whether the current board state is terminal (win, loss, or draw).

        Args:
            depth (int): Current depth in the Minimax recursion.

        Returns:
            int | None: Returns the heuristic score if terminal, otherwise None.
        """
        score = self.evaluate_ai_score()
        if abs(score) == 10:  # Win or loss detected
            return score - depth if score > 0 else score + depth

        # No moves left means a draw
        if not self._get_remaining_moves(all_moves=True, mapping=True):
            return 0

        return None


    def _minimax_core(
        self,
        depth: int,
        turn_max: bool,
        alpha: float,
        beta: float,
        max_depth: Union[int, None],
        use_time_limit: bool = False
    ) -> int:
        """
        Core Minimax algorithm with alpha-beta pruning and optional time limit.

        Args:
            depth (int): Current recursion depth.
            turn_max (bool): Whether the AI is maximizing (True) or minimizing (False).
            alpha (float): Best value that the maximizer currently can guarantee.
            beta (float): Best value that the minimizer currently can guarantee.
            max_depth (int | None): Maximum allowed recursion depth (None for unlimited).
            use_time_limit (bool): If True, terminates early if time limit exceeded.

        Returns:
            int: Heuristic score representing the desirability of the current board state.
        """

        # Check if the AI has exceeded its computation time limit
        if use_time_limit and self._is_time_exceeded():
            return self.evaluate_ai_score()

        # Check recursion depth limit
        if max_depth is not None and depth >= max_depth:
            return self.evaluate_ai_score()

        # Generate cache key and check if result already computed
        key = self._get_cache_key()
        if key in self.cache:
            return self.cache[key]

        # Evaluate terminal conditions: win, loss, or draw
        terminal_score = self._evaluate_terminal_state(depth)
        if terminal_score is not None:
            return terminal_score

        # Get remaining moves, sorted by priority (center > corners > edges)
        remaining_moves = self._get_remaining_moves(all_moves=True, mapping=True)

        def move_priority(pos: Tuple[int, int]) -> int:
            row, col = pos
            center = self._size_board // 2
            if (row, col) == (center, center):
                return 3  # center is highest priority
            elif (row in (0, self._size_board - 1) and col in (0, self._size_board - 1)):
                return 2  # corners next
            else:
                return 1  # edges last

        remaining_moves.sort(key=move_priority, reverse=True)

        best = float('-inf') if turn_max else float('inf')

        # Recursively explore moves
        for row, col in remaining_moves:
            self._mapping_moves[row][col] = AI_MARK if turn_max else PLAYER_MARK
            val = self._minimax_core(
                depth + 1,
                not turn_max,
                alpha,
                beta,
                max_depth,
                use_time_limit
            )
            self._mapping_moves[row][col] = UNDERSCORE

            if turn_max:
                if val > best:
                    best = val
                if val > alpha:
                    alpha = val
            else:
                if val < best:
                    best = val
                if val < beta:
                    beta = val

            # Alpha-beta pruning cutoff
            if beta <= alpha:
                break

        self.cache[key] = best
        return best


    # ───────────────────────────────────────────────
    # 6. Board Tools and Utilities 🧰
    # ───────────────────────────────────────────────

    def _get_remaining_moves(
        self,
        all_moves: bool = False,
        mapping: bool = False
    ) -> Union[List[Tuple[int, int]], Tuple[int, int], Literal[False]]:
        """
        Returns available positions on the board.

        Args:
            all_moves (bool): If True, returns a list of all available positions.
                            If False, returns the first available position found.
            mapping (bool): If True, uses the visual board (_mapping_moves);
                            otherwise uses the logical board (_current_moves).

        Returns:
            List[Tuple[int, int]]: List of (row, col) coordinates if all_moves is True.
            Tuple[int, int]: Single (row, col) coordinate if all_moves is False.
            False: If the board is full (no available moves).

        Raises:
            TypeError: If 'all_moves' or 'mapping' are not booleans.
        """
        if not isinstance(all_moves, bool):
            raise TypeError(f"'all_moves' must be bool, got {type(all_moves).__name__}")
        if not isinstance(mapping, bool):
            raise TypeError(f"'mapping' must be bool, got {type(mapping).__name__}")

        # Choose the board: visual or logical.
        board = (
            self._mapping_moves if mapping
            else [[move.animal for move in row] for row in self._current_moves]
        )

        available: List[Tuple[int, int]] = [
            (r, c)
            for r in range(self._size_board)
            for c in range(self._size_board)
            if board[r][c] == (UNDERSCORE if mapping else EMPTY)
        ]

        if all_moves:
            return available
        else:
            return available[0] if available else False


