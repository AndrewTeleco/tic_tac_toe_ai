#!/usr/bin/env python3

"""
TicTacToe Game Logic - Core Mechanics for GUI Integration

This module contains the core game logic for the Tic Tac Toe application.
It manages player configuration, board state, AI evaluation, move validation,
win/tie detection, and overall game state flow for a GUI-driven game.

Main Features:
- Initialization and Configuration
- Player and Turn Management
- Move Validation and Game State
- AI Evaluation and Scoring
- Win and Tie Detection
- Board State Mapping

Raises:
    RuntimeError: If player credentials cannot be loaded from storage.

Author: Andrés David Aguilar Aguilar
Date: 2025-07-17
"""

from itertools import cycle
import logging
import shelve
import traceback
from typing import Dict, Iterator, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from tic_tac_toe.ai.ranking_top_players import RankingTopPlayers

from tic_tac_toe.core.enums import (
    Difficulty,
    LabelType
)

from tic_tac_toe.core.helper_classes import (
    InvalidMoveError,
    Move,
    OpponentCredentials,
    Player
)

from tic_tac_toe.core.helper_methods import normalize_user, make_key
from tic_tac_toe.core.literals import *
from tic_tac_toe.ai.ai_player import AIPlayer

from tic_tac_toe.core.paths import (
    ROOT_PATH_DATA, DB_PATH,
    LOGS_FILE, DEFAULT_LOGS_FILE
)


logger = logging.getLogger(__name__)

