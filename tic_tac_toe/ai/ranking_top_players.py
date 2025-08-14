#!/usr/bin/env python3

"""
RANKING TOP PLAYERS MODULE - Player Rankings and Statistics Management

This module manages the storage, retrieval, and presentation of player ranking data
for the Tic Tac Toe game. It interacts with persistent storage to save player scores
and wins, and provides formatted output for display in the UI and console.

Responsibilities:
- Load and initialize player ranking data from persistent storage.
- Update and maintain player scores and win counts.
- Save updated ranking data safely back to storage.
- Format ranking tables with color-coded highlights for top players.
- Provide interfaces for other modules to access ranking information.

Structure:
- Constants defining ANSI color codes for styled console output.
- RankingTopPlayers class handling all ranking logic and persistence.
- Methods for loading, saving, updating, and formatting ranking data.

Author: Andrés David Aguilar Aguilar
Date: 2025-07-11

"""

import logging
import shelve
from typing import Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from tic_tac_toe.core.logic_game import TicTacToeLogic

from tic_tac_toe.core.enums import LabelType
from tic_tac_toe.core.helper_methods import normalize_user, make_key
from tic_tac_toe.core.literals import *
from tic_tac_toe.core.paths import ROOT_PATH_DATA, RANKING_PLAYERS_SHELVE


logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────
# ANSI escape codes for styled console output in player rankings
# ─────────────────────────────────────────────────────────────────

ANSI_SILVER = "\033[38;2;192;192;192m"        # Color used to indicate second place players
ANSI_BRONZE = "\033[38;2;205;127;50m"         # Color applied to third place players
ANSI_MAGENTA_SOFT = "\x1b[38;2;255;153;255m"  # Soft magenta used for subtle emphasis on ranking list borders


