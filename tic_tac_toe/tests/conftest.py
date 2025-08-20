# tests/conftest.py

import pytest
from unittest.mock import MagicMock

# -------------------- Dummy Classes --------------------

# ----- Root windows -----
class DummyTk:
    pass

class DummyToplevel:
    pass

# ----- Tk widgets -----
class DummyListbox:
    pass

# ----- ttk widgets -----
class DummyFrame:
    pass

class DummyButton:
    pass

class DummyScale:
    pass

class DummyLabel:
    pass

class DummyCheckbutton:
    pass

class DummyRadiobutton:
    pass

# -------------------- Fixture para mockear Tkinter globalmente --------------------
@pytest.fixture(autouse=True)
def mock_tkinter(monkeypatch):
    """
    Mock tkinter.Tk, Toplevel, ttk widgets y messagebox globalmente.
    Esto permite correr tests de GUI en CI sin display.
    """

    # ----- Patch root windows -----
    import tkinter as tk
    monkeypatch.setattr(tk, "Tk", DummyTk)
    monkeypatch.setattr(tk, "Toplevel", DummyToplevel)
    monkeypatch.setattr(tk, "Listbox", DummyListbox)

    # ----- Patch messagebox -----
    try:
        import tkinter.messagebox as msg
        monkeypatch.setattr(msg, "showinfo", MagicMock())
        monkeypatch.setattr(msg, "showwarning", MagicMock())
        monkeypatch.setattr(msg, "showerror", MagicMock())
    except ImportError:
        pass

    # ----- Patch ttk widgets -----
    try:
        import tkinter.ttk as ttk
        monkeypatch.setattr(ttk, "Frame", DummyFrame)
        monkeypatch.setattr(ttk, "Button", DummyButton)
        monkeypatch.setattr(ttk, "Scale", DummyScale)
        monkeypatch.setattr(ttk, "Label", DummyLabel)
        monkeypatch.setattr(ttk, "Checkbutton", DummyCheckbutton)
        monkeypatch.setattr(ttk, "Radiobutton", DummyRadiobutton)
    except ImportError:
        pass