class TicTacToeLogic:
    """
    Implements the core game logic for a Tic Tac Toe game.

    Responsibilities include managing players and turns, validating moves,
    tracking the board state, detecting wins and ties, and evaluating 
    moves for AI decision-making.

    This class encapsulates all the rules and mechanics needed to 
    run a complete Tic Tac Toe game with support for human and AI players.

    Attributes:
        size_board (int): Board size (NxN).
        players (Dict[str, Tuple[str, Player]]): Loaded player credentials and data.
        _scores, _wins, _games (Dict[str, int]): Tracking player statistics.
        _current_moves (List[List[Move]]): Current state of the game board with moves.
        _mapping_moves (List[List[str]]): Simplified board representation for AI.
        _winning_combos (List[List[Tuple[int,int]]]): All winning line combinations.
        _winner_exists, _predict_tie (bool): Flags for game state.
        _current_player (Tuple[str, Player]): Player whose turn it is currently.

    """

    # ───────────────────────────────────────────────
    # 1. Initialization and configuration
    # ───────────────────────────────────────────────

    def __init__(self, size_board: int = SIZE_BOARD) -> None:
        """
        Initializes the game logic with the given board size and loads player credentials.

        Sets up initial game flags, player data, game mode, board state, AI player,
        and computes possible winning combinations.

        Args:
            size_board (int): Size of the Tic Tac Toe board (NxN). Must be >= 3.

        Raises:
            ValueError: If size_board is not an integer or less than 3.
        """
        self._validate_board_size(size_board)
        self.size_board: int = size_board

        # Initialize game state and flags
        self._init_game_flags()
        self._init_statistics_dicts()

        # Load player credentials and configure game mode       
        raw_creds = self._load_credentials()
        if not raw_creds:
            raise RuntimeError("Failed to load player credentials.")
        self.players = self._prepare_players(raw_creds)
        self.file_logs_name = raw_creds.get(LOGS_FILE, DEFAULT_LOGS_FILE)

        self._init_game_type_and_players()

        # Set up the game board and AI
        self._init_game()
        self._calculate_winning_combos()
        self._ai_player = AIPlayer(
            self.size_board, 
            self._current_moves, 
            self._mapping_moves, 
            self._winning_combos
        )


    def _validate_board_size(self, size_board: int) -> None:
        """
        Validate the size of the board.

        Args:
            size_board (int): Board size to validate.

        Raises:
            ValueError: If size_board is less than 3 or not an integer.
        """
        if not isinstance(size_board, int) or size_board < 3:
            raise ValueError("Board size must be an integer >= 3.")
        

    def _init_game_flags(self) -> None:
        """
        Initializes flags used to track the game state.

        Flags include:
        - Whether playing versus machine
        - If there is a winner
        - If a tie is predicted
        - The current winning combination
        - All possible winning combinations
        """
        self._vs_machine: bool = False
        self._winner_exists: bool = False
        self._predict_tie: bool = False
        self._winner_combo: list[tuple[int, int]] = []
        self._winning_combos: list[list[tuple[int, int]]] = []


    def reset_flags(self) -> None:
        """
        Reset game state flags for a new game or round.
        Clears winner flags and winning combination.
        """
        self._winner_exists = False
        self._predict_tie = False
        self._winner_combo.clear()


    def _init_statistics_dicts(self) -> None:
        """Initialize statistics dictionaries for scores, wins, and games played."""
        self._scores: Dict[str, int] = {}
        self._wins: Dict[str, int] = {}
        self._games: Dict[str, int] = {}


    def _load_credentials(self) -> Dict[str, Tuple[str, Player]]:
        """
        Loads player credentials from persistent storage.

        Returns:
            Dict[str, Tuple[str, Player]]: username -> (user_id, Player)

        Raises:
            OSError: If no player credentials could be loaded.
        """
        db_path = ROOT_PATH_DATA / DB_PATH
        try:
            with shelve.open(db_path) as credentials:
                return dict(credentials)
        except (OSError, IOError, EOFError, KeyError) as e:
            logger.error(f"[ERROR] Loading credentials: {e}")
            logger.debug(traceback.format_exc())
            return {}


    def _prepare_players(self, raw_credentials: Dict[str, dict]) -> Dict[str, Tuple[str, Player]]:
        """
        Transforms raw credentials into internal player dict and adds MACHINE.

        Args:
            raw_credentials (dict): Raw data loaded from shelve.

        Returns:
            dict: players dict ready for the game.

        Raise:
            RuntimeError: If player credentials failed to be loaded.
        """
        players: Dict[str, Tuple[str, Player]] = {}
        required_keys = (FIRST_USER, SECOND_USER)

        # Build players dictionary
        for user_key in required_keys:
            data = raw_credentials.get(user_key)

            if not data or not all(k in data for k in (USERNAMES, ANIMALS, COLORS)):
                raise RuntimeError(f"Missing or invalid data for {user_key}.")
            
            players[user_key] = (
                data[USERNAMES],
                Player(animal=data[ANIMALS], color=data[COLORS]),
            )
        
        # Add MACHINE based on second user as template
        players[MACHINE] = (MACHINE, players[SECOND_USER][1])
        
        return players


    def _init_game_type_and_players(self) -> None:
        """
        Initializes the game type iterator and the current player cycle.

        Sets up iterators for game types (e.g., player vs player, player vs machine),
        determines current players based on the game type, and initializes the current player.

        Also sets the _vs_machine flag based on the current game type.
        """
        self._game_modes = range(NUM_PLAYERS)
        self._iter_type_of_game: Iterator[int] = cycle(self._game_modes)

        self._current_type_of_game = next(self._iter_type_of_game)
        self._vs_machine = self._current_type_of_game == 1

        self._current_players = self._determine_current_players()
        self._iter_current_players: Iterator[Tuple[str, Player]] = cycle(self._current_players.items())
        self._current_player = next(self._iter_current_players)


    def restore_current_players_state(self) -> None:
        """
        Restores the current players' dictionary and iterator based on the latest credentials.

        This ensures correct color and symbol associations when displaying player-related
        data (e.g., in the ranking table) after switching game modes (e.g., from vs player to vs machine).

        It prevents desynchronization between player identity and their associated visuals.
        """
        self._current_players = {
            data[0]: data[1] for _, data in self.players.items()
            if data[0] != MACHINE or data[0] not in self._current_players
        }
        self._iter_current_players = cycle(self._current_players.items())
        self._current_player = next(self._iter_current_players)


    def set_all_statistics(self, ranking: 'RankingTopPlayers') -> None:
        """
        Safely load player scores, wins, and games from RankingTopPlayers.

        Only fills in values for current players that don't already exist in self._scores, self._wins or self._games.

        Args:
            ranking (RankingTopPlayers): Object holding current ranking stats for players.
        """
        for player in self._current_players:
            norm_player = normalize_user(player)

            # Compose keys
            score_key = make_key(LabelType.SCORE.value, norm_player)
            wins_key = make_key(LabelType.WINS.value, norm_player)

            # Get from ranking or fallback
            score = int(ranking.string_vars.get(score_key, "0"))
            wins = int(ranking.string_vars.get(wins_key, "0"))
            games = int(ranking.games.get(player, 0))

            # Only set if not already present
            self._scores.setdefault(player, score)
            self._wins.setdefault(player, wins)
            self._games.setdefault(player, games)


    def _init_game(self) -> None:
        """
        Initialize the game board and mapping structures.

        Creates empty move objects and underscores for AI mapping.
        """
        self._current_moves = [
            [Move(row=r, col=c) for c in range(self.size_board)]
            for r in range(self.size_board)
        ]
        self._mapping_moves = [
            [EMPTY for _ in range(self.size_board)] for _ in range(self.size_board)
        ]


    def _calculate_winning_combos(self) -> None:
        """
        Calculates all possible winning combinations for the current board size.

        Winning combinations include:
        - All rows
        - All columns
        - The two diagonals

        Stores the result in self._winning_combos as a list of position tuples.
        """
        rows = [[(move.row, move.col) for move in row] for row in self._current_moves]
        columns = [list(col) for col in zip(*rows)]
        first_diag = [(rows[i][i]) for i in range(self.size_board)]
        second_diag = [(rows[i][self.size_board - 1 - i]) for i in range(self.size_board)]
        self._winning_combos = rows + columns + [first_diag, second_diag]


    @property 
    def scores(self) -> dict[str, int]:
        """
        Return a copy of the current players' scores.

        Returns:
            dict[str, int]: Mapping of username to score.
        """
        return self._scores.copy()


    @property
    def wins(self) -> dict[str, int]:
        """
        Return a copy of the current players' win counts.

        Returns:
            dict[str, int]: Mapping of username to win count.
        """
        return self._wins.copy()


    @property
    def games(self) -> dict[str, int]:
        """
        Return a copy of the current players' total games played.

        Returns:
            dict[str, int]: Mapping of username to games played.
        """
        return self._games.copy()


    @property
    def current_player(self) -> tuple[str, Player]:
        """
        Return the current player as a tuple of (name, Player instance).

        Returns:
            tuple[str, Player]: The current player's identifier and Player object.
        """
        return self._current_player


    @property
    def current_players(self) -> dict[str, Player]:
        """
        Return a copy of the current players dictionary.

        Returns:
            dict[str, Player]: Mapping of player names to Player instances.
        """
        return dict(self._current_players)


    # ───────────────────────────────────────────────
    # 2. Player and Turn Management
    # ───────────────────────────────────────────────
        

    def toggle_type_of_game(self) -> None:
        """
        Switch the game mode (PvP <-> PvM), update player sets and current player iterator.

        Raises:
            RuntimeError: If no players are found for the current game type.
        """
        self._current_type_of_game = next(self._iter_type_of_game)
        self._vs_machine = (self._current_type_of_game == 1)

        self._current_players = self._determine_current_players()
        if not self._current_players:
            raise RuntimeError("No players determined for current game type.")
        
        self._iter_current_players = cycle(self._current_players.items())
        self.toggle_player()


    def toggle_player(self) -> None:
        """
        Advance to the next player in the current players iterator.

        Raises:
            RuntimeError: If no players are available to toggle.
        """        
        try:
            self._current_player = next(self._iter_current_players)
        except StopIteration:
            raise RuntimeError("No players available to toggle.")


    def get_play_vs_machine(self) -> bool:
        """
        Returns True if the current game mode is player vs machine.

        Returns:
            bool: True if playing against the machine, False otherwise.
        """
        return self._vs_machine


    def _determine_current_players(self) -> dict[str, Player]:
        """
        Determine the active players dict depending on the current game mode.

        Raises:
            RuntimeError: If the current type of game is invalid or required players are missing.

        Returns:
            dict[str, Player]: Mapping of player names to Player instances.
        """
        if self._current_type_of_game not in {0, 1}:
            raise RuntimeError(f"Invalid game type: {self._current_type_of_game}")

        if self._current_type_of_game == 1:  # Player vs Machine
            if MACHINE not in self.players or FIRST_USER not in self.players:
                raise RuntimeError("Required players not found for vs Machine mode.")
            return {
                MACHINE: self.players[SECOND_USER][1],
                self.players[FIRST_USER][0]: self.players[FIRST_USER][1],
            }

        # Player vs Player mode
        if FIRST_USER not in self.players or SECOND_USER not in self.players:
            raise RuntimeError("Required players not found for vs Player mode.")
        return {
            self.players[FIRST_USER][0]: self.players[FIRST_USER][1],
            self.players[SECOND_USER][0]: self.players[SECOND_USER][1],
        }


    def get_opponent_name(self) -> str:
        """
        Returns the name of the opponent player.

        Returns:
            str: The opponent's name, or "Machine" if playing against the AI.
        """
        if self._vs_machine:
            return MACHINE

        current_player_name, _ = self.current_player
        creds = self.get_opponent_credentials_for(current_player_name)
        return creds.name


    def get_opponent_credentials_for(self, current_player_name: str) -> OpponentCredentials:
        """
        Retrieves the opponent's credentials based on the current player's name.

        Args:
            current_player_name (str): The name of the current player.

        Returns:
            OpponentCredentials: Named tuple with opponent's name, symbol, symbol name,
                                color name, and ANSI color.

        Raises:
            RuntimeError: If the opponent is not found in current players.
        """
        for player_name, player_data in self._current_players.items():
            if player_name != current_player_name:
                return OpponentCredentials(
                    name=player_name,
                    symbol=player_data.animal[0],
                    symbol_name=player_data.animal[1],
                    color_name=player_data.color[0],  # e.g. "red"
                    ans_clr=player_data.color[2],     # e.g. "\033[91m"
                )
        raise RuntimeError("Opponent not found.")


    def get_current_player_info(self) -> tuple[str, Player]:
        """
        Returns the current player's information as a tuple.

        Returns:
            tuple[str, Player]: A tuple containing the current player's name and Player object.
        """
        return self.current_player


    def get_opponent_info(self) -> tuple[str, str, str]:
        """
        Returns basic information about the opponent player.

        Returns:
            tuple[str, str, str]: A tuple containing opponent's name, symbol, and symbol name.
        """
        current_player_name, _ = self.current_player
        creds = self.get_opponent_credentials_for(current_player_name)
        return creds.name, creds.symbol, creds.symbol_name


    def get_ansi_color_for_user(self, user: str) -> str:
        """
        Returns the ANSI color code associated with a given user.

        This method provides consistent color coding when displaying players
        in the ranking table or elsewhere.

        - If the user is MACHINE, returns a fixed golden color.
        - If the user is one of the two active players in the current session,
        returns their assigned ANSI color.
        - All other users (from past sessions) receive a neutral gray color.

        Args:
            user (str): Username of the player.

        Returns:
            str: ANSI escape code string representing the user's color.
        """
        player1_name, player1_data = self.get_current_player_info()
        player2_name = self.get_opponent_name()
        player2_data = self.get_opponent_credentials_for(player1_name)

        if user == MACHINE:
            return ANSI_AQUAMARINE
        if user == player1_name:
            return player1_data.color[2]
        if user == player2_name:
            return player2_data.ans_clr
        
        for _, data in self.players.items():
            if data[0] == user:
                return data[1].color[2]
            
        return ANSI_AQUAMARINE


    def update_score(self, player: str, add_score: int) -> None:
        """
        Increment the score of a given player, wrapping around at 1000.

        If the player is not yet in the internal score dictionary,
        they are initialized with the added score value.

        The score resets to 0 after reaching or exceeding 1000 
        (e.g., 998 + 5 → 3).

        Args:
            player (str): Username whose score will be updated.
            add_score (int): Points to add to the player's score.

        Returns:
            None
        """
        self._scores[player] = (int(self._scores.get(player, 0)) + add_score) % 1000


    def update_wins(self, player: str, add_wins: int) -> None:
        """
        Increment the win count for a given player, wrapping around at 100.

        If the player is not yet in the internal wins dictionary,
        they are initialized with the added win value.

        The win count resets to 0 after reaching or exceeding 100 
        (e.g., 99 + 2 → 1).

        Args:
            player (str): Username whose win count will be updated.
            add_wins (int): Number of wins to add.

        Returns:
            None
        """
        self._wins[player] = (int(self._wins.get(player, 0)) + add_wins) % 100


    def update_games(self, player: str, add_games: int) -> None:
        """
        Increment the total number of games played by a player, wrapping around at 1000.

        If the player is not yet in the internal games dictionary,
        they are initialized with the added game count.

        The count resets to 0 after reaching or exceeding 1000 
        (e.g., 998 + 5 → 3).

        Args:
            player (str): Username whose game count will be updated.
            add_games (int): Number of games to add.

        Returns:
            None
        """
        self._games[player] = (int(self._games.get(player, 0)) + add_games) % 1000


    # ───────────────────────────────────────────────
    # 3. Move Validation and Game State
    # ───────────────────────────────────────────────

    def _is_valid_movement(self, move: Move) -> bool:
        """
        Validate whether a move is allowed.

        Args:
            move (Move): Move to validate.

        Returns:
            bool: True if move is valid, False otherwise.

        Raises:
            InvalidMoveError: If move is out of bounds or invalid.
        """
        r, c = move.row, move.col
        if not (0 <= r < self.size_board and 0 <= c < self.size_board):
            raise InvalidMoveError(f"Move out of board bounds: ({r}, {c})")

        return (
            self._current_moves[r][c].animal == EMPTY_CELL
            and not self._winner_exists
            and not self._predict_tie
        )


    def _process_move(self, move: Move) -> None:
        """
        Apply a move to the board after validating it.

        Args:
            move (Move): Move to apply.

        Raises:
            InvalidMoveError: If the move is invalid or cell is already occupied.
        """
        if not self._is_valid_movement(move):
            raise InvalidMoveError(f"Invalid move at ({move.row}, {move.col})")
        if self._current_moves[move.row][move.col].animal != EMPTY:
            raise InvalidMoveError(f"Cell ({move.row}, {move.col}) is already occupied")

        self._current_moves[move.row][move.col] = move
        self._update_board_mapping()
        self._check_and_predict_tie()

    
    def _has_winner(self) -> bool:
        """
        Checks whether the game has a winner.

        Returns:
            bool: True if a winning condition has been met, False otherwise.
        """
        return self._winner_exists


    def _is_tied(self) -> bool:
        """
        Checks whether the game has ended in a tie.

        A tie occurs when all cells are filled, no winner exists,
        or the game predicts no winning combination is possible.

        Returns:
            bool: True if the game is tied, False otherwise.
        """
        board_full = all(
            move.animal != EMPTY for row in self._current_moves for move in row
        )
        return self._predict_tie or (board_full and not self._has_winner())


    # ───────────────────────────────────────────────
    # 4. AI Evaluation
    # ───────────────────────────────────────────────

    def _update_ai_player(self) -> None:
        """
        Updates the AIPlayer instance with the latest board state.

        This should be called whenever the board state changes.
        """
        self._ai_player.set_current_state(
            self.size_board,
            self._current_moves,
            self._mapping_moves,
            self._winning_combos
        )

    
    def get_ai_move_by_level(self, level: Difficulty) -> tuple[int, int]:
        """
        Retrieves the AI's selected move based on the given difficulty level.

        Args:
            level (Difficulty): The difficulty level for the AI.

        Returns:
            tuple[int, int]: Coordinates (row, column) of the AI's chosen move.

        Raises:
            RuntimeError: If the difficulty level is not supported.
        """
        method_map = {
            Difficulty.EASY: self._ai_player.select_random_move,
            Difficulty.MEDIUM: self._ai_player.select_medium_move,
            Difficulty.HARD: self._ai_player.select_hard_move,
            Difficulty.VERY_HARD: self._ai_player.select_very_hard_move,
        }

        try:
            self._ai_player.level = level
            return method_map[level]()
        except KeyError:
            raise RuntimeError(f"Unsupported AI difficulty level: {level.name}")

    
    # ───────────────────────────────────────────────
    # 5. Win/Tie Detection
    # ───────────────────────────────────────────────

    def _is_combo_blocked(self, win_comb: List[str]) -> bool:
        """
        Returns True if the combo is blocked (both players' symbols present or no empty spots).
        """
        unique = set(win_comb)
        # Combo blocked if it contains three different symbols (shouldn't happen) 
        # or contains two different symbols but none is underscore (empty).
        return len(unique) == 3 or (len(unique) == 2 and UNDERSCORE not in unique)


    def _check_and_predict_tie(self) -> None:
        """
        Analyzes the board to predict if the game will end in a tie.

        Counts blocked winning combinations to determine if no player 
        can win in subsequent moves.

        Sets the internal flag `_predict_tie` to True if a tie is predicted.
        """
        blocked_combos = 0
        total_combos = len(self._winning_combos)

        for combo in self._winning_combos:
            win_comb = [self._mapping_moves[r][c] for r, c in combo]

            if self._check_winner(win_comb, combo):
                return

            if self._is_combo_blocked(win_comb):
                blocked_combos += 1

        self._predict_tie = (blocked_combos == total_combos)


    def _check_winner(self, win_comb: List[str], combo: List[Tuple[int, int]]) -> bool:
        """
        Check if the given combination (line) contains a winner.

        Args:
            win_comb (List[str]): List of symbols in the winning combination (e.g., ['X', 'X', 'X']).
            combo (List[Tuple[int, int]]): Coordinates of the cells in this combination.

        Returns:
            bool: True if a winner is found, False otherwise.

        Side Effects:
            Updates self._winner_exists and self._winner_combo if a winner is detected.
        """
        unique_symbols = set(win_comb)
        # Winner condition: exactly one symbol (not empty or underscore) filling the combo
        if len(unique_symbols) == 1 and EMPTY not in unique_symbols and UNDERSCORE not in unique_symbols:
            self._winner_exists = True
            self._winner_combo = combo.copy()
            return True
        return False


    # ───────────────────────────────────────────────
    # 6. Board State Management
    # ───────────────────────────────────────────────

    def _update_board_mapping(self) -> None:
        """
        Updates the internal board mapping used for AI evaluation and UI display.

        Converts the current moves into a simplified representation where:
        - EMPTY cells become UNDERSCORE
        - Machine player cells become AI_MARK
        - Human player cells become PLAYER_MARK

        Returns:
            None
        """
        for r in range(self.size_board):
            for c in range(self.size_board):
                move = self._current_moves[r][c]
                if move.animal == EMPTY:
                    self._mapping_moves[r][c] = UNDERSCORE
                elif self._is_machine_symbol(move):
                    self._mapping_moves[r][c] = AI_MARK
                else:
                    self._mapping_moves[r][c] = PLAYER_MARK

        self._update_ai_player()


    def _is_machine_symbol(self, move: Move) -> bool:
        """
        Determines if the given move was made by the machine player.

        Args:
            move (Move): The move to check.

        Returns:
            bool: True if the move belongs to the machine player, False otherwise.
        """
        machine = self.players[MACHINE][1]
        return move.animal == machine.animal[0] and move.color == machine.color[0]


















    