#!/usr/bin/env python3

"""
TicTacToe Enumerations and UI Constants - Enums for Game States, UI Elements and Controls

This module centralizes all enumeration classes used throughout the Tic Tac Toe project,
including difficulty levels, UI label types, action buttons, and widget key identifiers.

Designed to improve code clarity, modularity, and maintainability by grouping
all enum types and UI constant keys in one place.

Author: Andrés David Aguilar Aguilar  
Date: 2025-07-16
"""

from enum import Enum
from typing import NamedTuple, Optional

from tic_tac_toe.core.literals import *


class Difficulty(Enum):
    """
    Enum representing difficulty levels for the AI opponent.
    """
    EMPTY = (EMPTY, GRAY, TEXT_MOVE_SCALE, "👈")
    EASY = (EASY, COLOR_EASY_LEVEL, TEXT_EASY_LEVEL, "😄")
    MEDIUM = (MEDIUM, COLOR_MEDIUM_LEVEL, TEXT_MEDIUM_LEVEL, "🤔")
    HARD = (HARD, COLOR_HARD_LEVEL, TEXT_HARD_LEVEL, "😨")
    VERY_HARD = (VERY_HARD, COLOR_VERY_HARD_LEVEL, TEXT_VERY_HARD_LEVEL, "🤖")

    def __init__(self, mode: str, bg: str, text: str, icon: str):
        self._mode = mode
        self._bg = bg
        self._text = text
        self._icon = icon

    @property
    def mode(self) -> str: return self._mode

    @property
    def bg(self) -> str: return self._bg

    @property
    def text(self) -> str: return self._text

    @property
    def icon(self) -> str: return self._icon


class LabelType(str, Enum):
    """Enum for types of score labels used in the UI."""
    NAME = NAME
    WINS = WINS
    SCORE = SCORE


class ActionButtons(str, Enum):
    """Enum for action button labels."""
    START = TEXT_START_BUTTON
    RESET = TEXT_RESET_BUTTON
    EXIT = TEXT_EXIT_BUTTON


class WidgetKey(NamedTuple):
    """
    Unified key for widget naming and identification.

    Can be used for:
    - Game widgets (score, wins)
    - UserCredentials widgets (entries, labels, checkbuttons)
    """

    prefix: Optional[str] = None    # e.g., USERNAME, ANIMAL, COLOR
    base: str = ""                  # e.g., "1", "Alice", etc.
    suffix: Optional[str] = None    # e.g., LABEL, CHECKBUTTON, LIST

    def build_name(self) -> str:
        """
        Build the full widget name by concatenating non-empty parts.
        Example: WidgetKey("ANIMAL", "1", "LABEL") -> "ANIMAL1LABEL"
        """
        return ''.join(filter(None, (self.prefix, self.base, self.suffix)))





