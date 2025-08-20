# tests/conftest.py

import pytest
from unittest.mock import MagicMock

# -------------------- Dummy Classes --------------------

# ----- Root windows -----
class DummyTk:
    def __init__(self, *args, **kwargs):
        pass

class DummyToplevel:
    def __init__(self, *args, **kwargs):
        pass

# ----- Tk widgets -----
class DummyListbox:
    def __init__(self, *args, **kwargs):
        pass

# ----- ttk widgets -----
class DummyFrame:
    def __init__(self, *args, **kwargs):
        pass

class DummyButton:
    def __init__(self, *args, **kwargs):
        pass

class DummyScale:
    def __init__(self, *args, **kwargs):
        pass

class DummyLabel:
    def __init__(self, *args, **kwargs):
        pass

class DummyCheckbutton:
    def __init__(self, *args, **kwargs):
        pass

class DummyRadiobutton:
    def __init__(self, *args, **kwargs):
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
    monkeypatch.setattr(tk, "Listbox", DummyListbox)  # Listbox está en tkinter, no ttk

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
