# tests/test_gui.py

"""
Pytest-based unit tests for the TicTacToeGame GUI module.

This module uses pytest fixtures and unittest.mock to test GUI integration points
without invoking actual game logic or GUI rendering. Subcomponents such as BoardGame,
ButtonsPanel, and DisplayGame are mocked.

Author: Andrés David Aguilar Aguilar
Date: 2025-08-20
"""

import pytest
from unittest.mock import MagicMock, patch
from tic_tac_toe.core.logic_game import TicTacToeLogic
from tic_tac_toe.gui.tic_tac_toe_game import TicTacToeGame
from tic_tac_toe.core.helper_classes import Player, Move
from tic_tac_toe.core.literals import BOARD, BUTTONS_PANEL, CHECKBUTTON, DISPLAY, TIED, WINNER


# -------------------- Fixtures --------------------
        
@pytest.fixture
def mock_player():
    """Return a standard mock Player instance."""
    return lambda name="Player", animal="🐱", color="red": Player(
        animal=(animal, animal.lower(), None),
        color=(color, None, None)
    )


@pytest.fixture
def mock_moves():
    """Return a function that generates a board with mock moves."""
    return lambda size: [
        [Move(row=r, col=c,
              animal="🐱" if (r + c) % 2 == 0 else "🐶",
              color="red" if (r + c) % 2 == 0 else "blue")
         for c in range(size)]
        for r in range(size)
    ]


@pytest.fixture
def logic_mock(mock_player, mock_moves):
    """Return a MagicMock for TicTacToeLogic with default setup."""
    logic = MagicMock(spec=TicTacToeLogic)
    logic.size_board = 3
    logic.get_play_vs_machine.return_value = False
    logic.current_player = ("Player1", mock_player())
    logic.current_players = {
        "Player1": mock_player(),
        "Player2": mock_player("Player2", "🐶", "blue"),
        "MACHINE": mock_player("MACHINE", "🤖", "green")
    }
    logic.toggle_type_of_game = MagicMock()
    logic.toggle_player = MagicMock()
    logic.reset_flags = MagicMock()
    logic._init_game = MagicMock()
    logic._calculate_winning_combos = MagicMock()
    logic._ai_player = MagicMock()
    logic._vs_machine = False
    logic.file_logs_name = 'tic_tac_toe_logs.txt'
    logic._current_moves = mock_moves(logic.size_board)
    return logic


@pytest.fixture
def game(logic_mock):
    """Create a TicTacToeGame instance with mocked subcomponents."""
    with patch("tic_tac_toe.gui.tic_tac_toe_game.BoardGame", return_value=MagicMock()) as board_patch, \
         patch("tic_tac_toe.gui.tic_tac_toe_game.ButtonsPanel", return_value=MagicMock()) as buttons_patch, \
         patch("tic_tac_toe.gui.tic_tac_toe_game.DisplayGame", return_value=MagicMock()) as display_patch, \
         patch("tic_tac_toe.user_config.user_credentials_gui.UserCredentialsGUI._configure_window_form"):

        game_instance = TicTacToeGame(logic_mock)
        game_instance.logic = logic_mock
        game_instance.board_mock = board_patch.return_value
        game_instance.buttons_mock = buttons_patch.return_value
        game_instance.display_mock = display_patch.return_value
        game_instance.display_mock.current_color = "red"

        yield game_instance


@pytest.fixture
def game_vs_machine(logic_mock):
    """Return a TicTacToeGame instance with AI opponent enabled and mocks."""
    logic_mock.get_play_vs_machine.return_value = True
    with patch("tic_tac_toe.gui.tic_tac_toe_game.BoardGame", return_value=MagicMock()) as board_patch, \
         patch("tic_tac_toe.gui.tic_tac_toe_game.ButtonsPanel", return_value=MagicMock()) as buttons_patch, \
         patch("tic_tac_toe.gui.tic_tac_toe_game.DisplayGame", return_value=MagicMock()) as display_patch, \
         patch("tic_tac_toe.user_config.user_credentials_gui.UserCredentialsGUI._configure_window_form"):

        game_instance = TicTacToeGame(logic_mock)
        game_instance.logic = logic_mock
        game_instance.board_mock = board_patch.return_value
        game_instance.buttons_mock = buttons_patch.return_value
        game_instance.display_mock = display_patch.return_value

        # Mock difficulty panel inside buttons_mock
        game_instance.buttons_mock.difficulty_panel = MagicMock()
        game_instance.buttons_mock.difficulty_panel.level = "EASY"
        game_instance.buttons_mock.difficulty_panel.my_scale = MagicMock()
        game_instance.display_mock.current_color = "red"

        yield game_instance


# -------------------- Basic GUI Tests --------------------

