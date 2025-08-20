#!/usr/bin/env python3

"""
DIFFICULTY PANEL MODULE - GUI panel for AI difficulty selection in the Tic Tac Toe game.

This module constructs the semicircle-based difficulty selector interface, allowing users
to choose AI difficulty levels from EASY to VERY HARD.

Responsibilities:
- Build and display the AI difficulty selector UI
- React to user selections and notify the main game
- Provide visual feedback for selected difficulty
- Encapsulate difficulty-related state for easy integration

Structure:
- Initialization and Layout Setup
- Difficulty Button Generation and Event Binding
- Difficulty State Management
- Public Accessors and Resets

Author: Andrés David Aguilar Aguilar
Date: 2025-07-02
"""

import math
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Optional, List, Tuple

if TYPE_CHECKING:
    from tic_tac_toe.gui.tic_tac_toe_game import TicTacToeGame
    from tic_tac_toe.core.logic_game import TicTacToeLogic

from tic_tac_toe.core.enums import Difficulty
from tic_tac_toe.core.literals import *


# ───────────────────────────────────────────────
# Constants for DifficultyPanel and Dashboard UI
# ───────────────────────────────────────────────

CANVAS_WIDTH = 225  # Width of the dashboard canvas
CANVAS_HEIGHT = 165  # Height of the dashboard canvas
ARC_THICKNESS = 65  # Thickness of each difficulty arc
POINTER_LENGTH = 75  # Length of the pointer arrow
POINTER_OFFSET = 5  # Radius of center circle (pointer base)

ARC_START_ANGLE = 0  # Starting angle for first arc (degrees)
ARC_EXTENT_ANGLE = 45  # Angle extent of each arc segment (degrees)

ARC_BBOX_X1, ARC_BBOX_Y1 = 35, 35  # Bounding box top-left corner for arcs
ARC_BBOX_X2, ARC_BBOX_Y2 = 190, 190  # Bounding box bottom-right corner for arcs

_DIFFICULTY_RANGES = {
    Difficulty.EMPTY: (0, 0),
    Difficulty.EASY: (1, 45),
    Difficulty.MEDIUM: (46, 90),
    Difficulty.HARD: (91, 135),
    Difficulty.VERY_HARD: (136, 180)
}


