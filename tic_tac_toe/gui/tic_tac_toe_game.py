#!/usr/bin/env python3

"""
TicTacToeGame - Main Controller for GUI Tic Tac Toe Application

This module defines the main tkinter window that orchestrates the entire Tic Tac Toe game.
It manages the GUI components, player interactions, game state flow, and links to backend logic.

Main Features:
- GUI Layout Initialization and Management
- Coordination of Display, Board, Configuration Panels
- Handling Player Inputs and Game Progression
- Logging and Ranking Integration

Author: Andrés David Aguilar Aguilar
Date: 2025-07-18
"""

import logging
import tkinter as tk
import traceback
from tkinter import ttk
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tic_tac_toe.gui.difficulty_panel import DifficultyPanel

from tic_tac_toe.gui.board_game import BoardGame
from tic_tac_toe.gui.buttons_panel import ButtonsPanel
from tic_tac_toe.gui.display_game import DisplayGame
from tic_tac_toe.core.enums import LabelType, Difficulty
from tic_tac_toe.core.helper_methods import parse_entry_bg, strip_ansi
from tic_tac_toe.core.literals import *
from tic_tac_toe.core.log_game import LogGame
from tic_tac_toe.core.logic_game import TicTacToeLogic, Move
from tic_tac_toe.ai.ranking_top_players import RankingTopPlayers
from tic_tac_toe.user_config.user_credentials_gui import UserCredentialsGUI


logger = logging.getLogger(__name__)


