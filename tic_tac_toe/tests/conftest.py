# tests/conftest.py

import pytest
from unittest.mock import MagicMock, patch

def fake_tk_init(self, *args, **kwargs):
    self.tk = MagicMock()  # evita dependencias reales
    self._w = "mock"       # Tkinter usa esto como identificador
    self.children = {}

@pytest.fixture(autouse=True)
def patch_tkinter():
    with patch("tkinter.Tk.__init__", new=fake_tk_init), \
         patch("tkinter.Tk.mainloop", return_value=None), \
         patch("tkinter.IntVar", new=MagicMock), \
         patch("tkinter.StringVar", new=MagicMock), \
         patch("tkinter.BooleanVar", new=MagicMock):
        yield

