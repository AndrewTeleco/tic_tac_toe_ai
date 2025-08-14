#!/usr/bin/env python3

"""
TicTacToe Helper Classes - Support Classes for Game Entities and Logic

This module defines auxiliary classes used throughout the Tic Tac Toe project,
including data containers and helper structures that facilitate clean code,
type safety, and modular design.

Main contents:
- Data classes for representing players, moves, and other entities 👤
- Custom exceptions ⚠️
- AI and UI configuration utilities 🛠️

Designed for clarity, reusability, and compatibility across platforms.

Author: Andrés David Aguilar Aguilar  
Date: 2025-07-16
"""

from dataclasses import dataclass
from typing import Optional, NamedTuple, Any

from tic_tac_toe.core.literals import *

from tic_tac_toe.core.enums import Difficulty, LabelType


@dataclass(frozen=True)
class Player:
    """
    Represents a player with an animal symbol and color scheme.
    """
    animal: tuple[str, str]
    color: tuple[str, str]


@dataclass(frozen=True)
class Move:
    """
    Represents a move on the board with row, column, animal, and color.
    """
    row: int
    col: int
    animal: str = EMPTY
    color: str = EMPTY


class OpponentCredentials(NamedTuple):
    """
    Stores configuration data for an opponent player, used for rendering
    and logic identification in the game.
    """
    name: str
    symbol: str
    symbol_name: str
    color_name: str
    ans_clr: str


# ───────────────────────────────────────────────
# Custom Exceptions ⚠️
# ───────────────────────────────────────────────

class InvalidMoveError(ValueError):
    """Custom exception for invalid moves in the game."""
    pass


# ───────────────────────────────────────────────
# AI and UI Configuration Utilities 🛠️
# ───────────────────────────────────────────────

@dataclass
class AIConfig:
    """AI configuration for each difficulty level."""

    SETTINGS = {
        Difficulty.EASY: {
            "depth": None,
            "boost_level": None,
            "error": None,
            "time_limit": None
        },          
        Difficulty.MEDIUM: {
            "depth": 3,
            "boost_level": None,
            "error": 0.2,
            "time_limit": None
        },       
        Difficulty.HARD: {
            "depth": 4,
            "boost_level": None,
            "error": None,
            "time_limit": None
        },
        Difficulty.VERY_HARD: {
            "depth": None,
            "boost_level": Difficulty.VERY_HARD,
            "error": None, 
            "time_limit": 2.5
        }
    }

    @classmethod
    def get(cls, level: Difficulty, key: str) -> Any:
        """
        Retrieve the AI configuration value for a given difficulty level and key.
        """
        if level not in cls.SETTINGS:
            raise KeyError(f"Difficulty level '{level}' not found in AIConfig settings.")
        if key not in cls.SETTINGS[level]:
            raise KeyError(f"Key '{key}' not found for difficulty level '{level}'.")
        return cls.SETTINGS[level][key]


@dataclass
class InnerScoreConfig:
    """
    Visual and logical configuration for internal score display
    with styling and positioning options.
    """
    user: str
    clr: str
    font_1: int = 10
    font_2: int = 40
    row_1: int = 0
    row_2: int = 1
    col_1: int = 0
    col_2: int = 0
    index: int = 0
    padx: int = 5
    pady: int = 0
    anml: Optional[str] = None
    label: Optional[LabelType] = None
    sticky: str = 'ns'
    machine: Optional[str] = None
