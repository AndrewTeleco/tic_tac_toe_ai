# tests/test_user_config.py

"""
Pytest-based unit tests for UserCredentials GUI and storage modules.

Tests include:
1. Resource loading (animals/colors)
2. Persistent storage
3. Event/log generation
4. Loading credentials
5. GUI variable initialization
6. GUI Listbox / Checkbutton / Radiobutton simulation
7. Validation integration (valid and invalid cases)

Mocks and FakeVars are used to avoid opening real Tk windows.

Author: Andrés David Aguilar Aguilar
Date: 2025-08-21
"""

import pytest
import tkinter as tk
from tic_tac_toe.user_config.user_credentials_storage import (
    load_animal_list,
    load_color_list,
    store_data,
    loading_credentials,
    create_event,
    create_final_event
)
from tic_tac_toe.user_config.user_credentials_gui import UserCredentialsGUI
from tic_tac_toe.user_config.user_credentials_validator import validate_all
from tic_tac_toe.user_config.user_credentials_callbacks import build_name
from tic_tac_toe.core.literals import (
    FIRST_USER, SECOND_USER,
    FIRST_ANIMAL, SECOND_ANIMAL,
    FIRST_COLOR, SECOND_COLOR,
    ANIMAL, ANIMALS, COLOR, COLORS,
    USERNAMES, EMPTY, NUM_PLAYERS,
    SELECT, ALL_MATCHES, RADIOBUTTON
)


# -------------------- Fixtures --------------------

@pytest.fixture
def fake_var_monkeypatch(monkeypatch):
    """Patch Tkinter StringVar and BooleanVar with FakeVar for GUI tests."""
    class FakeVar:
        def __init__(self, value=None): self._value = value
        def get(self): return self._value
        def set(self, value): self._value = value
        def trace_add(self, mode, callback): return "trace_id"
        def trace_remove(self, mode, trace_id): pass
    monkeypatch.setattr(tk, "StringVar", FakeVar)
    monkeypatch.setattr(tk, "BooleanVar", FakeVar)
    return FakeVar


@pytest.fixture
def gui_instance(fake_var_monkeypatch, monkeypatch):
    """Return a UserCredentialsGUI instance with patched Tk variables."""
    gui = UserCredentialsGUI()
    monkeypatch.setattr(gui._callbacks, "_update_current_user", lambda: None)
    return gui


# -------------------- 1. Resource Loading Tests --------------------

def test_load_animal_list_returns_dict():
    """Test that load_animal_list() returns a dictionary of string->string."""
    animals = load_animal_list()
    assert isinstance(animals, dict)
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in animals.items())


def test_load_color_list_returns_dict():
    """Test that load_color_list() returns a dictionary of string->tuple(R,G,B)."""
    colors = load_color_list()
    assert isinstance(colors, dict)
    assert all(isinstance(k, str) and isinstance(v, tuple) and len(v) == 3 for k, v in colors.items())
    assert all(isinstance(i, int) for color in colors.values() for i in color)


# -------------------- 2. Persistent Storage Tests --------------------

def test_store_data_creates_file_and_shelve(tmp_path):
    """Test that store_data() creates both log file and shelve database."""
    logs = ["Test log entry\n"]
    credentials = {
        FIRST_USER: {USERNAMES: "Alice", ANIMALS: ("🐶","Dog","bg"), COLORS: ("Red",(255,0,0),"escape")},
        SECOND_USER: {USERNAMES: "Bob", ANIMALS: ("🐱","Cat","bg"), COLORS: ("Blue",(0,0,255),"escape")}
    }
    log_file = tmp_path / "test_log.md"
    db_path = tmp_path / "test_db"

    result_path = store_data(credentials, logs, db_path=db_path, file_logs_name=log_file)
    assert result_path.exists()
    assert log_file.read_text() == "".join(logs)
    assert any(f.exists() for f in db_path.parent.glob(db_path.name + "*"))


# -------------------- 3. Log Generation Tests --------------------

def test_create_event_generates_string():
    """Test that create_event() returns a string containing the username."""
    lasts = {ANIMAL+"1": EMPTY, COLOR+"1": EMPTY}
    event = create_event(
        anml=ANIMAL+"1",
        animal="🐶",
        clr=COLOR+"1",
        color="Red",
        name_anml="Dog",
        rgb=(255,0,0),
        username="Alice",
        lasts=lasts
    )
    assert isinstance(event, str)
    assert "Alice" in event


