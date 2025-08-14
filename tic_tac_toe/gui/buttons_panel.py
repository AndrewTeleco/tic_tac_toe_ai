#!/usr/bin/env python3

"""
BUTTONS PANEL MODULE

This module defines the ButtonsPanel class, a GUI component for configuring and controlling the Tic Tac Toe game.

Responsibilities:
- Allow user selection of board size (3x3 or 4x4)
- Toggle between game modes (Human vs Machine)
- Select difficulty level via a semicircular gauge
- Provide main action buttons: Start, Reset, and Exit

Structure:
- Board Size Selector (Radiobuttons)
- Game Mode Toggle (Checkbutton)
- Difficulty Selector (Custom Semicircle Widget)
- Action Buttons (with custom labels)

Author: Andrés David Aguilar Aguilar
Date: 2025-07-07
"""


import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic_tac_toe.gui.tic_tac_toe_game import TicTacToeGame
    from tic_tac_toe.core.logic_game import TicTacToeLogic

from tic_tac_toe.gui.difficulty_panel import DifficultyPanel
from tic_tac_toe.core.enums import ActionButtons
from tic_tac_toe.core.helper_methods import normalize_user
from tic_tac_toe.core.literals import *


class ButtonsPanel(tk.Frame):
    """
    Configuration panel for the TicTacToe game UI.

    Includes:
    - Board size selection (3x3 or 4x4)
    - Game mode toggle (vs human or machine)
    - Difficulty level selector (semicircle gauge)
    - Main game control buttons (Start, Reset, Exit)

    Layout structure:
        ButtonsPanel
        ├── Board Size Selector (Radiobuttons)
        │   ├── Label: "Board Size Dimension"
        │   ├── [3x3] Radiobutton
        │   └── [4x4] Radiobutton
        │
        ├── Game Mode Toggle (Checkbutton)
        │   └── [✓] Play vs Machine
        │
        ├── Difficulty Panel (semicircle)
        │   └── DifficultyPanel widget
        │       ├── EASY 😄
        │       ├── MEDIUM 🤔
        │       └── HARD 😨
        │
        └── Action Buttons
            ├── ▶ START
            ├── 🔄 RESET
            └── ❌ EXIT
    """


    def __init__(self, parent: tk.Frame, controller: 'TicTacToeGame', logic_game: 'TicTacToeLogic') -> None:
        super().__init__(parent, bg=BLACK) 
        self.controller = controller 
        self._logic = logic_game
        self.sizes = (3, 4)        
        
        for i in range(4):
            self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._create_board_size_selector() 
        self._create_game_mode_toggle()  
        self._create_difficulty_selector()     
        self._create_action_buttons()   


    # ──────────────────────────────────────────────────────────────
    # 1. Board Size Radiobuttons
    # ──────────────────────────────────────────────────────────────
    
    def _create_board_size_selector(self) -> None:
        """Create radio buttons to select board size (3x3 or 4x4)."""
        radio_frame = tk.Frame(self, bg=BLACK)
        radio_frame.grid(row=0, column=0, sticky=tk.N, pady=(5, 10))

        label = tk.Label(
            radio_frame,
            text=TEXT_BOARD_SIZE_DIMENSION,
            justify=tk.CENTER,
            fg=COLOR_DISPLAY_TEXT,
            bg=COLOR_BG_DEFAULT,
            font=(FONT_FAMILY_DEFAULT, FONT_SIZE_SMALL, BOLD)
        )
        label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        for i, size in enumerate(self.sizes):
            self._add_board_size_radiobutton(radio_frame, i, f"{size}x{size}", size)


    def _add_board_size_radiobutton(self, parent: tk.Frame, index: int, label: str, size: int) -> None:
        """Helper to create a bordered board size radiobutton."""
        border = tk.Frame(
            parent,
            highlightbackground=COLOR_HIGHLIGHT_SIZE_RADIOBUTTONS,
            highlightthickness=4
        )
        border.grid(row=1, column=index, padx=5, pady=3)

        rd_btn = tk.Radiobutton(
            border,
            text=label,
            variable=self.controller.board_size_radiobutton,
            value=index,
            selectcolor=WHITE,
            activebackground=COLOR_SIZE_RADIOBUTTONS,
            activeforeground=COLOR_BG_DEFAULT,
            font=(FONT_FAMILY_DEFAULT, 11, BOLD),
            bg=COLOR_SIZE_RADIOBUTTONS,
            fg=COLOR_BG_DEFAULT,
            command=lambda: self.controller.change_board_size(size)
        )
        rd_btn.grid()
        self.controller.widgets[label] = rd_btn


    # ──────────────────────────────────────────────────────────────
    # 2. Checkbutton Game Mode (Human vs Machine)
    # ──────────────────────────────────────────────────────────────

    def _create_game_mode_toggle(self) -> None:
        """Create checkbutton to toggle between human and AI opponent."""
        check_frame = tk.Frame(self, bg=BLACK)
        check_frame.grid(row=1, column=0, sticky=tk.N, pady=5)

        check = tk.Checkbutton(
            check_frame,
            text=TEXT_PLAY_VS_MACHINE,
            name='checkbutton_vs_machine', 
            bg=COLOR_BG_DEFAULT,
            fg=COLOR_DISPLAY_TEXT,
            font=(FONT_FAMILY_DEFAULT, FONT_SIZE_SMALL, BOLD),
            justify=tk.CENTER,
            variable=self.controller.game_mode_checkbutton,
            selectcolor=COLOR_SELECTOR,
            command=self.controller.switch_type_of_game,
        )
        check.grid(padx=5, pady=5)
        self.controller.widgets[CHECKBUTTON] = check


    # ──────────────────────────────────────────────────────────────
    # 3. Difficulty Panel (Semicircle Visualization)
    # ──────────────────────────────────────────────────────────────

    def _create_difficulty_selector(self) -> None:
        """Add the semicircle difficulty selector widget."""
        container = tk.Frame(self, bg=BLACK)
        container.grid(row=2, column=0, sticky=tk.N, pady=5)

        panel = DifficultyPanel(container, self.controller, self._logic)
        panel.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N)
        self.difficulty_panel = panel
        self.difficulty_panel._toggle_canvas(tk.DISABLED, True)

    # ──────────────────────────────────────────────────────────────
    # 4. Action Buttons (Start, Reset, Exit)
    # ──────────────────────────────────────────────────────────────

    def _create_action_buttons(self):
        """Create Start, Reset and Exit buttons."""
        buttons_frame = tk.Frame(self, bg=BLACK)
        buttons_frame.grid(row=3, column=0, pady=5, sticky=tk.N)

        commands = [
            self.controller.start_game, 
            self.controller.reset_game, 
            self.controller.exit_game
        ]

        for i, (button_enum, command) in enumerate(zip(ActionButtons, commands)):
            self._add_action_button(buttons_frame, i, button_enum.value, command)


    def _add_action_button(self, parent:tk.Frame, index: int, label: str, command: callable) -> None:
        """
        Create a single button and store it in the controller's widget registry.

        Args:
            label (str): The text displayed on the button.
            command (Callable): The function to call when the button is clicked.
            bg_color (str): Background color of the button.
            font_size (int): Font size for the button text.
        """
        frame = tk.Frame(
            parent,
            highlightbackground=COLOR_SIZE_RADIOBUTTONS,
            highlightthickness=3,
            bd=0
        )
        frame.grid(row=0, column=index, padx=10)
        self.controller.frames[label] = frame
        
        button = tk.Button(
            frame,
            text=label,
            fg=COLOR_DISPLAY_TEXT,
            bg=COLOR_BG_DEFAULT,
            width=8,
            justify=tk.CENTER,
            font=(FONT_FAMILY_DEFAULT, 12, BOLD),
            command=command
        )
        button.grid()
        
        key = normalize_user(label).lower()
        self.controller.widgets[key] = button

