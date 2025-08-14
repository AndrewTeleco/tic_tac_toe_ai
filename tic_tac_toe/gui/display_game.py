#!/usr/bin/env python3

"""
DISPLAY GAME MODULE - GUI presentation layer for player information and game state.

This module builds and manages the player display panels and the central message interface
in the Tic Tac Toe game.

Responsibilities:
- Display player info (name, symbol, score, wins)
- Display central blinking or static messages
- Update display dynamically based on game logic
- Encapsulate visual state to maintain UI consistency

Structure:
- Initialization and Player Data Retrieval
- UI Display Composition
- Public Update Methods
- Display Properties
- Utility Helpers

Author: Andrés David Aguilar Aguilar
Date: 2025-07-01
"""

import tkinter as tk
import traceback
import logging
from typing import Optional, TYPE_CHECKING, Callable, Dict, Union

if TYPE_CHECKING:
    from tic_tac_toe.core.logic_game import TicTacToeLogic
    from tic_tac_toe.ai.ranking_top_players import RankingTopPlayers

from tic_tac_toe.core.enums import LabelType
from tic_tac_toe.core.helper_classes import InnerScoreConfig
from tic_tac_toe.core.helper_methods import (
    normalize_user, 
    make_key, 
    get_zfill_pad, 
    parse_entry_bg
)
from tic_tac_toe.core.literals import *
from tic_tac_toe.ai.ranking_top_players import RankingTopPlayers


logger = logging.getLogger(__name__)