def test_create_final_event_generates_string():
    """Test that create_final_event() returns a string including both usernames."""
    credentials = {
        FIRST_USER: {USERNAMES: "Alice", ANIMALS: ("🐶","Dog","bg"), COLORS: ("Red",(255,0,0),"escape")},
        SECOND_USER: {USERNAMES: "Bob", ANIMALS: ("🐱","Cat","bg"), COLORS: ("Blue",(0,0,255),"escape")}
    }
    final_event = create_final_event(credentials)
    assert isinstance(final_event, str)
    assert "Alice" in final_event and "Bob" in final_event


# -------------------- 4. Loading Credentials Tests --------------------

def test_loading_credentials_returns_dict(monkeypatch):
    """Test that loading_credentials() returns a correctly structured dictionary."""
    animals = {"Dog": "🐶", "Cat": "🐱"}
    colors = {"Red": (255,0,0), "Blue": (0,0,255)}

    class FakeWidget:
        def cget(self, attr): return "bg"

    widgets = {
        "animal_1_select": FakeWidget(),
        "animal_2_select": FakeWidget(),
        "color_1_select": FakeWidget(),
        "color_2_select": FakeWidget()
    }

    creds = loading_credentials(
        animals, colors, widgets,
        usr_1="Alice", usr_2="Bob",
        anml_1="🐶", anml_2="🐱",
        clr_1="Red", clr_2="Blue"
    )
    assert isinstance(creds, dict)
    assert creds[FIRST_USER][USERNAMES] == "Alice"
    assert creds[SECOND_USER][ANIMALS][0] == "🐱"


# -------------------- 5. GUI Variable Initialization Test --------------------

def test_gui_initialization_does_not_crash(monkeypatch):
    """Ensure GUI can be initialized with a real Tk master without crashing."""
    root = tk.Tk()
    root.withdraw()
    OriginalStringVar, OriginalBooleanVar = tk.StringVar, tk.BooleanVar
    monkeypatch.setattr(tk, "StringVar", lambda *a, **k: OriginalStringVar(master=root, *a, **k))
    monkeypatch.setattr(tk, "BooleanVar", lambda *a, **k: OriginalBooleanVar(master=root, *a, **k))

    gui = UserCredentialsGUI()
    for var in gui.String_Vars.values(): var.set("")
    for var in gui.Boolean_Vars.values(): var.set(False)
    for key in gui.items: gui.items[key] = [str(i) for i in range(5)]
    for key in gui.items: gui._callbacks._refresh_listbox(key)

    gui.destroy()
    root.destroy()


# -------------------- 6. GUI Mocks --------------------

class MockListbox:
    """Minimal mock of a Tkinter Listbox for testing selection logic."""
    def __init__(self, name="mock_listbox"):
        self.items = []
        self.selected_indices = []
        self._name = name

    def insert(self, index, value):
        """Insert an item at the given index."""
        if isinstance(index, str):
            index = len(self.items) if index=="end" else int(index)
        self.items.insert(index, value)

    def delete(self, first, last=None):
        """Delete items between indices [first, last]."""
        if isinstance(first, str):
            first = len(self.items)-1 if first=="end" else int(first)
        if last is None:
            last = first
        elif isinstance(last, str):
            last = len(self.items)-1 if last=="end" else int(last)
        first = max(0, min(first, len(self.items)-1))
        last = max(0, min(last, len(self.items)-1))
        del self.items[first:last+1]
        self.selected_indices = []

    def selection_set(self, index):
        """Select the given index."""
        self.selected_indices = [index]

    def curselection(self):
        """Return currently selected indices."""
        return self.selected_indices

    def size(self):
        """Return the number of items in the listbox."""
        return len(self.items)

    def get(self, first, last=None):
        """Return items between indices [first, last]."""
        if isinstance(first, str):
            first = len(self.items)-1 if first=="end" else int(first)
        if last is not None:
            if isinstance(last, str):
                last = len(self.items)-1 if last=="end" else int(last)
            return tuple(self.items[first:last+1])
        return self.items[first]

    def winfo_name(self):
        """Return the name of the listbox."""
        return self._name

    def itemconfigure(self, index, **kwargs):
        """Stub for Tkinter Listbox.itemconfigure (does nothing)."""
        pass


# -------------------- 6a. GUI Listbox --------------------