class TicTacToeGame(tk.Tk):
    """
    Main window for the TicTacToe game.
    
    Manages:
        - The display, game board, and configuration panel.
        - Communication with the backend logic (TicTacToeLogic).
        - Handle player interactions and game progression.
    """

    # ───────────────────────────────────────────────
    # 1. Initialization and Attributes
    # ───────────────────────────────────────────────

    def __init__(self, logic_game: TicTacToeLogic, mode: str = 'BOTH') -> None:
        """
        Initialize the main window and build all components.

        Args:
            logic_game (TicTacToeLogic): The backend logic engine of the game.
            mode (str): Optional logging mode (default is 'BOTH').

        -----------------------------
        TicTacToeGame Layout Overview
        -----------------------------

        TicTacToeGame (tk.Tk)
        │
        └─── self.frames[WHOLE] : tk.Frame
            │
            ├─── row 0:
            │        └── self.frames[DISPLAY] : DisplayGame
            │            ├── PlayerPanel
            │            ├── MessageLabel
            │            └── OpponentPanel
            │
            └─── row 1:
                    ├── self.frames[BOARD] : BoardGame
                    │   └── N x N Grid of game buttons
                    │
                    └── self.frames[CONFIGURATION_PANEL] : tk.Frame
                            └── self.frames[BUTTONS_PANEL] : ButtonsPanel
                                ├── Radiobuttons Board Size (3x3 / 4x4)
                                ├── Checkbutton Game Mode (Human vs Machine)
                                ├── DifficultyPanel (Semicircular selector)
                                └── Action Buttons: START | RESET | EXIT
        """
        super().__init__()
        self._init_attributes(logic=logic_game, mode=mode)
        UserCredentialsGUI._configure_window_form(
            self, "TicTacToeGame", 1130, 615, y_offset=25
        )
        self.build_board_game()
        self._load_log_cells()


    def _init_attributes(self, logic:TicTacToeLogic, mode: str) -> None:
        """
        Initialize internal state and control structures.

        Args:
            logic (TicTacToeLogic): Logic engine instance.
            mode (str): Logging mode.
        
        Raises:
            TypeError: If logic is not a TicTacToeLogic instance.
        """
        if not isinstance(logic, TicTacToeLogic):
            raise TypeError("Expected an instance of TicTacToeLogic.")

        self._logic: TicTacToeLogic = logic
        self._ranking = RankingTopPlayers(self._logic)
        self._log = LogGame(self._logic, mode='both')

        self.mode: str = mode
        self.size: int = logic.size_board
        self.is_ai_opponent: bool = False
        self.delay: int = 0

        # Tkinter control variables
        self.game_mode_checkbutton: tk.IntVar = tk.IntVar(value=0)  
        self.board_size_radiobutton: tk.BooleanVar = tk.BooleanVar(value=False)  

        # Shared state dictionaries
        self.widgets: dict[str, tk.Widget] = {}
        self.frames: dict[str, tk.Frame] = {}

        # Cached game data
        self.cache: dict = {}
        self.games: dict = {}
        self.ids : list = []
        self.logs: list = []


    # ───────────────────────────────────────────────
    # 2. UI Construction and Layout Setup
    # ───────────────────────────────────────────────

    def build_board_game(self) -> None:
        """Construct the full game UI: display, board, and configuration panel."""
        self._build_root_frame()
        self._build_display_frame()
        self._build_board_and_config_panel()


    def _build_root_frame(self) -> None:
        """Create and configure the root container frame."""
        self.frames[WHOLE] = tk.Frame(self, bg=BLACK)
        self.frames[WHOLE].pack(fill=tk.BOTH, expand=True)
        self.frames[WHOLE].grid_rowconfigure(0, weight=1)
        self.frames[WHOLE].grid_rowconfigure(1, weight=5)
        self.frames[WHOLE].grid_columnconfigure(0, weight=3)
        self.frames[WHOLE].grid_columnconfigure(1, weight=1)


    def _build_display_frame(self) -> None:
        """Build the display frame at the top with player info and messages."""
        self.frames[DISPLAY] = DisplayGame(self.frames[WHOLE], self._logic, self._ranking)
        self.frames[DISPLAY].grid(row=0, column=0, columnspan=2, sticky=tk.N)


    def _build_board_and_config_panel(self) -> None:
        """Build the board game grid and the configuration panel."""
        # Board grid on the left
        self.frames[BOARD] = BoardGame(self.frames[WHOLE], self, self._logic)
        self.frames[BOARD].grid(row=1, column=0)

        # Configuration panel on the right
        self.frames[CONFIGURATION_PANEL] = tk.Frame(
            self.frames[WHOLE],
            bg=BLACK,
            highlightbackground=COLOR_CENTER_HIGHLIGHT,
            highlightthickness=5,
        )
        self.frames[CONFIGURATION_PANEL].grid(row=1, column=1, padx=(5, 10))

        # Buttons panel inside configuration panel
        self.frames[BUTTONS_PANEL] = ButtonsPanel(
            self.frames[CONFIGURATION_PANEL], self, self._logic
        )
        self.frames[BUTTONS_PANEL].grid(row=0, column=0)


    def _load_log_cells(self) -> None:
        """
        Link the main controller's cell references with the LogGame instance.

        This allows the logging mechanism to access and update the
        button cells on the game board for visual feedback or logging purposes.
        """
        self._log.cells = self.cells


    @property
    def cells(self) -> dict[tk.Button, tuple[int, int]]:
        """
        Provides a read-only dictionary mapping each cell button widget
        to its (row, column) position on the game board.

        This property delegates to the BoardGame frame's internal
        cells mapping, exposing the board's button state to the
        main controller for convenient access.
        """
        return self._get_board().cells


    @property
    def button_frames(self) -> dict[tk.Frame, tuple[int, int]]:
        """
        Provides a read-only dictionary mapping each button container frame
        to its (row, column) position on the game board.

        This property accesses the BoardGame frame's internal mapping
        of button frames to their coordinates, enabling controlled
        interaction with the board's UI layout.
        """
        return self._get_board().button_frames

    # ───────────────────────────────────────────────
    # 3. Game Settings & Mode Controls
    # ───────────────────────────────────────────────

    def change_board_size(self, size: int) -> None:
        """
        Change the game board size (e.g., 3x3 to 4x4) and reset the board.

        Args:
            size (int): New board dimension.
        """
        if size == self.size:
            return

        self.withdraw()
        self.size = size
        self.frames[BOARD].destroy()

        self._logic.size_board = size
        self.frames[BOARD] = BoardGame(self.frames[WHOLE], self, self._logic)
        self.frames[BOARD].grid(row=1, column=0)
        self._get_board().clear_internal_maps()
        self._get_board()._create_board_grid()

        self.reset_game(only_size=True)

        self.deiconify()


    def switch_type_of_game(self) -> None:
        """
        Toggle between human vs. human and human vs. machine modes.

        This resets the board and updates the opponent panel and difficulty UI.
        """
        self._logic.toggle_type_of_game()
        self.reset_game()

        players = self._logic.current_players
        difficulty_panel = self._get_difficulty_panel()

        if MACHINE in players:
            difficulty_panel._toggle_canvas(tk.NORMAL)
        else:
            difficulty_panel.reset()

        self._logic.set_all_statistics(self._ranking)

        opponent = self._logic.get_opponent_name()

        display = self._get_display()
        display.update_label(LabelType.NAME, opponent, opponent)

        for label in (LabelType.WINS, LabelType.SCORE):
            display.update_variable(label, opponent)


    def start_game(self) -> None:
        """Start a new game and enable board interaction."""
        display = self._get_display()
        display._setup_ui_data()
        self._setup_display_for_start()
        self._highlight_board_frames()
        self._bind_board_buttons()
        self._toggle_start_reset_btns(RESET, START)
        self._log.process_logs(state=START)

        if display.current_user == MACHINE:
            self.play_machine(start=True)


    def _setup_display_for_start(self) -> None:
        """Configure the display message and colors when the game starts."""
        display = self._get_display()
        user = display.current_user
        animal = display.current_animal
        animal_name = display.current_animal_name
        color = display.current_color

        dark_color = parse_entry_bg(color) == WHITE
        if dark_color: 
            color = WHITE

        display.message_label.config(
            text=f'{user} plays with\n{animal} ({animal_name})',
            fg=color
        )


    def _highlight_board_frames(self) -> None:
        """Highlight all board frames to indicate active game state."""
        for frame in self.button_frames:
            frame.config(
                highlightbackground=COLOR_BOARD_BUTTON_FRAMES, 
                highlightcolor=COLOR_BOARD_BUTTON_FRAMES
            )


    def _bind_board_buttons(self) -> None:
        """Bind mouse events to all board buttons to enable player interaction."""
        for button in self.cells:
            button.bind('<Button-1>', self.play_user)
            button.bind('<ButtonRelease-1>', self.play_machine)


    def reset_game(self, only_size=False) -> None:
        """
        Reset the game to its initial state after RESET button is clicked.

        Args:
            only_size (bool): If True, reset only the board size without
                            clearing difficulty slider.
        """
        self._reset_logic_and_state()
        self._reset_ui()
        self._reset_bindings()
        self.is_ai_opponent = False
        self.cache.clear()
        self._logic.reset_flags()
        self._logic._update_board_mapping()

        if not only_size:
            self._reset_difficulty_scale()

        self._log.update_cells(self.cells)
        self._log.update_size(self.size)
        self._log.process_logs(state=RESET)

        self._toggle_start_reset_btns(START, RESET)


    def _reset_logic_and_state(self) -> None:
        """Reset the backend logic and winning combinations."""
        self._logic._init_game()
        self._logic._calculate_winning_combos()


    def _reset_ui(self) -> None:
        """Reset the display and board UI to initial state."""
        display = self._get_display()
        display._setup_ui_data()
        display.message_label.config(
            text=TEXT_START_NEW_GAME,
            fg=COLOR_DISPLAY_TEXT
        )
        self._get_board().reset_board()


    def _reset_bindings(self) -> None:
        """Remove all user click bindings on the board buttons."""
        self._stop_binds("<Button-1>")
        self._stop_binds("<ButtonRelease-1>")


    def _reset_difficulty_scale(self) -> None:
        """Reset the difficulty slider to 0."""
        self._get_difficulty_slider().set(0)


    def exit_game(self) -> None:
        """Exit the application, saving ranking and logs cleanly."""
        display = self._get_display()
        self._ranking.string_vars = display.get_string_vars()
        self._ranking.games = self._logic.games

        # Restore player state to ensure correct coloring in ranking
        self._logic.restore_current_players_state()
        ranking_str = self._ranking._store_ranking()

        # Remove ANSI codes and store clean ranking in logs
        self._log.logs_file.append(strip_ansi(ranking_str))

        self.destroy()


    # ───────────────────────────────────────────────
    # 4. Player & AI Event Handlers
    # ───────────────────────────────────────────────

    def play_user(self, event: Optional[tk.Event] = None) -> None:
        """
        Handle a move triggered by the human player.

        Args:
            event (Optional[tk.Event]): Click event containing the widget reference.
        """
        if self._logic.get_play_vs_machine():
            self._stop_binds("<Button-1>")

        clicked_button = event.widget
        _, data = self._logic.current_player
        row_, col_ = self.cells[clicked_button]

        move = Move(
            row=row_,
            col=col_,
            animal=data.animal[0],
            color=data.color[0]
        )
        self.process_player_move(move, clicked_button)


    def play_machine(self, start: bool = False, delay: int = 2500) -> None:
        """
        Execute the machine's move with a delay.

        Args:
            start (bool): If True, called at the beginning of the game.
            delay (int): Delay (in milliseconds) before executing the move.
        """
        if not self.check_play_machine():
            return

        if start:
            self._stop_binds("<Button-1>")
        self._stop_binds("<ButtonRelease-1>")

        _, data = self._logic.current_player
        result = self._ai_controller()

        if result is None:
            return  # No move available
        (row_, col_), button = result

        move = Move(row=row_, col=col_, animal=data.animal[0], color=data.color[0])

        self.delay = 0
        self.ids = []

        self._get_display().blink_display_message(
            TEXT_MACHINE_TURN, 
            data.color[0], 
            lambda: self._restart_binds(move, button)
        )


    def _restart_binds(self, move: Move, btn: tk.Button) -> None:
        """
        Re-enable button bindings and execute the machine move.

        Args:
            move (Move): The machine's chosen move.
            btn (tk.Button): The target button widget.
        """
        for button in self.cells:
            button.bind('<Button-1>', self.play_user)
            button.bind('<ButtonRelease-1>', self.play_machine)

        self.process_player_move(move, btn)


    def _stop_binds(self, event: str) -> None:
        """
        Disable all button bindings for a specific event.

        Args:
            event (str): The event sequence string to disable (e.g. "<Button-1>").
        """
        for button in self.cells:
            button.bind(event, "break")


    def check_play_machine(self) -> bool:
        """
        Determine if a machine move should be executed.

        Returns:
            bool: True if playing vs machine and no game-over condition met.
        """
        return (
            self._logic.get_play_vs_machine()
            and not self._logic._has_winner()
            and not self._logic._is_tied()
        )


    # ───────────────────────────────────────────────
    # 5. UI Helpers & Widget State Management
    # ───────────────────────────────────────────────

    def _toggle_start_reset_btns(self, active: str, disable: str) -> None:
        """
        Enable the specified 'active' button and disable the specified 'disable' button.
        Also toggles game mode and board size radio buttons accordingly.

        Args:
            active (str): Name of the button to activate (e.g., 'START').
            disable (str): Name of the button to deactivate (e.g., 'RESET').
        """
        self._toggle_widget_state(active, tk.NORMAL)
        self._toggle_widget_state(disable, tk.DISABLED)

        is_start = (active == START)

        # Toggle radio buttons (e.g., 3x3 and 4x4)
        for size in range(3, 5):
            name = f"{size}x{size}"
            self._toggle_widget_state(name, tk.NORMAL if is_start else tk.DISABLED)

        # Toggle game mode checkbutton
        self._toggle_widget_state(CHECKBUTTON, tk.NORMAL if is_start else tk.DISABLED)

        # Toggle difficulty scale only if playing vs machine
        scale_state = tk.NORMAL if is_start and self.game_mode_checkbutton.get() else tk.DISABLED
        self._set_scale_state(scale_state)


    def _toggle_widget_state(self, name: str, state: str) -> None:
        """
        Toggle the state of a widget using its internal name reference.

        Args:
            name (str): The internal widget name stored in self.widgets.
            state (str): Desired state (e.g., tk.NORMAL or tk.DISABLED).
        """
        widget = self._get_widget(name)
        if widget:
            self._set_widget_state(widget, state)


    def _set_widget_state(self, widget: tk.Widget, state: str) -> None:
        """
        Set the state of a widget with special handling for ttk.Scale widgets.

        Args:
            widget (tk.Widget): The widget to configure.
            state (str): Target state, such as tk.NORMAL or tk.DISABLED.
        """
        try:
            if isinstance(widget, ttk.Scale):
                widget.state(['disabled' if state == tk.DISABLED else '!disabled'])
            elif not isinstance(widget, tk.Frame):
                widget.config(state=state)
        except tk.TclError as e:
            logger.error(f"Error setting widget state: {e}")
            logger.debug(traceback.format_exc())


    def _set_scale_state(self, state: str) -> None:
        """
        Set the state of the difficulty scale widget.

        Args:
            state (str): Desired state, such as tk.NORMAL or tk.DISABLED.
        """
        scale = self._get_difficulty_slider()
        self._set_widget_state(scale, state)


    def _get_widget(self, name: str) -> Optional[tk.Widget]:
        """
        Safely retrieve a widget by name from internal registry.

        Args:
            name (str): Widget identifier key.

        Returns:
            Optional[tk.Widget]: The corresponding widget, or None if not found.
        """
        return self.widgets.get(name)


    # ───────────────────────────────────────────────
    # 6. Core Game Logic Flow
    # ───────────────────────────────────────────────

    def process_player_move(self, move: Move, btn: tk.Button) -> None:
        """
        Validate and execute the given move. Update UI and game state.

        Args:
            move (Move): Move object with coordinates, symbol, and color.
            btn (tk.Button): Button widget where the move is made.
        """
        if not self._logic._is_valid_movement(move):
            return

        _, data = self._logic.current_player
        self._get_board().update_cell(btn, move, data.animal[2])
        self._logic._process_move(move)
        self._log.process_logs(button=btn, state=MOVE)

        if self._logic._has_winner():
            self._handle_winner()
        elif self._logic._is_tied():
            self._handle_tie()
        else:
            self._handle_next_turn()


    def _handle_winner(self) -> None:
        """
        Handle actions and UI updates after a player wins the game.
        """
        user, _ = self._logic.current_player

        self._update_player_statistics(WINNER)
        self._get_display().update_display_message(
            user + TEXT_WINS_THE_GAME, COLOR_DISPLAY_TEXT
        )
        self._get_board().highlight_winning_cells(self._logic._winner_combo)
        self._log.process_logs(state=WINNER)


    def _handle_tie(self) -> None:
        """
        Handle actions and UI updates after a tie.
        """
        self._update_player_statistics(TIED)
        self._get_display().update_display_message(TEXT_TIED_GAME, COLOR_TIED_GAME)
        self._logic.toggle_player()
        self._log.process_logs(state=TIED)


    def _handle_next_turn(self) -> None:
        """
        Toggle player turn and update display message accordingly.
        """
        msg_machine = ""
        if self._logic.get_play_vs_machine():
            user, _ = self._logic.current_player
            if user == MACHINE:
                msg_machine = f'{user.capitalize()} moved...\n'

        self._logic.toggle_player()
        user, data = self._logic.current_player

        msg = f'{user.upper()}\n"{data.animal[0]}" \'s turn'
        msg = msg_machine + msg
        self._get_display().update_display_message(msg, data.color[0])


    # ───────────────────────────────────────────────
    # 7. Subcomponent Accessors & Registration
    # ───────────────────────────────────────────────

    def _get_component(self, key: str) -> Any:
        """
        Generic accessor for UI components stored in self.frames.

        Args:
            key (str): The key of the component to retrieve.

        Returns:
            Any: The component instance.
        """
        return self.frames[key]


    def _get_display(self) -> DisplayGame:
        """Retrieve the DisplayGame instance."""
        return self._get_component(DISPLAY)


    def _get_board(self) -> BoardGame:
        """Retrieve the BoardGame instance."""
        return self._get_component(BOARD)


    def _get_buttons_panel(self) -> ButtonsPanel:
        """Retrieve the ButtonsPanel instance."""
        return self._get_component(BUTTONS_PANEL)


    def _get_difficulty_panel(self) -> 'DifficultyPanel':
        """
        Retrieve the DifficultyPanel instance.

        Returns:
            DifficultyPanel: The difficulty panel widget.
        """
        return self._get_buttons_panel().difficulty_panel


    def _get_difficulty_slider(self) -> ttk.Scale:
        """
        Retrieve the difficulty slider widget from the DifficultyPanel.

        Returns:
            ttk.Scale: The scale widget for difficulty selection.
        """
        return self._get_difficulty_panel().my_scale


    def register_cell(self, button: tk.Button, position: tuple[int, int]) -> None:
        """
        Register a cell button and its board position.

        Args:
            button (tk.Button): The cell button widget.
            position (tuple[int, int]): The (row, column) position.
        """
        self.cells[button] = position


    def register_button_frame(self, frame: tk.Frame, position: tuple[int, int]) -> None:
        """
        Register a button container frame and its board position.

        Args:
            frame (tk.Frame): The frame widget containing the button.
            position (tuple[int, int]): The (row, column) position.
        """
        self.button_frames[frame] = position


    # ───────────────────────────────────────────────
    # 8. AI Controller & Move Selection
    # ───────────────────────────────────────────────

    def _ai_controller(self) -> tuple[Optional[tuple[int, int]], Optional[tk.Button]]:
        """
        Determines the AI's next move coordinates and retrieves the associated button
        based on the current difficulty level selected in the difficulty panel.

        Returns:
            tuple[tuple[int, int], Optional[tk.Button]]: Coordinates of the AI's move as (row, column),
                                                        and the corresponding Tkinter button widget,
                                                        or (None, None) if no valid moves exist.

        Raises:
            RuntimeError: If the difficulty level is unsupported or no moves can be made.
        """
        difficulty_level = self._get_difficulty_panel().level

        if difficulty_level == Difficulty.EMPTY:
            difficulty_level = Difficulty.EASY

        try:
            row_, col_ = self._select_move_by_difficulty(difficulty_level)
            button = self._get_board()._retrieve_button_from_coords((row_, col_))
        except RuntimeError as e:
            logger.error(f"AI move error: {e}")
            logger.debug(traceback.format_exc())
            return None, None
        else:
            return (row_, col_), button


    def _select_move_by_difficulty(self, difficulty_level: str) -> tuple[int, int]:
        """
        Selects the next move coordinates based on the specified difficulty level.

        Args:
            difficulty_level (str): The current difficulty mode (e.g., 'EASY', 'MEDIUM', 'HARD', 'VERY_HARD').

        Returns:
            tuple[int, int]: Coordinates for the AI move.

        Raises:
            RuntimeError: If no valid moves are available or difficulty level is not supported.
        """
        return self._logic.get_ai_move_by_level(difficulty_level)


    # ───────────────────────────────────────────────
    # 9. Player Statistics Update
    # ───────────────────────────────────────────────

    def _update_player_statistics(self, mode: str) -> None:
        """
        Update player statistics (score, wins, games) after a game ends.

        In 'WINNER' mode, only the current player receives 3 points and 1 win.
        In tie or other modes, both players receive 1 point and 0 wins.

        After updating scores, wins, and games in the logic,
        the display is refreshed accordingly.

        Args:
            mode (str): Indicates the outcome of the game. 
                        'WINNER' means someone won; otherwise, it's a tie.
        """
        display = self._get_display()
        current_user, opponent = display.current_user, display.opponent_name
        current_players = (current_user, opponent)

        if mode == WINNER:
            player, _ = self._logic.current_player
            statistics = {player: {SCORE: 3, WINS: 1}}
        else:
            statistics = {user: {SCORE: 1, WINS: 0} for user in current_players}

        for player, stats in statistics.items():
            self._logic.update_score(player, stats[SCORE])
            self._logic.update_wins(player, stats[WINS])

        for user in current_players:
            self._logic.update_games(user, 1)

        display.refresh_scores(self._logic.scores, self._logic.wins)

