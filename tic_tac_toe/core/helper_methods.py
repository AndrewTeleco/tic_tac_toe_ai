#!/usr/bin/env python3

"""
TicTacToe Helper Methods - Utility Functions for Game Logic and AI Scoring

This module provides reusable utility functions that support various parts of the
Tic Tac Toe project, including positional evaluation, board transformations,
symmetry detection, and scoring heuristics for AI levels.

- Generic Utilities (Normalization, Keys, Labels)
- Board Serialization and Conversion
- AI Scoring and Heuristics
- Positional and Symmetry Bonuses

These functions aim to promote code reuse, modularity, and clarity throughout the project.

Compatible with: Windows, macOS, Linux (UTF-8, ANSI colors supported)

Author: Andrés David Aguilar Aguilar  
Date: 2025-07-16
"""

import re
from typing import List, Optional, Tuple, Sequence

from tic_tac_toe.core.enums import WidgetKey, LabelType
from tic_tac_toe.core.literals import *

ANSI_PATTERN = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


# ───────────────────────────────────────────────
# Positional Evaluation Helpers 📍
# ───────────────────────────────────────────────

def positional_score_extended(row: int, col: int, size: int) -> float:
    """
    Returns a positional bonus based on key board areas:
    center, corners, diagonals, symmetry axes, and edges.

    Args:
        row (int): Row index.
        col (int): Column index.
        size (int): Board size.

    Returns:
        float: Total bonus score based on position.
    """
    center = size // 2
    score = 0.0

    # Determine center positions based on even/odd board size
    center_cells = (
        {(center, center)} if size % 2 == 1 else
        {(center - 1, center - 1), (center - 1, center),
         (center, center - 1), (center, center)}
    )

    # Positional bonus rules
    bonuses = [
        (0.15, (row, col) in center_cells),  # Center bonus
        (0.08, (row, col) in {(0, 0), (0, size - 1), (size - 1, 0), (size - 1, size - 1)}),  # Corners
        (0.05, row == col or row + col == size - 1),  # Diagonals
        (0.04, row == center or col == center),  # Center row/col
        (0.02, row in (0, size - 1) or col in (0, size - 1))  # Edges
    ]

    for bonus, condition in bonuses:
        if condition:
            score += bonus

    return round(score, 4)


def symmetry_score(positions: Sequence[Tuple[int, int]], size: int) -> float:
    """
    Computes bonus based on symmetry: diagonal alignment and center involvement.

    Args:
        positions (Sequence[Tuple[int, int]]): Coordinates in a potential combo.
        size (int): Board size.

    Returns:
        float: Bonus score for symmetry patterns.
    """
    if not positions:
        return 0.0

    center = size // 2
    center_coords = (
        {(center, center)} if size % 2 == 1 else
        {(center - 1, center - 1), (center - 1, center),
         (center, center - 1), (center, center)}
    )

    # Bonus conditions for symmetry
    conditions = [
        (1.5, all(r == c for r, c in positions)),              # Main diagonal
        (1.5, all(r + c == size - 1 for r, c in positions)),   # Anti-diagonal
        (1.0, any(pos in center_coords for pos in positions)), # Center involvement
        (0.5, any(r == center for r, _ in positions)),         # Center row
        (0.5, any(c == center for _, c in positions))          # Center column
    ]

    return sum(bonus for bonus, condition in conditions if condition)


# ───────────────────────────────────────────────
# Generic Utility Functions 🧩
# ───────────────────────────────────────────────

def get_zfill_pad(label: LabelType) -> int:
    """
    Return the zero-padding width for a given label type.

    This is used to format numeric fields (like scores or wins) with leading zeros
    in the ranking display or UI elements.

    Args:
        label (LabelType): The label type ('score', 'wins', etc.).

    Returns:
        int: Number of digits to pad with zeros (e.g., 3 → '007', 2 → '05').
             Defaults to 0 for unsupported or non-numeric label types.
    """
    match label:
        case LabelType.SCORE:
            return 3
        case LabelType.WINS:
            return 2
        case _:
            return 0
        

