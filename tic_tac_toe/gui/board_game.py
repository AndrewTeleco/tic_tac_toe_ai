#!/usr/bin/env python3

"""
BOARD GAME MODULE - GUI Grid Management for the Tic Tac Toe board.

This module handles the creation, rendering, and updating of the main Tic Tac Toe grid.
It is responsible for managing cell widgets, detecting visual states, and highlighting
winning combinations based on game progress.

Responsibilities:
- Create an N x N interactive grid of buttons as the game board.
- Handle cell updates (symbols, colors) after each move.
- Visually highlight winning combinations.
- Reset the board between rounds.
- Provide read-only access to internal widget mappings.

Structure:
- Initialization and Controller Binding
- UI Composition (Grid Creation)
- Visual Update Methods (cell, highlight, reset)
- Internal Mapping and Retrieval Helpers

Author: Andrés David Aguilar Aguilar
Date: 2025-07-03
"""


import tkinter as tk
from typing import TYPE_CHECKING, Optional, Dict, Tuple

if TYPE_CHECKING:
    from tic_tac_toe.gui.tic_tac_toe_game import TicTacToeGame
    from tic_tac_toe.core.logic_game import TicTacToeLogic

from tic_tac_toe.core.literals import *

from tic_tac_toe.core.helper_classes import Move