class RankingTopPlayers:
    """
    Handles ranking data storage, retrieval and formatting for Tic Tac Toe players.

    - Loads and initializes player scores and wins.
    - Persists data in shelve-based storage.
    - Generates formatted ranking tables for display.
    """
    RANKING_DB_PATH = ROOT_PATH_DATA / RANKING_PLAYERS_SHELVE
    
    # ───────────────────────────────────────────────
    # 1. Initialization
    # ───────────────────────────────────────────────

    def __init__(self, logic_game: 'TicTacToeLogic'):
        self._logic = logic_game
        self._string_vars = {}
        self._games = {}


    # ───────────────────────────────────────────────
    # 2. Properties (Accessors and Mutators)
    # ───────────────────────────────────────────────

    @property
    def string_vars(self) -> dict:
        """
        Get the dictionary of string variables.

        Returns:
            dict: A dictionary containing string variables used in the class.
        """
        return self._string_vars


    @string_vars.setter
    def string_vars(self, new_vars: dict) -> None:
        """
        Replace the internal StringVar mapping with a new one.

        Args:
            new_vars (dict): Dictionary mapping keys to string representations of scores and wins.

        This is useful when syncing GUI state with the backend logic after mode switches.
        """
        if not isinstance(new_vars, dict):
            raise ValueError("Expected a dictionary for string_vars.")
        self._string_vars = new_vars

    
    @property
    def games(self) -> dict:
        """
        Get the dictionary of total games played per user.

        Returns:
            dict: Mapping of username → games played.
        """
        return self._games


    @games.setter
    def games(self, new_games: dict) -> None:
        """
        Set the dictionary of total games played per user.

        Args:
            new_games (dict): A dictionary mapping usernames to games played.
        """
        self._games = new_games


    # ───────────────────────────────────────────────
    # 3. Data Loading and Fallback Initialization
    # ───────────────────────────────────────────────

    def _load_player_statistics(self, user: str, opponent_name: str) -> None:
        """
        Load wins, games and score from persistent storage (shelve) into string variables.

        Args:
            user: The current user's name.
            opponent_name: The opponent's user name.
        """
        users = [user, opponent_name, MACHINE]

        try:
            with shelve.open(self.RANKING_DB_PATH) as previous_ranking:
                for user in users:
                    normalized_user = normalize_user(user)
                    user_data = previous_ranking.get(user, {})

                    for label in LabelType:
                        key = make_key(label.value, normalized_user)
                        default_val = DEFAULT_WINS if label == LabelType.WINS else DEFAULT_SCORE
                        val = user_data.get(label.value.lower(), default_val)
                        self._string_vars[key] = val
                    self._games[user] = user_data.get('games', DEFAULT_GAMES)
                
        except (OSError, IOError) as e:
            logger.warning(
                f"Could not load rankings for user '{user}' or opponent '{opponent_name}': {e}"
            )
            self._initialize_default_scores(users)


    def _initialize_default_scores(self, users: List[str]) -> None:
        """
        Initialize default scores and wins for given users.

        Args:
            users: List of usernames to initialize.
        """
        for user in users:
            normalized_user = normalize_user(user)
            for label in LabelType:
                key = make_key(label.value, normalized_user)
                default_val = DEFAULT_WINS if label == LabelType.WINS else DEFAULT_SCORE
                self._string_vars[key] = default_val
            self._games[user] = DEFAULT_GAMES


    # ───────────────────────────────────────────────
    # 4. Data Storage and Updating
    # ───────────────────────────────────────────────

    def _store_ranking(self) -> str:
        """
        Save the current top players list to the shelve database,
        display the ranking.
        """
        with shelve.open(self.RANKING_DB_PATH, flag='c') as db:
            for player_name in self._games:
                data = self._get_player_stats(player_name)
                db[player_name] = data

        return self._show_current_ranking()


    def _get_player_stats(self, player_name: str) -> Dict[str, object]:
        """
        Compute and return the player's stats dictionary for storage.

        Args:
            player_name (str): The username of the player.

        Returns:
            Dict[str, object]: Dictionary containing wins, score, games played, and win rate percentage.
        """
        normalized_player = normalize_user(player_name)

        wins_key = make_key(LabelType.WINS.value, normalized_player)
        score_key = make_key(LabelType.SCORE.value, normalized_player)

        def get_value(key):
            val = self._string_vars.get(key, 0)
            # Attempt to get the real value if it's a StringVar
            if hasattr(val, 'get') and callable(val.get):
                try:
                    return int(val.get())
                except Exception:
                    return 0
            try:
                return int(val)
            except Exception:
                return 0

        wins = get_value(wins_key)
        score = get_value(score_key)

        games = int(self._games.get(player_name, 0))

        try:
            win_rate = round((wins / games) * 100, 2)
        except ZeroDivisionError:
            win_rate = 0.0

        return {
            'wins': wins,
            'score': score,
            'games': games,
            'rate': f"{win_rate} %"
        }


    # ───────────────────────────────────────────────
    # 5. Display Formatting Methods
    # ───────────────────────────────────────────────

    def _show_current_ranking(self) -> str:
        """
        Retrieve the current ranking from storage, format and print it.

        Returns:
            str: Formatted string of the current ranking table.
        """
        with shelve.open(self.RANKING_DB_PATH) as db:
            ranking_list: List[Tuple[str, int, int, int, str]] = [
                (
                    player, int(data[WINS.lower()]), 
                    int(data[SCORE.lower()]), 
                    int(data[GAMES.lower()]), 
                    data[RATE.lower()]
                )
                for player, data in db.items()
            ]

        ranking_list.sort(
            key=lambda x: (float(x[4].split()[0]), x[2]),  # (Sort by rate, score)
            reverse=True
        )

        headers = [POS, USER, GAMES, WINS, SCORE, RATE]
        col_widths = [11, 20, 13, 12, 13, 14]

        title = f"{ANSI_MAGENTA_SOFT}" + " 😎 TOP PLAYERS LIST 😎 ".center(88, '-') + f"{RESET_COLOR}"
        border_line = f"{ANSI_MAGENTA_SOFT}" + "-" * 90 + f"{RESET_COLOR}"

        ranking_str = f"\n{title}\n"
        ranking_str += self._format_ranking_header(headers, col_widths) + "\n"

        for idx, player_stats in enumerate(ranking_list, 1):
            ranking_str += self._format_ranking_line(idx, player_stats, headers, col_widths) + "\n"

        ranking_str += f"{border_line}\n\n"

        print(ranking_str)
        return ranking_str


    def _format_ranking_header(self, headers: List[str], col_widths: List[int]) -> str:
        """
        Format and return the ranking table header string with colored pipes and olive-colored underscores.
        """
        header_line = ""
        for header, width in zip(headers, col_widths):
            header_line += f"{ANSI_AQUAMARINE}|"
            header_text = header.center(width, UNDERSCORE)
            header_line += f"{header_text}"
        header_line += f"|{RESET_COLOR}"
        return header_line


    def _format_ranking_line(
        self,
        position: int,
        player_stats: Tuple[str, int, int, int, str],
        headers: List[str],
        col_widths: List[int]
        ) -> str:
        """
        Format a single line of the ranking table with colors and padding.

        Args:
            position (int): The player's position in the ranking.
            player_stats (Tuple[str, int, int, int, str]): Player's stats (username, wins, score, games, rate).
            headers (List[str]): List of column headers.
            col_widths (List[int]): Corresponding widths for each column.

        Returns:
            str: Formatted colored string representing one row of the ranking table.
        """
        user, wins, score, games, rate = player_stats
        ansi_user_color = self._logic.get_ansi_color_for_user(user)

        pos_color = {
            1: ANSI_GOLD,
            2: ANSI_SILVER,
            3: ANSI_BRONZE
        }.get(position, ANSI_AQUAMARINE)

        if pos_color != ANSI_AQUAMARINE:
            ansi_user_color = pos_color

        def colorize(text: str, color: str) -> str:
            return f"{color}{text}{RESET_COLOR}"

        line = ANSI_AQUAMARINE
        for header, width in zip(headers, col_widths):
            line += f"{ANSI_AQUAMARINE}|{RESET_COLOR}"
            if header == POS:
                pos_str = str(position).center(width)
                pos_str = colorize(pos_str, pos_color)
                line += pos_str
            elif header == USER:
                user_str = colorize(user.center(width), ansi_user_color)
                line += user_str
            elif header == WINS:
                wins_str = colorize(str(wins).zfill(2).center(width), ansi_user_color)
                line += wins_str
            elif header == SCORE:
                score_str = colorize(str(score).zfill(3).center(width), ansi_user_color)
                line += score_str
            elif header == GAMES:
                games_str = colorize(str(games).zfill(3).center(width), ansi_user_color)
                line += games_str
            elif header == RATE:
                rate_str = colorize(rate.center(width), ansi_user_color)
                line += rate_str

        line += f"{ANSI_AQUAMARINE}|{RESET_COLOR}"
        return line