class DisplayGame(tk.Frame):
    """
    Frame responsible for constructing the game board display.

    Attributes:
        _current_user (str): Current player's username.
        _current_animal (str): Current player's animal symbol.
        _current_animal_name (str): Current player's animal full name.
        _current_color (str): Current player's color.
        _opponent_name (str): Opponent's username.
        _opponent_animal (str): Opponent's animal symbol.
        _opponent_animal_name (str): Opponent's animal full name.
        _opponent_color (str): Opponent's color.
    """

    # ─────────────────────────────────────────────
    # 1. Initialization and Setup
    # ─────────────────────────────────────────────

    def __init__(self, parent: tk.Frame, logic_game: 'TicTacToeLogic', ranking: 'RankingTopPlayers') -> None:
        """
        Initialize the DisplayGame frame.

        Args:
            parent (tk.Frame): Parent Tkinter frame.
            logic_game (TicTacToeLogic): Game logic handler.
            ranking (RankingTopPlayers): Ranking handler.
        """
        super().__init__(parent, bg=BLACK)

        self._logic: 'TicTacToeLogic' = logic_game
        self._ranking_top_players: 'RankingTopPlayers' = ranking

        self._display_frame: Optional[tk.Frame] = None
        self._center_score: Optional[tk.Frame] = None

        self._string_vars: Dict[str, tk.StringVar] = {}
        self._internal_widgets: Dict[str, Union[tk.Label, tk.Widget]] = {}

        self._current_user: str = FIRST_USER
        self._current_animal: str = AI_MARK
        self._current_animal_name: str = EMPTY
        self._current_color: str = COLOR_PLAYER_SCORE

        self._opponent_name: str = SECOND_USER
        self._opponent_animal: str = PLAYER_MARK
        self._opponent_animal_name: str = EMPTY
        self._opponent_color: str = COLOR_OPPONENT_SCORE

        self._setup_ui_data()
        self._create_board_display()


    def _setup_ui_data(self) -> None:
        """
        Retrieve user and opponent data from the logic handler.

        Sets internal attributes for current player and opponent.

        Handles exceptions by assigning default values and logs errors.
        """
        try:
            current_user, current_data = self._logic.get_current_player_info()
            self._current_user = current_user
            self._current_animal = current_data.animal[0]
            self._current_animal_name = current_data.animal[1]
            self._current_color = current_data.color[0]

            opponent_name, opponent_animal, opponent_animal_name = self._logic.get_opponent_info()
            self._opponent_name = opponent_name
            self._opponent_animal = opponent_animal
            self._opponent_animal_name = opponent_animal_name
            self._opponent_color = (
                self._logic.players[SECOND_USER][1].color[0]
                if opponent_name in self._logic.players[SECOND_USER][0] else COLOR_OPPONENT_SCORE
            )

        except Exception as e:
            logger.error(f"[ERROR] UI data fetch failed: {e}")
            logger.debug(traceback.format_exc())
            # Defaults fallback
            self._current_user = FIRST_USER
            self._current_animal = AI_MARK
            self._current_animal_name = EMPTY
            self._current_color = COLOR_PLAYER_SCORE
            self._opponent_name = SECOND_USER
            self._opponent_animal_name = EMPTY
            self._opponent_animal = PLAYER_MARK
            self._opponent_color = COLOR_OPPONENT_SCORE


    def _create_board_display(self) -> None:
        """
        Create the left, center, and right panels for the game display.

        Calls ranking and logic methods to update statistics display.

        Returns:
            None
        """
        self._display_frame = tk.Frame(
            self,
            bg=BLACK,
            highlightbackground=BLACK,
            highlightthickness=2,
            bd=0
        )
        self._display_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self._ranking_top_players._load_player_statistics(self._current_user, self._opponent_name)
        self._logic.set_all_statistics(self._ranking_top_players)
        self._create_score_panel(self._current_user, self._current_animal, self._current_color)
        self._create_center_panel()
        self._create_score_panel(self._opponent_name, self._opponent_animal, self._opponent_color, reverse=True)
        self._ranking_top_players._show_current_ranking()


    # ─────────────────────────────────────────────
    # 2. UI Composition (Score Panels and Layout)
    # ─────────────────────────────────────────────

    def _create_score_panel(self, user: str, animal: str, color: str, reverse: bool = False) -> None:
        """
        Create a score panel for a player, positioned left or right.

        Uses InnerScoreConfig dataclass to define display properties.

        Args:
            user (str): Player name.
            animal (str): Player symbol/animal icon.
            color (str): Color code for display.
            reverse (bool): If True, panel is placed on right side (typically opponent).

        Returns:
            None
        """

        def make_config(user_inner, clr_inner, font_1, font_2, row_1, row_2, col_1, col_2, index, pady=0, label=None, anml=None, machine=None):
            return InnerScoreConfig(
                user=user_inner,
                clr=clr_inner,
                font_1=font_1,
                font_2=font_2,
                row_1=row_1,
                row_2=row_2,
                col_1=col_1,
                col_2=col_2,
                index=index,
                pady=pady,
                anml=anml,
                label=label,
                machine=machine
            )

        panel = tk.Frame(
            self._display_frame,
            bg=COLOR_BG_DEFAULT,
            highlightbackground=COLOR_HIGHLIGHT,
            highlightthickness=5
        )

        col = 2 if reverse else 0
        panel.grid(row=0, column=col)

        machine = MACHINE if reverse else None

        user_used = self._opponent_name if reverse else user
        color_used = self._opponent_color if reverse else color
        animal_used = self._opponent_animal if reverse else animal

        configs = [
            make_config(
                user_inner=user_used,
                clr_inner=color_used,
                font_1=FONT_SIZE_MEDIUM,
                font_2=FONT_SIZE_LARGE,
                row_1=0,
                row_2=0,
                col_1=0,
                col_2=1,
                index=col,
                anml=animal_used,
                machine=machine
            ),
            make_config(
                user_inner=user_used,
                clr_inner=COLOR_PLAYER_SCORE if reverse else COLOR_OPPONENT_SCORE,
                font_1=FONT_SIZE_SMALL,
                font_2=FONT_SIZE_LARGE,
                row_1=0,
                row_2=1,
                col_1=0,
                col_2=0,
                index=1,
                label=LabelType.WINS,
                machine=machine
            ),
            make_config(
                user_inner=user_used,
                clr_inner=COLOR_PLAYER_SCORE if reverse else COLOR_OPPONENT_SCORE,
                font_1=FONT_SIZE_SMALL,
                font_2=FONT_SIZE_LARGE,
                row_1=0,
                row_2=1,
                col_1=0,
                col_2=0,
                index=0 if reverse else 2,
                label=LabelType.SCORE,
                machine=machine
            )
        ]

        for cfg in configs:
            self._build_inner_score(panel, cfg)


    def _create_center_panel(self) -> None:
        """
        Create the central message panel between player score panels.

        The panel displays status messages such as game start prompt, turn indicators, or win notifications.

        Returns:
            None
        """
        self._center_score = tk.Frame(
            self._display_frame,
            bg=BLACK,
            highlightbackground=COLOR_CENTER_HIGHLIGHT,
            highlightthickness=6
        )
        # Use sticky NS to stretch vertically, ensuring visual balance
        self._center_score.grid(row=0, column=1, sticky=tk.NS)

        self._message_label = tk.Label(
            self._center_score,
            text=TEXT_START_THE_GAME,
            justify=tk.CENTER,
            fg=COLOR_DISPLAY_TEXT,
            width=24,
            font=FONT_DISPLAY,
            bg=BLACK
        )
        self._message_label.grid(row=0, column=0, padx=5, pady=5)


    def _build_inner_score(self, parent_frame: tk.Frame, config: InnerScoreConfig) -> None:
        """
        Build an inner score block within a parent frame based on configuration.

        This includes two labels stacked vertically: top label (usually name or label type)
        and bottom label (score, wins, or symbol), with font and color settings.

        Args:
            parent_frame (tk.Frame): Container frame for this score block.
            config (InnerScoreConfig): Configuration dataclass with display parameters.

        Returns:
            None
        """
        bg_color = parse_entry_bg(config.clr)
        frame = tk.Frame(
            parent_frame,
            bg=bg_color,
            highlightbackground=COLOR_HIGHLIGHT,
            highlightthickness=1
        )
        frame.grid(
            row=0,
            column=config.index,
            sticky=config.sticky
        )

        # Determine top label text: label (e.g. "wins") or user name with line breaks
        top_label_text = config.label.value if config.label else config.user.replace(SPACE, '\n')
        top_label = tk.Label(
            frame,
            font=(FONT_DISPLAY[0], config.font_1, BOLD),
            bg=bg_color,
            fg=config.clr,
            text=top_label_text
        )
        top_label.grid(
            row=config.row_1,
            column=config.col_1,
            padx=config.padx,
            pady=config.pady,
        )

        var = self._get_or_create_stringvar(config.label, config.user)

        # Set initial text for variable labels
        if var and config.label == LabelType.NAME:
            var.set(config.user.replace(SPACE, '\n'))
        elif var and config.anml:
            var.set(config.anml)

        # Choose font family for bottom label: digital style for numeric labels, normal otherwise
        font_family = DIGITAL_STYLE if config.label and config.label != LabelType.NAME else FONT_DISPLAY[0]

        if var:
            # Pad numeric text with zeros for alignment
            var.set(str(var.get()).zfill(get_zfill_pad(config.label)))
            bottom_label = tk.Label(
                frame,
                font=(font_family, config.font_2, BOLD),
                bg=bg_color,
                fg=config.clr,
                textvariable=var
            )
        else:
            bottom_label = tk.Label(
                frame,
                font=(FONT_DISPLAY[0], config.font_2, BOLD),
                bg=bg_color,
                fg=config.clr,
                text=config.anml or EMPTY
            )

        bottom_label.grid(
            row=config.row_2,
            column=config.col_2,
            padx=config.padx,
            pady=config.pady,
        )

        # Save references to labels for later dynamic updates
        self._assign_internal_widgets(config.user, top_label, bottom_label,
                                    config.label.value if config.label else None)

        # If this is the machine player, also assign widgets keyed to MACHINE for easy update
        if config.machine and config.machine != config.user:
            self._assign_internal_widgets(config.machine, top_label, bottom_label,
                                        config.label.value if config.label else None)
            self._get_or_create_stringvar(config.label, config.machine)


    def _assign_internal_widgets(self, user: str, top_label: tk.Label, bottom_label: tk.Label, label: Optional[str]) -> None:
        """
        Store references to top and bottom label widgets in internal dictionary.

        This allows later updating of these labels by normalized user keys and label type.

        Args:
            user (str): Username, normalized for dictionary keys.
            top_label (tk.Label): The top label widget (e.g. player's name or label).
            bottom_label (tk.Label): The bottom label widget (e.g. score or wins).
            label (Optional[str]): Label type string used for key composition.

        Returns:
            None
        """
        norm_user = normalize_user(user)
        key_top = make_key(DISPLAY, norm_user, f"{label}_top" if label else "name_top")
        key_bottom = make_key(DISPLAY, norm_user, f"{label}_bottom" if label else "name_bottom")
        self._internal_widgets[key_top] = top_label
        self._internal_widgets[key_bottom] = bottom_label


    # ─────────────────────────────────────────────
    # 3. Public Interface (External Interactions)
    # ─────────────────────────────────────────────

    def update_label(self, label: LabelType, user: str, text: str) -> None:
        """
        Update the text or textvariable of a label widget for the given user and label type.

        Args:
            label (LabelType): One of NAME, WINS, or SCORE.
            user (str): Player name.
            text (str): New text to display.
        """
        norm_user = normalize_user(user)
        suffix = f"{label.value}_top" if label == LabelType.NAME else f"{label.value}_bottom"
        widget_key = make_key(DISPLAY, norm_user, suffix)
        var_key = make_key(label.value, norm_user)

        widget = self._internal_widgets.get(widget_key)
        var = self._string_vars.get(var_key)

        if var:
            var.set(text.zfill(get_zfill_pad(label)))
            if isinstance(widget, tk.Label):
                widget.config(textvariable=var)
        elif isinstance(widget, tk.Label):
            widget.config(text=text.replace(SPACE, '\n'))


    def update_variable(self, label: LabelType, user: str) -> None:
        """
        Re-assign the StringVar to a label widget after a game mode switch.

        Args:
            label (LabelType): Only WINS or SCORE are valid here.
            user (str): Player name.
        """
        if label not in (LabelType.WINS, LabelType.SCORE):
            return

        norm_user = normalize_user(user)
        widget_key = make_key(DISPLAY, norm_user, f"{label.value}_bottom")
        var_key = make_key(label.value, norm_user)

        widget = self._internal_widgets.get(widget_key)
        var = self._string_vars.get(var_key)

        if var:
            var.set(var.get().zfill(get_zfill_pad(label)))
            if isinstance(widget, tk.Label):
                widget.config(textvariable=var)


    def refresh_scores(self, scores: dict[str, int], wins: dict[str, int]) -> None:
        """
        Refresh the displayed scores and wins for the current active players.

        Args:
            scores (dict[str, int]): Mapping of user → score.
            wins (dict[str, int]): Mapping of user → wins.
        """
        for user in self._logic.current_players:
            if user in scores:
                self.update_label(LabelType.SCORE, user, str(scores[user]))
            if user in wins:
                self.update_label(LabelType.WINS, user, str(wins[user]))


    def get_stringvar(self, label_type: LabelType, user: str) -> Optional[tk.StringVar]:
        """
        Get the StringVar associated with a score label.

        Args:
            label_type (LabelType): WINS or SCORE.
            user (str): Player name.

        Returns:
            Optional[tk.StringVar]: The StringVar if found, else None.
        """
        if label_type not in (LabelType.WINS, LabelType.SCORE):
            return None

        norm_user = normalize_user(user)
        return self._string_vars.get(make_key(label_type.value, norm_user))


    def blink_display_message(self, msg: str, color: str, callback: Callable[[], None]) -> None:
        """
        Show a blinking message for a fixed duration, then execute a callback.

        Args:
            msg (str): Message to blink.
            color (str): Message text color.
            callback (Callable[[], None]): Function to call after blinking finishes.
        """
        max_duration = 2500  # ms
        interval = 500
        elapsed = 0

        def blink():
            nonlocal elapsed
            if elapsed >= max_duration:
                callback()
                return
            blink_msg = msg + ('⌛' if (elapsed // interval) % 2 == 0 else ' ')
            self.update_display_message(blink_msg, color)
            elapsed += interval
            self.after(interval, blink)

        blink()


    def update_display_message(self, text: str, color: str) -> None:
        """
        Update the central display message.

        Args:
            text (str): Message to show.
            color (str): Text color.
        """
        dark_color = parse_entry_bg(color) == WHITE
        if dark_color: 
            color = WHITE

        self.message_label.config(text=text, fg=color)


    # ─────────────────────────────────────────────
    #  4. Properties (Game Metadata)
    # ─────────────────────────────────────────────

    # ── Current player ──

    @property
    def current_user(self) -> str:
        """Return the current player's username."""
        return self._current_user

    @property
    def current_animal(self) -> str:
        """Return the current player's animal symbol."""
        return self._current_animal

    @property
    def current_animal_name(self) -> str:
        """Return the current player's animal name."""
        return self._current_animal_name

    @property
    def current_color(self) -> str:
        """Return the current player's display color."""
        return self._current_color


    # ── Opponent player ──

    @property
    def opponent_name(self) -> str:
        """Return the opponent player's username."""
        return self._opponent_name

    @property
    def opponent_animal(self) -> str:
        """Return the opponent player's animal symbol."""
        return self._opponent_animal

    @property
    def opponent_animal_name(self) -> str:
        """Return the opponent player's animal name."""
        return self._opponent_animal_name

    @property
    def opponent_color(self) -> str:
        """Return the opponent player's display color."""
        return self._opponent_color


    # ── Visuals ──

    @property
    def background_color(self) -> str:
        """Return the parsed background color for the current user."""
        return parse_entry_bg(self.current_color)

    @property
    def message_label(self) -> tk.Label:
        """
        Access the central message label widget.

        :return: The central display message label.
        """
        return self._message_label


    # ─────────────────────────────────────────────
    # 5. Helpers (Utility Methods)
    # ─────────────────────────────────────────────

    def _get_or_create_stringvar(self, label: Optional[LabelType], user: str) -> Optional[tk.StringVar]:
        """
        Retrieve or create a StringVar for a specific user and label.

        Args:
            label (Optional[LabelType]): The type of label (e.g., SCORE, WINS, NAME).
            user (str): The player's username.

        Returns:
            Optional[tk.StringVar]: The associated StringVar instance, or None if label is None.
        """
        if not label:
            return None

        norm_user = normalize_user(user)
        key = make_key(label.value, norm_user)

        if key not in self._string_vars:
            # Check if it already exists in the ranking system
            base_val = self._ranking_top_players.string_vars.get(key)

            # Fallback default value if not found
            default_val = {
                LabelType.WINS.value: DEFAULT_WINS,
                LabelType.SCORE.value: DEFAULT_SCORE,
                LabelType.NAME.value: user.replace(SPACE, '\n')
            }.get(label.value, EMPTY)

            self._string_vars[key] = tk.StringVar(
                value=base_val if base_val is not None else default_val
            )

        return self._string_vars[key]


    def get_string_vars(self) -> dict[str, tk.StringVar]:
        """
        Return the internal dictionary mapping keys to StringVar instances.

        Returns:
            dict[str, tk.StringVar]: A mapping of label keys to StringVars used in the GUI.
        """
        return self._string_vars