class BoardGame(tk.Frame):
    """
    Frame responsible for constructing and managing the TicTacToe board UI.

    Responsibilities:
        - Create an N x N grid of buttons representing board cells.
        - Update the appearance of cells when moves occur.
        - Highlight winning cells visually.
        - Reset board state to initial configuration.

    Collaborates with:
        - controller (TicTacToeGame) to register buttons and frames.
        - logic_game (TicTacToeLogic) to access game state if needed.

    Args:
        parent: Parent Tkinter container.
        controller: Main game controller for coordination.
        logic_game: Backend game logic instance.
    """

    # ───────────────────────────────────────────────
    # 1. Initialization
    # ───────────────────────────────────────────────

    def __init__(
        self,
        parent: tk.Widget,
        controller: 'TicTacToeGame',
        logic_game: 'TicTacToeLogic'
    ) -> None:
        super().__init__(parent, bg=BLACK)
        self.controller: 'TicTacToeGame' = controller
        self._logic: 'TicTacToeLogic' = logic_game
        self._button_frames: Dict[tk.Frame, Tuple[int, int]] = {}
        self._cells: Dict[tk.Button, Tuple[int, int]] = {}
        self._create_board_grid()


    @property
    def cells(self) -> dict[tk.Button, tuple[int, int]]:
        """
        Provides a read-only copy of the mapping between cell buttons and their positions.

        Returns:
            dict: A dictionary where keys are button widgets and values are (row, column) tuples.

        Note:
            Returns a copy to prevent external modification of the internal state.
        """
        return self._cells  


    @property
    def button_frames(self) -> dict[tk.Frame, tuple[int, int]]:
        """
        Provides a read-only copy of the mapping between button frame widgets and their positions.

        Returns:
            dict: A dictionary where keys are frame widgets and values are (row, column) tuples.

        Note:
            Returns a copy to prevent external modification of the internal state.
        """
        return self._button_frames


    def clear_internal_maps(self):
        """
        Clear the internal mappings of cells and button frames.

        This method empties the dictionaries that store cell buttons and their associated frames,
        effectively resetting the internal state related to the GUI components.
        """
        self._cells.clear()
        self._button_frames.clear()


    # ───────────────────────────────────────────────
    # 2. UI Composition (Grid Creation)
    # ───────────────────────────────────────────────

    def _create_board_grid(self) -> None:
        """Create an N x N button grid representing the game board."""
        self.main_frame = tk.Frame(
            self,
            bg=COLOR_BG_DEFAULT,
            highlightbackground=COLOR_CENTER_HIGHLIGHT,
            highlightthickness=5
        )
        self.main_frame.grid(
            row=0, column=0, sticky=tk.NSEW, padx=10, pady=10
        )

        for i in range(self.controller.size):
            self.main_frame.grid_rowconfigure(i, weight=1)
            self.main_frame.grid_columnconfigure(i, weight=1)

        for row in range(self.controller.size):
            for col in range(self.controller.size):
                self._create_cell_button(row, col)


    def _create_cell_button(self, row: int, col: int) -> None:
        """
        Create and place a single cell button with a highlighted border.

        Args:
            row: Row index.
            col: Column index.
        """
        button_border = tk.Frame(
            self.main_frame,
            highlightbackground=GRAY, 
            highlightcolor=GRAY,
            highlightthickness=4, 
            bd=0
        )
        button_border.grid(row=row, column=col, padx=3, pady=3, sticky=tk.NSEW)

        button = tk.Button(
            button_border, 
            text=EMPTY, 
            width=4,
            font=(FONT_FAMILY_DEFAULT, self._get_font_size(), BOLD),
            bg=COLOR_BG_DEFAULT, 
            activebackground=COLOR_BG_DEFAULT
        )
        button.grid(row=row, column=col, sticky=tk.NSEW)

        self._cells[button] = (row, col)
        self._button_frames[button_border] = (row, col)

        button_border.grid_rowconfigure(0, weight=1)
        button_border.grid_columnconfigure(0, weight=1)


    def _get_font_size(self) -> int:
        """
        Determine font size based on board size for better UI scaling.

        Returns:
            int: Font size for cell buttons.
        """
        font_size_map = {3: 48, 4: 35}
        return font_size_map.get(self.controller.size, 24)
    

    # ───────────────────────────────────────────────
    # 3. Visual Updates (Cell & Board State)
    # ───────────────────────────────────────────────

    def update_cell(self, button: tk.Button, move: Move, bg_color: Optional[str]) -> None:
        """
        Update the cell's appearance based on a player's move.

        Args:
            button (tk.Button): The button widget of the cell.
            move (Move): Move object with `animal` and `color`.
            bg_color (Optional[str]): Background color for the move.
        """
        if not button:
            raise ValueError("Invalid button reference passed to update_cell.")

        bg_color = bg_color or COLOR_BG_DEFAULT
        button.config(
            text=move.animal,
            fg=move.color,
            bg=bg_color,
            activeforeground=move.color,
            activebackground=bg_color
        )


    def highlight_winning_cells(self, combo: list[tuple[int, int]]) -> None:
        """
        Highlight the borders of cells that form the winning combination.

        Args:
            combo (list[tuple[int, int]]): Coordinates of the winning cells.
        """
        for frame, (row, col) in self.button_frames.items():
            if (row, col) in combo:
                frame.config(highlightbackground=COLOR_HIGHLIGHT_WIN)
            else:
                frame.config(highlightbackground=COLOR_HIGHLIGHT_DEFAULT)


    def reset_board(self) -> None:
        """
        Reset all cells to the initial empty state and clear highlights.
        """
        for button in self.cells.keys():
            button.config(text=EMPTY, bg=COLOR_BG_DEFAULT, fg=BLACK)
        for frame in self.button_frames.keys():
            frame.config(highlightbackground=GRAY, highlightcolor=GRAY)


    # ──────────────────────────────────────────────────────────────
    # 4. Helper methods
    # ──────────────────────────────────────────────────────────────

    def _retrieve_button_from_coords(self, coords: tuple[int, int]) -> Optional[tk.Button]:
        """
        Retrieve a button widget based on its (row, col) coordinates.

        Args:
            coords (tuple[int, int]): Coordinates to search for.

        Returns:
            tk.Button: Corresponding button widget.

        Raises:
            RuntimeError: If no matching button is found.
        """
        for button, (row, col) in self.cells.items():
            if (row, col) == coords:
                return button
        raise RuntimeError("No button available for the provided move coords.")