def test_initial_attributes(game):
    """Verify TicTacToeGame initializes expected attributes."""
    assert game.size == 3
    assert not game.is_ai_opponent
    assert isinstance(game.widgets, dict)
    assert isinstance(game.frames, dict)


def test_build_board_game_calls_subcomponents(game):
    """Ensure GUI subcomponents are instantiated and assigned to frames."""
    assert game.frames[BOARD]
    assert game.frames[DISPLAY]
    assert game.frames[BUTTONS_PANEL]


def test_cells_property_returns_board_cells(game):
    """Verify cells property returns the board's cells dictionary."""
    game.frames[BOARD].cells = {'btn_mock': (0, 0)}
    assert game.cells == {'btn_mock': (0, 0)}


def test_change_board_size_rebuilds_board(game, mock_moves):
    """Changing board size updates logic and rebuilds the GUI."""
    new_size = 4
    game.logic.size_board = new_size
    game.logic._current_moves = mock_moves(new_size)
    game.frames[BOARD] = MagicMock()
    game.change_board_size(new_size)
    assert game.size == new_size
    game.frames[BOARD].grid.assert_called()


def test_switch_type_of_game_calls_reset_and_updates_display(game):
    """Switching game type resets flags and updates display label."""
    game._get_buttons_panel = MagicMock()
    game._get_display = MagicMock()
    game.logic.current_players = {
        "Player1": Player(animal=("🐱","cat",None), color=("red", None, None)),
        "MACHINE": Player(animal=("🤖","robot",None), color=("green", None, None))
    }
    game.switch_type_of_game()
    game._get_display().update_label.assert_called()


# -------------------- Advanced GUI Tests --------------------

# ---------- start_game ----------

def test_start_game_binds_buttons(game_vs_machine):
    """Verify start_game binds board buttons."""
    game_vs_machine._bind_board_buttons = MagicMock()
    game_vs_machine._highlight_board_frames = MagicMock()
    game_vs_machine._toggle_start_reset_btns = MagicMock()
    game_vs_machine._log = MagicMock()
    game_vs_machine._get_display = MagicMock(return_value=game_vs_machine.display_mock)

    game_vs_machine.start_game()
    game_vs_machine._bind_board_buttons.assert_called()


def test_start_game_highlights_frames(game_vs_machine):
    """Verify start_game highlights board frames."""
    game_vs_machine._bind_board_buttons = MagicMock()
    game_vs_machine._highlight_board_frames = MagicMock()
    game_vs_machine._toggle_start_reset_btns = MagicMock()
    game_vs_machine._log = MagicMock()
    game_vs_machine._get_display = MagicMock(return_value=game_vs_machine.display_mock)

    game_vs_machine.start_game()
    game_vs_machine._highlight_board_frames.assert_called()


def test_start_game_toggles_buttons(game_vs_machine):
    """Verify start_game toggles start/reset buttons."""
    game_vs_machine._bind_board_buttons = MagicMock()
    game_vs_machine._highlight_board_frames = MagicMock()
    game_vs_machine._toggle_start_reset_btns = MagicMock()
    game_vs_machine._log = MagicMock()
    game_vs_machine._get_display = MagicMock(return_value=game_vs_machine.display_mock)

    game_vs_machine.start_game()
    game_vs_machine._toggle_start_reset_btns.assert_called_with("RESET", "START")


def test_start_game_process_logs(game_vs_machine):
    """Verify start_game logs the 'START' state."""
    game_vs_machine._bind_board_buttons = MagicMock()
    game_vs_machine._highlight_board_frames = MagicMock()
    game_vs_machine._toggle_start_reset_btns = MagicMock()
    game_vs_machine._log = MagicMock()
    game_vs_machine._get_display = MagicMock(return_value=game_vs_machine.display_mock)

    game_vs_machine.start_game()
    game_vs_machine._log.process_logs.assert_called_with(state="START")


# ---------- reset_game ----------

def test_reset_game_resets_logic_and_ui(game_vs_machine):
    """Verify reset_game resets logic and UI components."""
    game_vs_machine._reset_logic_and_state = MagicMock()
    game_vs_machine._reset_ui = MagicMock()
    game_vs_machine._reset_bindings = MagicMock()
    game_vs_machine._reset_difficulty_scale = MagicMock()
    game_vs_machine._log = MagicMock()
    game_vs_machine._toggle_start_reset_btns = MagicMock()

    game_vs_machine.reset_game(only_size=False)
    game_vs_machine._reset_logic_and_state.assert_called()
    game_vs_machine._reset_ui.assert_called()


def test_reset_game_resets_bindings_and_difficulty(game_vs_machine):
    """Verify reset_game resets bindings and difficulty scale."""
    game_vs_machine._reset_bindings = MagicMock()
    game_vs_machine._reset_difficulty_scale = MagicMock()
    game_vs_machine._log = MagicMock()
    game_vs_machine._toggle_start_reset_btns = MagicMock()

    game_vs_machine.reset_game(only_size=False)
    game_vs_machine._reset_bindings.assert_called()
    game_vs_machine._reset_difficulty_scale.assert_called()