class DifficultyPanel(tk.Frame):
    """
    Dashboard panel for selecting the AI opponent difficulty.

    This panel presents a semicircular selector with arcs representing
    difficulty levels, a pointer indicating the current selection, and
    a slider control for user interaction.

    Args:
        parent (tk.Frame): Parent container frame.
        controller (TicTacToeGame): Main app controller instance.
        logic_game (TicTacToeLogic): Backend game logic.

    Usage example:
        panel = DifficultyPanel(parent_frame, controller, logic_game)
        panel.grid(...)
        # To reset panel state:
        panel.reset()
    """

    # ───────────────────────────────────────────────
    # 1. Initialization
    # ───────────────────────────────────────────────


    def __init__(
        self,
        parent: tk.Frame,
        controller: 'TicTacToeGame',
        logic_game: 'TicTacToeLogic'
    ) -> None:
        super().__init__(parent)
        self.controller = controller
        self._logic = logic_game
        self._level: str = Difficulty.EMPTY.mode
        self.parent = parent
        self._arc_start_angle = ARC_START_ANGLE  # reset per drawing

        self._build_panel()


    def _build_panel(self) -> None:
        """Build the dashboard canvas, arcs, pointer, slider, and labels."""
        self.canvas = tk.Canvas(
            self.parent,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg=BLACK,
            highlightthickness=0
        )

        self.id_canvas: List[Tuple[int, str, str]] = []

        # Draw arcs for each difficulty except EMPTY
        for difficulty in Difficulty:
            if difficulty is not Difficulty.EMPTY:
                self._draw_arc(difficulty.mode, difficulty.bg)

        # Draw small center circle (pointer base)
        center_x = center_y = CANVAS_WIDTH // 2
        self.id_canvas.append((
            self.canvas.create_oval(
                center_x - POINTER_OFFSET,
                center_y - POINTER_OFFSET,
                center_x + POINTER_OFFSET,
                center_y + POINTER_OFFSET,
                fill=BLUE
            ),
            'fill',
            BLUE
        ))

        # Initial pointer at 0 degrees (pointing right)
        self.pointer = self.canvas.create_line(
            center_x, center_y,
            center_x + POINTER_LENGTH * math.cos(math.radians(0)),
            center_y - POINTER_LENGTH * math.sin(math.radians(0)),
            width=6, arrow=tk.LAST, fill=BLUE
        )

        # Slider style configuration
        style = ttk.Style()
        style.configure(SLIDER_STYLE, background=COLOR_BG_DEFAULT)

        self.my_scale = ttk.Scale(
            self.parent,
            from_=0, to=180,
            orient=tk.HORIZONTAL,
            command=self.update_dashboard,
            length=ARC_BBOX_X2 - ARC_BBOX_X1,
            style=SLIDER_STYLE
        )

        self.scale_label = tk.Label(
            self.parent,
            text=TEXT_DIFFICULTY_LEVEL,
            fg=COLOR_DISPLAY_TEXT,
            bg=COLOR_BG_DEFAULT,
            font=(FONT_FAMILY_DEFAULT, 10, BOLD)
        )

        self._create_scale_labels()

        # Layout the widgets with clear padding and sticky options
        self.canvas.grid(row=1, column=0, padx=10, sticky=tk.N)
        self.scale_label.grid(row=2, column=0, sticky=tk.S)
        self.my_scale.grid(row=3, column=0, pady=10, sticky=tk.N)


    # ───────────────────────────────────────────────
    # 2. Drawing and labeling
    # ───────────────────────────────────────────────

    def _draw_arc(self, level_text: str, color: str) -> None:
        """
        Draw an arc segment representing a difficulty level.

        Args:
            level_text (str): Text label for the arc.
            color (str): Color for the arc outline.

        Notes:
            The arc is drawn counterclockwise starting at start_angle.
            Coordinates for the text label are calculated using trigonometry:
            - The center of the arc is at (canvas_width/2, canvas_width/2).
            - The text position is offset along the radius at mid-angle.
            - The Y-axis is inverted in Tkinter, so sine values are used directly for Y.
        """
        start_angle = self._arc_start_angle
        mid_angle_deg = -(start_angle + ARC_EXTENT_ANGLE / 2)
        center_x = CANVAS_WIDTH // 2
        center_y = CANVAS_WIDTH // 2
        text_x = center_x + POINTER_LENGTH * math.cos(math.radians(mid_angle_deg))
        text_y = center_y + POINTER_LENGTH * math.sin(math.radians(mid_angle_deg))

        arc_id = self.canvas.create_arc(
            ARC_BBOX_X1, ARC_BBOX_Y1, ARC_BBOX_X2, ARC_BBOX_Y2,
            outline=color,
            width=ARC_THICKNESS,
            start=start_angle,
            extent=ARC_EXTENT_ANGLE,
            style=tk.ARC
        )
        self.id_canvas.append((arc_id, 'outline', color))

        self.canvas.create_text(
            text_x, text_y,
            text=level_text,
            font=(FONT_FAMILY_DEFAULT, 8, BOLD),
            fill=COLOR_BG_DEFAULT
        )

        self._arc_start_angle += ARC_EXTENT_ANGLE


    def _draw_pointer(self, angle_rad: float, color: str) -> None:
        """
        Draw the pointer arrow on the canvas pointing to the given angle.

        Args:
            angle_rad (float): Angle in radians for pointer direction.
            color (str): Color for the pointer arrow.
        """
        self.canvas.delete(self.pointer)
        center_x = center_y = CANVAS_WIDTH // 2
        end_x = center_x + POINTER_LENGTH * math.cos(angle_rad)
        end_y = center_y - POINTER_LENGTH * math.sin(angle_rad)

        self.pointer = self.canvas.create_line(
            center_x, center_y, end_x, end_y,
            width=6, arrow=tk.LAST, fill=color
        )


    def _create_scale_labels(self) -> None:
        """Create labels that show the difficulty description and emoji icon."""
        self.labels_frame = tk.Frame(self.parent, bg=GRAY)

        label_config = {
            "bg": GRAY,
            "fg": COLOR_BG_DEFAULT,
            "justify": tk.CENTER,
            "font": (FONT_FAMILY_DEFAULT, 12, BOLD),
            "width": 19,
            "height": 4,
            "text": TEXT_MOVE_SCALE 
        }

        icon_config = {
            "bg": GRAY,
            "fg": COLOR_BG_DEFAULT,
            "justify": tk.CENTER,
            "font": (FONT_FAMILY_DEFAULT, 42, BOLD),
            "width": 2,
            "text": "👈"
        }

        self.level_label = tk.Label(self.labels_frame, **label_config)
        self.level_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NS)

        self.icon_label = tk.Label(self.labels_frame, **icon_config)
        self.icon_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.NS)

        self.labels_frame.grid(row=1, column=1, rowspan=3, padx=20, pady=20, sticky=tk.NS)


    # ───────────────────────────────────────────────
    # 3. Dashboard interactivity
    # ───────────────────────────────────────────────

    def update_dashboard(self, *args) -> None:
        """
        Update pointer position and labels according to slider value.

        Args:
            *args: Ignored (tkinter scale passes the current value as argument).
        """
        slider_value = self.my_scale.get()
        angle_rad = math.radians(slider_value)

        # Redraw pointer at the new angle
        self._draw_pointer(angle_rad, BLUE)

        # Update labels according to slider position
        self._update_scale_labels(slider_value)


    def _update_scale_labels(self, slider_value: float = 0.0) -> None:
        """
        Update the difficulty label and icon based on the slider's position.

        Args:
            slider_value (float): Current slider value (0-180).
        """
        level = self._get_difficulty_by_value(slider_value)

        if level is not None:
            self._level = level.mode
            self.level_label.config(text=level.text, bg=level.bg, fg=BLACK)
            self.icon_label.config(text=level.icon, bg=level.bg, fg=BLACK)
            self.labels_frame.config(bg=level.bg)


    def _get_difficulty_by_value(self, value: float) -> Optional[Difficulty]:
        """
        Map slider value to difficulty level.

        Args:
            value (float): Slider value between 0 and 180.

        Returns:
            Difficulty: Matching difficulty enum or None if invalid.
        """
        value_int = int(round(value))
        for difficulty, (min_v, max_v) in _DIFFICULTY_RANGES.items():
            if min_v <= value_int <= max_v:
                return difficulty
        return None

    # ───────────────────────────────────────────────
    # 4. Canvas + frame state control
    # ───────────────────────────────────────────────

    def _toggle_canvas(self, state: str, disable_visuals: bool = False) -> None:
        """
        Enable or disable canvas and related widgets, optionally greying out visuals.

        Args:
            state (str): Tkinter widget state ('normal', 'disabled', etc).
            disable_visuals (bool): If True, grey out arcs and pointer visually.
        """
        self._toggle_children_widgets(self.parent, state=state)
        self._update_canvas_colors(disable=disable_visuals)


    def _toggle_children_widgets(self, widget: tk.Widget, state: Optional[str] = None) -> None:
        """
        Recursively set state on all child widgets.

        Args:
            widget (tk.Widget): Parent widget container.
            state (Optional[str]): Desired Tkinter state ('normal', 'disabled') or None.
        """
        for child in widget.winfo_children():
            if child.winfo_children():
                self._toggle_children_widgets(child, state)
            else:
                self.controller._set_widget_state(child, state)


    def _update_canvas_colors(self, disable: bool = False) -> None:
        """
        Update canvas arcs and pointer colors depending on enabled/disabled state.

        Args:
            disable (bool): If True, use grey colors for disabled state.
        """
        for item_id, prop, original_color in self.id_canvas:
            color = GRAY if disable else original_color
            if prop == 'outline':
                self.canvas.itemconfig(item_id, outline=color)
            elif prop == 'fill':
                self.canvas.itemconfig(item_id, fill=color)

        pointer_color = GRAY if disable else BLUE
        self._draw_pointer(0, pointer_color)

        self._update_scale_labels()

    
    def reset(self) -> None:
        """
        Reset the panel to default state (EMPTY).

        Enabling and disabling the slider forces the widget to refresh/redraw properly,
        ensuring the UI reflects the reset state immediately.
        """
        self.my_scale.state(['!disabled'])
        self.my_scale.set(0)
        self.my_scale.update_idletasks()
        self.update_dashboard()
        self.my_scale.state(['disabled'])
        self._toggle_canvas(tk.DISABLED, disable_visuals=True)


    def set_difficulty(self, difficulty: Difficulty) -> None:
        """
        Set the difficulty level programmatically.

        Args:
            difficulty (Difficulty): Difficulty enum value to set.
        """
        if difficulty not in _DIFFICULTY_RANGES:
            # If invalid difficulty, reset to EMPTY
            difficulty = Difficulty.EMPTY

        min_val, max_val = _DIFFICULTY_RANGES[difficulty]
        mid_val = (min_val + max_val) / 2
        self.my_scale.state(['!disabled'])
        self.my_scale.set(mid_val)
        self.my_scale.update_idletasks()
        self.update_dashboard()
        self.my_scale.state(['disabled'] if difficulty == Difficulty.EMPTY else ['!disabled'])
        self._toggle_canvas(
            tk.DISABLED if difficulty == Difficulty.EMPTY else tk.NORMAL,
            disable_visuals=(difficulty == Difficulty.EMPTY)
        )
        

    # ───────────────────────────────────────────────
    # 5. Properties
    # ───────────────────────────────────────────────

    @property
    def level(self) -> Difficulty:
        """
        Returns the selected Difficulty enum based on the scale value.
        Defaults to Difficulty.EASY if no match is found.
        """
        value = int(self.my_scale.get())
        for diff, (low, high) in _DIFFICULTY_RANGES.items():
            if low <= value <= high:
                return diff
        return Difficulty.EASY

