#!/usr/bin/env python3

"""
USER CREDENTIALS VALIDATOR MODULE

Validates user credentials for the TicTacToe game, including:
- Username constraints
- Animal selection
- Color selection
- Avoiding duplicates among players

Structure:
1. Username Validation
2. Animal & Color Validation
3. Combined Validation

Author: Andrés David Aguilar Aguilar
Date: 2025-07-24
"""

from typing import Dict, Tuple

from tic_tac_toe.core.literals import *


# ───────────────────────────────────────────────
# 1. Username Validation
# ───────────────────────────────────────────────

def validate_username(username: str, length: int = 18) -> bool:
    """
    Validate username length and characters, allowing empty string during editing.
    """
    return (
        len(username) <= length
        and all(ch.isalnum() or ch.isspace() for ch in username)
    )


def validate_unique_usernames(username1: str, username2: str) -> bool:
    """Ensure both usernames are filled and unique."""
    return (
        bool(username1) 
        and bool(username2) 
        and username1 != username2
    )


# ───────────────────────────────────────────────
# 2. Animal & Color Validation
# ───────────────────────────────────────────────

def validate_animal(animal_name: str, animals: Dict[str, str]) -> bool:
    """Check if the animal_name exists in the allowed animals."""
    return animal_name in animals


def validate_color(color_name: str, colors: Dict[str, Tuple[int, int, int]]) -> bool:
    """Check if the color_name exists in the allowed colors."""
    return color_name in colors


def validate_no_duplicate_animals_colors(
        animal1: str, 
        animal2: str, 
        color1: str, 
        color2: str
    ) -> bool:
    """Ensure that players don't have identical animal and color combinations."""
    unique_items = len(set([animal1, animal2, color1, color2]))
    return unique_items > 2


# ───────────────────────────────────────────────
# 3. Combined Validation
# ───────────────────────────────────────────────

def validate_all(
    username1: str, username2: str,
    animal1: str, animal2: str,
    color1: str, color2: str,
    animals: Dict[str, str],
    colors: Dict[str, Tuple[int, int, int]]
) -> Tuple[bool, str]:
    """Run all validations and return (valid, message)."""
    
    if not validate_unique_usernames(username1, username2):
        return False, "Both usernames must be filled and unique."

    if not validate_username(username1):
        return False, f"Username '{username1}' is invalid."

    if not validate_username(username2):
        return False, f"Username '{username2}' is invalid."

    if not (validate_animal(animal1, animals) and validate_animal(animal2, animals)):
        return False, "Both animals must be selected from the list."

    if not (validate_color(color1, colors) and validate_color(color2, colors)):
        return False, "Both colors must be selected from the list."

    if not validate_no_duplicate_animals_colors(animal1, animal2, color1, color2):
        return False, "Both animal and color fields cannot be identical or too similar."

    return True, ('Credentials have been filled successfully.' + 
                  '\nClick on the button to start the game.')