def test_reset_game_updates_logs(game_vs_machine):
    """Verify reset_game updates log information."""
    game_vs_machine._reset_logic_and_state = MagicMock()
    game_vs_machine._reset_ui = MagicMock()
    game_vs_machine._reset_bindings = MagicMock()
    game_vs_machine._reset_difficulty_scale = MagicMock()
    game_vs_machine._log = MagicMock()
    game_vs_machine._toggle_start_reset_btns = MagicMock()

    game_vs_machine.reset_game(only_size=False)
    game_vs_machine._log.update_cells.assert_called()
    game_vs_machine._log.update_size.assert_called()
    game_vs_machine._log.process_logs.assert_called_with(state="RESET")


def test_reset_game_toggles_buttons(game_vs_machine):
    """Verify reset_game toggles start/reset buttons."""
    game_vs_machine._reset_logic_and_state = MagicMock()
    game_vs_machine._reset_ui = MagicMock()
    game_vs_machine._reset_bindings = MagicMock()
    game_vs_machine._reset_difficulty_scale = MagicMock()
    game_vs_machine._log = MagicMock()
    game_vs_machine._toggle_start_reset_btns = MagicMock()

    game_vs_machine.reset_game(only_size=False)
    game_vs_machine._toggle_start_reset_btns.assert_called_with("START", "RESET")


# ---------- handle_winner and handle_tie ----------

def test_handle_winner_updates_logs(game_vs_machine):
    """Verify _handle_winner logs WINNER state."""
    game_vs_machine._get_display = MagicMock(return_value=game_vs_machine.display_mock)
    game_vs_machine._get_board = MagicMock()
    game_vs_machine._log = MagicMock()
    game_vs_machine.logic._winner_combo = [(0, 0), (0, 1), (0, 2)]

    game_vs_machine._handle_winner()
    game_vs_machine._log.process_logs.assert_called_with(state=WINNER)


def test_handle_tie_updates_logs_and_toggle_player(game_vs_machine):
    """Verify _handle_tie toggles player and logs TIED state."""
    game_vs_machine._get_display = MagicMock(return_value=game_vs_machine.display_mock)
    game_vs_machine._get_board = MagicMock()
    game_vs_machine._log = MagicMock()
    game_vs_machine.logic.toggle_player = MagicMock()

    game_vs_machine._handle_tie()
    game_vs_machine.logic.toggle_player.assert_called()
    game_vs_machine._log.process_logs.assert_called_with(state=TIED)


# ---------- play_machine ----------

def test_play_machine_calls_ai_controller(game_vs_machine):
    """Verify play_machine calls AI controller once when AI is enabled."""
    game_vs_machine._get_display = MagicMock()
    game_vs_machine._get_board = MagicMock()
    game_vs_machine.check_play_machine = MagicMock(return_value=True)
    mock_button = MagicMock()
    game_vs_machine._ai_controller = MagicMock(return_value=((0, 0), mock_button))
    game_vs_machine._restart_binds = MagicMock()
    game_vs_machine.is_ai_opponent = True
    game_vs_machine.logic._vs_machine = True

    game_vs_machine.play_machine(start=True)
    game_vs_machine._ai_controller.assert_called_once()


# ---------- toggle_start_reset_btns ----------

def test_toggle_start_reset_btns_widget_states(game_vs_machine):
    """Verify _toggle_start_reset_btns sets widget states correctly."""
    game_vs_machine._get_widget = MagicMock()
    game_vs_machine._get_difficulty_slider = MagicMock()
    game_vs_machine.game_mode_checkbutton.set(1)
    game_vs_machine._toggle_widget_state = MagicMock()
    game_vs_machine._set_scale_state = MagicMock()

    game_vs_machine._toggle_start_reset_btns("START", "RESET")
    expected_calls = [
        ("START", "normal"),
        ("RESET", "disabled"),
        ("3x3", "normal"),
        ("4x4", "normal"),
        (CHECKBUTTON, "normal")
    ]
    for name, state in expected_calls:
        game_vs_machine._toggle_widget_state.assert_any_call(name, state)


def test_toggle_start_reset_btns_scale_state(game_vs_machine):
    """Verify _toggle_start_reset_btns sets difficulty scale state correctly."""
    game_vs_machine._get_widget = MagicMock()
    game_vs_machine._get_difficulty_slider = MagicMock()
    game_vs_machine.game_mode_checkbutton.set(1)
    game_vs_machine._toggle_widget_state = MagicMock()
    game_vs_machine._set_scale_state = MagicMock()

    game_vs_machine._toggle_start_reset_btns("START", "RESET")
    game_vs_machine._set_scale_state.assert_called_with("normal")