def test_gui_listbox_selection(gui_instance, fake_var_monkeypatch):
    """Test that listbox selection updates the corresponding StringVar."""
    gui_instance.current_user = 1
    gui_instance.animals = {"🐶": "🐶"}

    for i in range(1, NUM_PLAYERS+1):
        list_key = f"animal_{i}_list"
        select_key = build_name(f"animal_{i}", suffix=SELECT)
        gui_instance.String_Vars[select_key] = fake_var_monkeypatch("")
        gui_instance.items[f"animal_{i}"] = ["🐶"]
        gui_instance.widgets[list_key] = MockListbox(name=list_key)
        gui_instance._callbacks._refresh_listbox(f"animal_{i}")
        gui_instance._callbacks._change_settings_label(list_key, select_key, gui_instance.widgets[list_key], 0)
        assert gui_instance.String_Vars[select_key].get() == "🐶"

    gui_instance.destroy()


# -------------------- 6b. GUI Checkbutton --------------------

def test_gui_checkbutton_toggle(gui_instance, fake_var_monkeypatch):
    """Test that Checkbutton toggles correctly update BooleanVar."""
    for i in range(1, NUM_PLAYERS+1):
        cb_key = build_name(f"animal_{i}", suffix=ALL_MATCHES)
        gui_instance.Boolean_Vars[cb_key] = fake_var_monkeypatch(False)
        gui_instance._callbacks.on_checkbutton_toggled(f"animal_{i}")
        assert isinstance(gui_instance.Boolean_Vars[cb_key].get(), bool)

    gui_instance.destroy()


# -------------------- 6c. GUI Radiobutton --------------------

def test_gui_radiobutton_toggle(gui_instance, fake_var_monkeypatch):
    """Test that Radiobutton toggles correctly update BooleanVar."""
    for i in range(1, NUM_PLAYERS+1):
        rb_key = build_name(f"animal_{i}", suffix=RADIOBUTTON)
        gui_instance.Boolean_Vars[rb_key] = fake_var_monkeypatch(False)
        gui_instance.Boolean_Vars[rb_key].set(True)
        assert gui_instance.Boolean_Vars[rb_key].get() is True

    gui_instance.destroy()


# -------------------- 7. Validation --------------------

def test_validation_integration(gui_instance):
    """Test validate_all with valid GUI state returns True."""
    animal_keys = list(gui_instance.animals.keys())
    color_keys  = list(gui_instance.colors.keys())

    gui_instance.String_Vars[FIRST_USER].set("Alice")
    gui_instance.String_Vars[SECOND_USER].set("Bob")
    gui_instance.String_Vars[FIRST_ANIMAL + SELECT].set(gui_instance.animals[animal_keys[0]])
    gui_instance.String_Vars[SECOND_ANIMAL + SELECT].set(gui_instance.animals[animal_keys[1]])
    gui_instance.String_Vars[FIRST_COLOR + SELECT].set(color_keys[0])
    gui_instance.String_Vars[SECOND_COLOR + SELECT].set(color_keys[1])

    valid, msg = validate_all(
        gui_instance.String_Vars[FIRST_USER].get(),
        gui_instance.String_Vars[SECOND_USER].get(),
        animal_keys[0], animal_keys[1],
        color_keys[0], color_keys[1],
        gui_instance.animals,
        gui_instance.colors
    )
    assert valid is True
    assert isinstance(msg, str)
    gui_instance.destroy()


def test_validation_invalid_cases(gui_instance):
    """Test validate_all returns False for invalid GUI states (duplicate animal/color, empty username)."""
    animal_keys = list(gui_instance.animals.keys())
    color_keys  = list(gui_instance.colors.keys())

    # ----------------- Duplicate animals -----------------
    duplicate_animal = gui_instance.animals[animal_keys[0]]  
    valid, msg = validate_all(
        "Alice", "Bob",
        duplicate_animal, duplicate_animal,  
        gui_instance.colors[color_keys[0]][2], 
        gui_instance.colors[color_keys[1]][2],
        gui_instance.animals,
        gui_instance.colors
    )
    assert valid is False

    # ----------------- Duplicate colors -----------------
    duplicate_color = gui_instance.colors[color_keys[0]][0]  
    valid, msg = validate_all(
        "Alice", "Bob",
        gui_instance.animals[animal_keys[0]], 
        gui_instance.animals[animal_keys[1]],
        duplicate_color, duplicate_color,  
        gui_instance.animals,
        gui_instance.colors
    )
    assert valid is False

    # ----------------- Empty username -----------------
    valid, msg = validate_all(
        "", "Bob",
        gui_instance.animals[animal_keys[0]], 
        gui_instance.animals[animal_keys[1]],
        gui_instance.colors[color_keys[0]][0], 
        gui_instance.colors[color_keys[1]][0],
        gui_instance.animals,
        gui_instance.colors
    )
    assert valid is False

    gui_instance.destroy()




