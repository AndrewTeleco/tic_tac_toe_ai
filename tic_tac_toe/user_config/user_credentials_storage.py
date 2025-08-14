#!/usr/bin/env python3

"""
USER CREDENTIALS STORAGE MODULE - Handles the persistence and logging of player credentials.

This module is responsible for loading static resources (animals and colors), 
processing user selection logs, and storing user credentials and logs 
both in files and in a shelve-based local database.

Responsibilities:
- Load animal and color options from .md resource files.
- Generate formatted logs for animal/color selections and final credentials.
- Persist user data and log files for future reference using shelve.
- Provide internal utilities for formatting and packaging credentials.

Structure:
1. Persistence Interface (store_data)
2. Resource Loaders (load_animal_list, load_color_list)
3. Logging Methods (process_logs, _create_event, _create_final_event)
4. Internal Helpers (_loading_credentials)

Author: Andrés David Aguilar Aguilar
Date: 2025-07-23
"""

import logging
import shelve
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tkinter import Widget

from tic_tac_toe.core.helper_methods import get_color_escape
from tic_tac_toe.core.literals import *
from tic_tac_toe.core.paths import (
    DB_PATH,
    LOGS_FILE,
    ROOT_PATH_DATA, 
    ROOT_PATH_LOGS, 
    ROOT_PATH_USER_CONFIG
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ───────────────────────────────────────────────
# 1. Helper to ensure directories exist
# ───────────────────────────────────────────────

def ensure_directories() -> None:
    """
    Ensure all required directories exist (data, logs, user_config).
    """
    for path in (ROOT_PATH_DATA, ROOT_PATH_LOGS, ROOT_PATH_USER_CONFIG):
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create directory {path}: {e}")

ensure_directories()

# ───────────────────────────────────────────────
# 2. Persistent Storage Methods (Shelve, Files)
# ───────────────────────────────────────────────

def store_data(
    credentials: Dict[str, Dict[str, Any]], 
    logs: List[str],
    db_path: Path = DB_PATH,
    file_logs_name: Optional[str] = None
) -> Optional[Path]:
    """
    Persist user credentials and log entries to disk with error handling.

    Args:
        credentials: User credentials for both players.
        logs: List of formatted string entries representing game events.
        db_path: Path to the shelve database file.
        file_logs_name: Optional custom log filename (used for testing or predictability).

    Returns:
        Optional[Path]: Path to the log file if successful, None on failure.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_logs_name = Path(file_logs_name or f"{timestamp}_log_file.md")
    log_path = file_logs_name if file_logs_name.is_dir() else ROOT_PATH_LOGS / file_logs_name

    try:
        with log_path.open(mode='w', encoding='utf-8') as file:
            file.writelines(logs)
    except OSError as e:
        logger.error(f"Failed to write logs to {log_path}: {e}")
        return None

    try:
        with shelve.open(str(db_path), flag='c') as db:
            for key, value in credentials.items():
                db[key] = value
            db[LOGS_FILE] = str(log_path.resolve())
    except Exception as e:
        logger.error(f"Failed to store data in shelve {db_path}: {e}")
        return None

    logger.info(f"Credentials and logs saved correctly in {db_path}")
    return log_path

# ───────────────────────────────────────────────
# 3. Resource Loaders (Static Load from .md files)
# ───────────────────────────────────────────────

def load_animal_list() -> Dict[str, str]:
    """
    Load animal names and their associated emojis from the 'Animals.md' file.

    Each line in the file should have the format:
    <emoji> <decimal_code> <hex_code> <animal name>

    Returns:
        Dict[str, str]: Mapping of capitalized animal names to their emojis.
                        Example: {'Ox': '🐂', 'Dog': '🐕'}
    """
    animals = {}
    path = ROOT_PATH_USER_CONFIG / 'Animals.md'

    if not path.exists():
        logger.warning(f"Resource file {path} not found.")
        return animals

    try:
        with path.open(encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) < 4:
                    continue
                emoji = parts[0]
                name = ' '.join(parts[3:]).capitalize()
                animals[name] = emoji
    except OSError as e:
        logger.error(f"Failed to read animals from {path}: {e}")

    return animals


def load_color_list() -> Dict[str, Tuple[int, int, int]]:
    """
    Load colors from 'Colors.md' file.

    Each line has the format:
        color_name hex_code RGB(r,g,b)

    Example line:
        aliceblue #F0F8FF RGB(240,248,255)

    Returns:
        Dict[str, Tuple[int,int,int]]: Mapping of color names (capitalized) to RGB tuples.
        Example: {'Aliceblue': (240, 248, 255), 'Aqua': (0, 255, 255)}
    """
    colors = {}
    path = ROOT_PATH_USER_CONFIG / 'Colors.md'

    if not path.exists():
        logger.warning(f"Resource file {path} not found.")
        return colors

    try:
        with path.open(encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) < 3:
                    continue  

                name = parts[0].capitalize()
                rgb_str = parts[-1]

                if not (rgb_str.startswith("RGB(") and rgb_str.endswith(")")):
                    continue  

                rgb_nums = rgb_str[4:-1].split(',')
                if len(rgb_nums) != 3:
                    continue

                try:
                    r, g, b = map(int, rgb_nums)
                except ValueError:
                    continue  

                colors[name] = (r, g, b)
    except OSError as e:
        logger.error(f"Failed to read colors from {path}: {e}")

    return colors


# ───────────────────────────────────────────────
# 4. Logging Methods (Console & File Logs)
# ───────────────────────────────────────────────

def process_logs(
        user: int,
        animals: Dict[str, str],
        colors: Dict[str, Tuple[int, int, int]],
        string_vars: Dict[str, Any],
        lasts: Dict[str, str],
        logs: List[str],
        credentials: Dict[str, Dict[str, Any]] = None,
        animal: str = None,
        color: str = None
    ) -> None:
    """
    Dispatch method to log either user selection changes or final credentials.

    Depending on the value of `final_log`, this method delegates to:
    - _log_intermediate_event: for incremental selection updates.
    - _log_final_event: for final summary of both players' credentials.

    Args:
        user (int): Index of the player (0 or 1).
        animals (Dict[str, str]): Animal name to emoji mapping.
        colors (Dict[str, Tuple[int, int, int]]): Color name to RGB mapping.
        string_vars (Dict[str, Any]): Tkinter StringVars associated with the GUI form.
        lasts (Dict[str, str]): Tracks last known values to avoid duplicate logs.
        logs (List[str]): Accumulates formatted log strings for writing to file.
        credentials (Dict[str, Dict[str, Any]]): Dictionary containing usernames, 
            selected animals and colors for both players.
        animal (str, optional): Selected animal emoji (if applicable).
        color (str, optional): Selected color name (if applicable).
    """
    timestamp = f"\n|TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|"

    if credentials:
        log_final_event(logs, timestamp, credentials)
    else:
        log_intermediate_event(
            user, animals, colors, string_vars, lasts, logs, timestamp, animal, color
        )


def log_intermediate_event(
        user: int,
        animals: Dict[str, str],
        colors: Dict[str, Tuple[int, int, int]],
        string_vars: Dict[str, Any],
        lasts: Dict[str, str],
        logs: List[str],
        timestamp: str,
        animal: str,
        color: str
    ) -> None:
    """
    Logs a selection change event for a single user.

    Compares the current selections to the last known values and 
    logs only if there has been a change in animal or color.

    Args:
        user (int): Index of the player (0 or 1).
        animals (Dict[str, str]): Animal name to emoji mapping.
        colors (Dict[str, Tuple[int, int, int]]): Color name to RGB mapping.
        string_vars (Dict[str, Any]): GUI variables to fetch current selections.
        lasts (Dict[str, str]): Tracks last recorded values for each selection.
        logs (List[str]): The list where the formatted log will be appended.
        timestamp (str): Timestamp string prepended to each event.
        animal (str): Currently selected animal emoji.
        color (str): Currently selected color name.
    """
    
    event: List[str] = []

    username_var = string_vars.get(USERNAME + str(user))
    username = username_var.get() if username_var else f"Player {user}"

    anml_key = ANIMAL + str(user)
    clr_key = COLOR + str(user)

    name_anml = next((k for k, v in animals.items() if v == animal), EMPTY)
    rgb = colors.get(color.capitalize(), EMPTY) if color else EMPTY

    for flag in (True, False):
        event.append(create_event(
            anml=anml_key,
            animal=animal,
            clr=clr_key,
            color=color,
            name_anml=name_anml,
            rgb=rgb,
            username=username,
            lasts=lasts,
            empty=flag
        ))

    lasts[anml_key] = name_anml
    lasts[clr_key] = color

    if event and event[0]:
        logs.append(timestamp + event[0])
        print(timestamp + event[1] + RESET_COLOR)


def log_final_event(logs: List[str], timestamp: str, 
                    credentials: Dict[str, Dict[str, Any]]) -> None:
    """
    Logs the final credential summary for both players.

    This method appends a formatted Markdown and console log
    showing the full username, animal, and color for each player.

    Args:
        logs (List[str]): The list where the final summary log will be stored.
        timestamp (str): Timestamp string prepended to the event.
        credentials (Dict[str, Dict[str, Any]]): Dictionary containing usernames, 
            selected animals and colors for both players.
    """

    logs.append(timestamp + create_final_event(credentials))
    print(timestamp + create_final_event(credentials, empty=False) + RESET_COLOR)


def create_final_event(credentials: Dict[str, Dict[str, Any]], empty: bool = True) -> str:
    """
    Generate a color-formatted final log entry summarizing both players' credentials.

    Args:
        credentials (Dict[str, Dict[str, Any]]): Dictionary containing usernames, 
            selected animals and colors for both players.
        empty (bool): If True, colors are replaced with neutral/white for printing.

    Returns:
        str: A formatted log string representing final game setup for both players.
    """
    event = []

    for i, (_, data) in enumerate(credentials.items()):
        rgb = data[COLORS][1]
        color_escape = get_color_escape(*rgb, empty=empty)
        username = data[USERNAMES]
        animal_name = data[ANIMALS][0]
        animal_text = data[ANIMALS][1]
        color_name = data[COLORS][0]

        event.append(
            f"\n{color_escape}"
            f"{'-'*5} FINAL CREDENTIALS OF PLAYER {i+1} {'-'*5}\n\t"
            f"- USERNAME: {username}\n\t"
            f"- SELECTED ANIMAL: {animal_name} ({animal_text})\n\t"
            f"- SELECTED COLOR: {color_name}\n"
        )
    return f"\n|EVENT: Both players are ready for the game 🎳|\n{''.join(event)}"


def create_event(
        anml: str,
        animal: str,
        clr: str,
        color: str,
        name_anml: str,
        rgb: Tuple[int, int, int],
        username: str,
        lasts: Dict[str, str],
        empty: bool = True
    ) -> str:
    """
    Generate an event string for a user's selection changes.

    Args:
        anml (str): Key for animal selection in lasts.
        animal (str): Current animal.
        clr (str): Key for color selection in lasts.
        color (str): Current color.
        name_anml (str): Name of the selected animal.
        rgb (Tuple[int, int, int]): RGB color tuple.
        username (str): Username.
        lasts (Dict[str, str]): Previous values to compare changes.
        empty (bool): Whether to disable color escapes.

    Returns:
        str: Event log string or EMPTY if nothing changed.
    """
    user_changed = color != lasts.get(clr) or name_anml != lasts.get(anml)
    animal_changed = bool(animal and name_anml != lasts.get(anml))
    color_changed = bool(color and color != lasts.get(clr))

    user_txt = f"{get_color_escape(*rgb, empty=empty)} {username}" if user_changed else EMPTY
    anml_txt = f" has selected {animal} ({name_anml}) as their flagship animal" if animal_changed else EMPTY
    clr_txt = f" has selected {color} as their color." if color_changed else EMPTY

    event = user_txt + anml_txt + clr_txt
    return f"EVENT: {event}|" if event else EMPTY


# ───────────────────────────────────────────────
# 5. Internal Helpers
# ───────────────────────────────────────────────

def loading_credentials(
    animals: Dict[str, str],
    colors: Dict[str, Tuple[int, int, int]],
    widgets: Dict[str, 'Widget'],
    usr_1: str,
    usr_2: str,
    anml_1: str,
    anml_2: str,
    clr_1: str,
    clr_2: str
) -> Dict[str, Dict[str, Any]]:
    """
    Generate the credentials dictionary for both users based on their selections.

    Args:
        animals: Mapping of animal names to emojis.
        colors: Mapping of color names to RGB values.
        widgets: Widget dictionary holding selection backgrounds.
        usr_1, usr_2: Usernames of both players.
        anml_1, anml_2: Selected animal emojis.
        clr_1, clr_2: Selected color names.

    Returns:
        A dictionary with full credentials for each user.
    """

    def reverse_lookup(d: Dict[str, str], value: str) -> str:
        """Get the key of a given value in a dictionary."""
        return next((k for k, v in d.items() if v == value), EMPTY)

    def rgb(clr: str) -> Tuple[int, int, int]:
        """Get RGB tuple for a given color name."""
        return colors.get(clr.capitalize(), (0, 0, 0))

    # Backgrounds for selected animals
    anml_1_bg = widgets[FIRST_ANIMAL + SELECT].cget('bg')
    anml_2_bg = widgets[SECOND_ANIMAL + SELECT].cget('bg')

    # Build the credentials dictionary
    credentials = {
        FIRST_USER: {
            USERNAMES: usr_1,
            ANIMALS: (
                anml_1,
                reverse_lookup(animals, anml_1),
                anml_1_bg
            ),
            COLORS: (
                clr_1,
                rgb(clr_1),
                get_color_escape(*rgb(clr_1), empty=False)
            )
        },
        SECOND_USER: {
            USERNAMES: usr_2,
            ANIMALS: (
                anml_2,
                reverse_lookup(animals, anml_2),
                anml_2_bg
            ),
            COLORS: (
                clr_2,
                rgb(clr_2),
                get_color_escape(*rgb(clr_2), empty=False)
            )
        }
    }

    return credentials







    
