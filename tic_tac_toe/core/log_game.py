#!/usr/bin/env python3

"""
LOG GAME MODULE - Logging System for Game Events

This module implements a logging system for the Tic Tac Toe game, allowing
events to be traced in real time through the console, written to a file, or both.

Responsibilities:
- Log key gameplay events (turns, moves, wins, resets, errors).
- Format log messages with timestamps and context.
- Support different output modes: console, file, or both.
- Persist logs to timestamped files inside a logs/ directory.
- Allow game components to trigger log messages without GUI coupling.

Structure:
- LogGame: Central logging class with interface to record and output events.
- Uses `datetime` for timestamp formatting and `pathlib` for file handling.
- Accepts external references to game logic and grid cells for context.

Author: Andrés David Aguilar Aguilar
Date: 2025-07-14
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Tuple, List

if TYPE_CHECKING:
    from tic_tac_toe.core.logic_game import TicTacToeLogic
    from tic_tac_toe.core.helper_classes import Player
    import tkinter as tk

from tic_tac_toe.core.literals import *
from tic_tac_toe.core.paths import ROOT_PATH_LOGS


class LogGame:
    """
    Logging system to trace and store game events in TicTacToe.
    Supports console, file, or both logging modes.
    
    Attributes:
        _logic (TicTacToeLogic): Reference to the game logic instance.
        size (int): Board size (e.g., 3 or 4).
        mode (str): Logging mode ('file', 'console', 'both', or None).
        logs (list[str]): Stored log entries for file output.
        cells (dict): Map of buttons to grid positions, set externally.
    """                      

    def __init__(self, logic_game: 'TicTacToeLogic', mode: Optional[str] = None) -> None:
        """
        Initialize the LogGame instance.

        Args:
            logic_game (TicTacToeLogic): Game logic used to retrieve state and metadata.
            mode (str, optional): Logging mode. Can be 'file', 'console', 'both', or None.
        """
        self._logic = logic_game
        self.size = logic_game.size_board
        self.mode = mode
        self.logs_file: list[str] = []
        self.cells: dict = {}
        self.path = ROOT_PATH_LOGS / self._logic.file_logs_name


    def update_cells(self, cells: dict['tk.Button', tuple[int,int]]) -> None:
        """
        Update the cells dictionary with buttons and their corresponding positions.

        Args:
            cells (dict[tk.Button, tuple[int, int]]): Dictionary where the key is a tkinter
                button and the value is a tuple representing the position (row, column) on the board.
        """
        self.cells = cells


    def update_size(self, size: int) -> None:
        """
        Update the size of the board.

        Args:
            size (int): New size of the board (number of rows and columns).
        """
        self.size = size


    def process_logs(self, button: Optional['tk.Button'] = None, state: Optional[str] = None) -> None:
        """
        Generate and store logs for a game event.

        Args:
            button (tk.Button, optional): Button involved in the action (required for 'move').
            state (Optional[str]): Event type. One of 'move', 'start', 'reset', 'winner', 'tied'.
        """
        user, data = self._logic.current_player

        args = (
            self._logic._winner_combo if state == WINNER 
            else [self.cells[button]] if state == MOVE
            else [0]
        )

        for csl in (0, 1):
            self._generate_log(*args, user=user, data=data, csl=bool(csl), state=state)


    def _generate_log(
        self,
        *args: Tuple[int, int],
        user: Optional[str] = None,
        data: Optional['Player'] = None,
        csl: bool = False,
        state: Optional[str] = None
    ) -> None:
        """
        Create a single log entry for console or file, including a game grid snapshot.

        Args:
            *args (Tuple[int, int]): Board cells affected by the event.
            user (Optional[str]): Current player's username.
            data (Optional[Player]): Visual data (animal, color) for the player.
            csl (bool): True if generating console version (with ANSI color).
            state (Optional[str]): Event type (see process_logs).
        """
        anml, anml_name = data.animal[:2]
        clr, ans_clr = data.color[0].lower(), data.color[2]
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        event = self._compose_event(
            state, user, anml, anml_name, clr, args, csl=csl, ans_clr=ans_clr
        )

        if csl:
            date = f"{ans_clr}{date}{RESET_COLOR}"

        grid = self._log_grid(*args, csl=csl, ans_clr=ans_clr)

        event_lines = event.splitlines()
        first_line = event_lines[0]
        rest_lines = event_lines[1:]

        log_entry = (
            f"\n|TIME: {date}|\n"
            f"|EVENT: {first_line}|\n"
            + "\n".join(rest_lines) + "\n"
            f"|GRID|\n{grid}\n"
        )

        if csl:
            print(log_entry)
        else:
            self.logs_file.append(log_entry)


    def _compose_event(
        self,
        state: str,
        user: str,
        anml: str,
        anml_name: str,
        clr: str,
        args: List[Tuple[int, int]],
        csl: bool = False,
        ans_clr: str = ""
    ) -> str:
        """
        Generate the event description based on the game state.

        Args:
            state (str): Type of event.
            user (str): Player name.
            anml (str): Animal symbol.
            anml_name (str): Animal label.
            clr (str): Color name.
            args (List[Tuple[int, int]]): Board cells affected by the event.
            csl (bool): Whether to apply ANSI color formatting.
            ans_clr (str): ANSI color code for the current player.

        Returns:
            str: Formatted event message.
        """
        def colorize(text: str, color: str) -> str:
            return f"{color}{text}{RESET_COLOR}" if csl else text

        user_disp = colorize(user, ans_clr)
        anml_disp = colorize(f"{anml} ({anml_name})", ans_clr)

        if state == WINNER:
            user_upper = user.upper()
            user_disp = colorize(user_upper, ans_clr)
            return (
                f"{user_disp} HAS WON THE GAME AND GET 3 POINTS 😎...! "
                f"by placing {anml_disp} in {args} board's coordinates."
            )

        if state == TIED:
            return "The game has ended in a match and both players get 1 point 🤝"

        if state == RESET:
            opp = self._logic.get_opponent_credentials_for(user)
            opp_disp = colorize(opp.name, opp.ans_clr)
            opp_anml_disp = colorize(f"{opp.symbol} ({opp.symbol_name})", opp.ans_clr)

            return (
                f"{user_disp} resets the game and keeps playing with {anml_disp}.\n"
                f"The opponent, {opp_disp}, continues with {opp_anml_disp}."
            )

        if state == START:
            return f"{user_disp} STARTS a new game playing with {anml_disp}"

        if state == MOVE:
            row, col = args[0]
            return f"{user_disp} puts {clr} {anml_disp} in {(row, col)} board's coordinates"


    def _log_grid(
        self,
        *args: Tuple[int, int],
        csl: Optional[bool] = None,
        ans_clr: Optional[str] = None
    ) -> str:
        """
        Generate a string representation of the current game board.

        Args:
            *args (Tuple[int, int]): Cells to highlight in the grid.
            csl (Optional[bool]): Whether to include ANSI color formatting.
            ans_clr (Optional[str]): ANSI color code for highlights.

        Returns:
            str: Textual grid representation with optional highlights.
        """
        borders = [['+----+'] * self.size for _ in range(self.size + 1)]

        anmls = [
            [f"| {move.animal if move.animal else SPACE * 2} |" for move in row]
            for row in self._logic._current_moves
        ]

        def content(row, col):
            return anmls[row // 2][col] if row % 2 else borders[row // 2][col]

        def should_color(row, col):
            return csl and ((row // 2, col) in args or (
                not row % 2 and (row // 2 - 1, col) in args))

        rows = len(borders + anmls)

        return '\n'.join([
            ' '.join([
                f"{ans_clr}{content(r, c)}{RESET_COLOR}" if should_color(r, c) else content(r, c)
                for c in range(self.size)
            ])
            for r in range(rows)
        ])


    def print_logs(self) -> None:
        """
        Output all stored logs depending on the current mode.

        - If mode is 'console': print logs to stdout.
        - If mode is 'file': save logs to disk.
        - If mode is 'both': do both.
        """
        if not self.mode:
            print("Logs are deactivated.")
            return

        if self.mode in (LOGS['FILE'], LOGS['BOTH']):
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, 'a', encoding='utf-8') as f:
                f.writelines(self.logs_file)