def make_key(label: str, normalized_username: str, extra_label: Optional[str] = None) -> WidgetKey:
    """
    Create a unique key tuple for dictionary lookups to avoid string concatenation.

    Args:
        label (str): Label type string (e.g., 'score', 'wins').
        normalized_username (str): Normalized username string.
        extra_label (Optional[str]): Optional extra label for further key distinction.

    Returns:
        WidgetKey: NamedTuple key for dict storage.
    """
    return WidgetKey(label.lower(), normalized_username.lower(), extra_label.lower() if extra_label else None)


def normalize_user(user: str) -> str:
    """
    Normalize a username by removing newlines and replacing spaces with underscores.

    Args:
        user (str): The username string to normalize.

    Returns:
        str: The normalized username.
    """
    return user.replace('\n', UNDERSCORE).replace(SPACE, UNDERSCORE)


def parse_entry_bg(item):
    dark_clrs = "^(Black|(Gray+([1-9]|[1-3][0-9]|[4][0-5])))$"
    if (re.findall(dark_clrs, item)): 
        # e.g:  Black, Gray1, Gray2, ..., Gray10, 
        #       Gray11,  ..., Gray30,..., Gray45                                 
        return WHITE
    return BLACK


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from a string."""
    return ANSI_PATTERN.sub('', text)


def get_color_escape(r=None, g=None, b=None, empty=True) -> str:
    """
    Convert RGB format into ANSI colour format.

    Args:
        r (int | None): Red component (0-255).
        g (int | None): Green component (0-255).
        b (int | None): Blue component (0-255).
        empty (bool): If True, returns an empty string regardless of RGB.

    Returns:
        str: ANSI escape code for the color, or EMPTY if not applicable.
    """
    if empty:
        return EMPTY

    # If r is actually a tuple/list (unpacking mistake)
    if isinstance(r, (tuple, list)) and len(r) == 3:
        r, g, b = r

    # Validate values
    if not all(isinstance(x, int) and 0 <= x <= 255 for x in (r, g, b)):
        return EMPTY

    return f"\033[38;2;{r};{g};{b}m"


# ───────────────────────────────────────────────
# Board Serialization and Conversion ♻️
# ───────────────────────────────────────────────

def board_to_str(mapping: Sequence[Sequence[str]]) -> str:
    """
    Flattens a 2D board into a single string.

    Note:
        Uses UNDERSCORE for empty cells.

    Args:
        mapping (Sequence[Sequence[str]]): The board to serialize.

    Returns:
        str: Flattened string version of the board.
    """
    return "".join(cell if cell else UNDERSCORE for row in mapping for cell in row)


def str_to_board(board_str: str, size: int) -> List[List[str]]:
    """
    Converts a flat string back to a 2D board.

    Args:
        board_str (str): Serialized board string.
        size (int): Size of one board dimension.

    Returns:
        List[List[str]]: 2D board.

    Raises:
        ValueError: If string length does not match expected board size.
    """
    expected = size ** 2
    if len(board_str) != expected:
        raise ValueError(f"Expected board string of length {expected}, got {len(board_str)}")
    return [list(board_str[i:i + size]) for i in range(0, expected, size)]


# ───────────────────────────────────────────────
# AI Scoring and Heuristics Utils 🎯
# ───────────────────────────────────────────────

def calculate_boost_score(
    combo: Sequence[str],
    positions: Sequence[Tuple[int, int]],
    size_board: int,
    board: Sequence[Sequence[str]]
) -> float:
    """
    Applies heuristic scoring to a combo line based on symbol count,
    positional context, and symmetry.

    Args:
        combo (Sequence[str]): Values in the current line (row/col/diagonal).
        positions (Sequence[Tuple[int, int]]): Positions of the line's cells.
        size_board (int): Board size.
        board (Sequence[Sequence[str]]): Game board representation.

    Returns:
        float: Final score with positional + symmetry + threat/strategy weight.
    """
    ai = combo.count(AI_MARK)
    player = combo.count(PLAYER_MARK)
    empty = combo.count(UNDERSCORE)

    # Lines with both player and AI are neutral (no value)
    if ai and player:
        return 0.0

    # Positional bonus (based on available empty cells)
    positional_bonus = sum(
        positional_score_extended(r, c, size_board)
        for r, c in positions
        if board[r][c] == UNDERSCORE
    )

    # Heuristic scoring rules
    rules = [
        (ai == size_board - 1 and empty == 1, 100.0),   # AI can win
        (player == size_board - 1 and empty == 1, 90.0),# Must block opponent
        (ai == size_board - 2 and empty == 2, 15.0),
        (player == size_board - 2 and empty == 2, 14.0),
        (ai == size_board - 3 and empty == 3, 6.0),
        (player == size_board - 3 and empty == 3, 5.0),
        (ai == 1 and empty == size_board - 1, 3.0),
        (player == 1 and empty == size_board - 1, 2.0),
        (empty == size_board, 1.0),                    # Fully empty line
        (ai == size_board - 2 and player == 0 and empty == 2, 5.0), # Threat pattern
        (player > ai and empty > 0, -2.0),              # Penalize losing lines
    ]

    base_score = sum(value for condition, value in rules if condition)
    sym_bonus = symmetry_score(positions, size_board)

    return round(base_score + positional_bonus + sym_bonus, 4)


def is_winning_combo(combo: Sequence[str]) -> bool:
    """
    Returns True if all elements in the combo are equal and not empty.

    Args:
        combo (Sequence[str]): Line of symbols (e.g., ['X', 'X', 'X']).

    Returns:
        bool: True if all equal and not empty.
    """
    return len(set(combo)) == 1 and combo[0] != UNDERSCORE


def score_combo(
    combo: Sequence[str],
    positions: Sequence[Tuple[int, int]],
    boost: bool,
    size_board: int,
    board: Sequence[Sequence[str]]
) -> int:
    """
    Scores a line: win, or strategic score if boost is enabled.

    Args:
        combo (Sequence[str]): Symbols in the line.
        positions (Sequence[Tuple[int, int]]): Cell coordinates.
        boost (bool): Whether to apply strategy-based scoring.
        size_board (int): Board size (e.g., 3 or 4).
        board (Sequence[Sequence[str]]): Current board state.

    Returns:
        int: Score from win or strategic evaluation.
    """
    if len(set(combo)) == 1 and combo[0] != UNDERSCORE:
        return 10 if combo[0] == AI_MARK else -10

    return int(calculate_boost_score(combo, positions, size_board, board)) if boost else 0


def win_score(combo: Sequence[str]) -> int:
    """
    Returns a fixed score depending on who wins.

    Args:
        combo (Sequence[str]): A winning combo (e.g., all 'X' or all 'O').

    Returns:
        int: +10 if AI wins, -10 if player wins.
    """
    return 10 if combo[0] == AI_MARK else -10


# ───────────────────────────────────────────────
# Widget Name Builder Utils 🏷️
# ───────────────────────────────────────────────

def build_name(base: str, prefix: Optional[str] = None, suffix: Optional[str] = None) -> str:
    """
    Build a widget name using WidgetKey as a helper.
    Example:
        build_name("1", prefix="ANIMAL", suffix="LABEL") -> "ANIMAL1LABEL"
    """
    return WidgetKey(prefix, base, suffix).build_name()


def build_widget_names(prefix: str, base: str, components: list[str]) -> dict[str, str]:
    """
    Build a dictionary of widget names using a common prefix and base.

    Args:
        prefix (str): Prefix for widget names (e.g., ANIMAL, COLOR).
        base (str): Base identifier (e.g., "1").
        components (list[str]): Suffixes to build (e.g., [LABEL, LIST, SELECT]).

    Returns:
        dict[str, str]: Mapping of component -> widget name.
    """
    base_name = build_name(base, prefix=prefix)
    return {
        'base': base_name,
        **{comp: build_name(base, prefix=prefix, suffix=comp) for comp in components}
    }


# ───────────────────────────────────────────────
# Widget Formatting Helpers 🐾
# ───────────────────────────────────────────────

def format_key(key: str, select: str, animals: dict[str, str]) -> str:
    """
    Format key for display. If the selection is an animal, 
    retrieve the mapped animal name.
    """
    if COLOR in select:
        return key
    return animals.get(key, key)


def get_animal_name(icon: str, animal_icons_to_names: dict[str, str]) -> str:
    """
    Retrieve the mapped name of an animal given its icon.
    """
    return animal_icons_to_names.get(icon, icon)

