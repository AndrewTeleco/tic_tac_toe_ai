#!/usr/bin/env python3

"""
USER CREDENTIALS GUI MODULE

Provides the graphical interface for the Tic-Tac-Toe user credential setup, 
handling:
- Player username, animal, and color selection
- Dynamic filtering and widget interaction
- Coordination with callbacks, validation, and storage modules

Structure:
1. Initialization & Attributes
2. Window & GUI Setup
3. User Interface (Per Player Section)
4. Widget Factory Methods
5. Callback Methods

Author: Andrés David Aguilar Aguilar
Date: 2025-07-14
"""

import tkinter as tk
from itertools import cycle
from tkinter import messagebox as msgbox
from typing import Dict, List, Optional

from tic_tac_toe.core.helper_methods import (
    build_name, 
    build_widget_names,
    get_animal_name
)
from tic_tac_toe.core.literals import *

from tic_tac_toe.user_config.user_credentials_callbacks import UserCredentialsCallbacks
from tic_tac_toe.user_config.user_credentials_storage import (
    store_data, 
    load_animal_list, 
    load_color_list, 
    loading_credentials, 
    process_logs
)
from tic_tac_toe.user_config.user_credentials_validator import validate_all


class UserCredentialsGUI(tk.Tk):
    """GUI for entering user credentials for TicTacToe."""

    # ───────────────────────────────────────────────
    # 1. Initialization and Attributes
    # ───────────────────────────────────────────────

    def __init__(self) -> None:
        """
        Initialize the User Credentials GUI and build all components.

        -------------------------------
        UserCredentialsGUI Layout Overview
        -------------------------------

        UserCredentialsGUI (tk.Tk)
        │
        ├── self.header_frame : tk.Frame
        │       └── self.header_label : tk.Label
        │            (Displays "Enter player credentials")
        │
        ├── self.frame : tk.Frame  (Main container for player forms)
        │       ├── Player 1 Section (tk.LabelFrame)
        │       │    ├── Username Entry (tk.Entry)
        │       │    ├── Animal Selection:
        │       │    │    ├── Entry Filter (tk.Entry)
        │       │    │    ├── Listbox + Scrollbar (tk.Listbox + tk.Scrollbar)
        │       │    │    ├── Checkbutton "All matches" (tk.Checkbutton)
        │       │    │    └── Radiobuttons Dark/Light (tk.Radiobutton)
        │       │    └── Color Selection:
        │       │         ├── Entry Filter (tk.Entry)
        │       │         ├── Listbox + Scrollbar (tk.Listbox + tk.Scrollbar)
        │       │         └── Checkbutton "All matches" (tk.Checkbutton)
        │       │
        │       └── Player 2 Section (same structure as Player 1)
        │
        └── self.btn_frame : tk.Frame
                └── self.button : tk.Button ("Start Game" action)
        """
        super().__init__()

        # Load data from storage
        self.animals: Dict[str, str] = load_animal_list()
        self.animal_icons_to_names: Dict[str, str] = {emoji: name for name, emoji in self.animals.items()}

        self.colors: Dict[str, tuple[int, int, int]] = load_color_list()

        # Instantiate callbacks handler, passing self for access to widgets, vars, etc.
        self._callbacks: UserCredentialsCallbacks = UserCredentialsCallbacks(self)

        # Initialize GUI internal state containers
        self._init_attributes()

        # Initialize tk Variables for binding to widgets
        self.Boolean_Vars: Dict[str, tk.BooleanVar] = {}
        self.String_Vars: Dict[str, tk.StringVar] = {}

        self._init_vars()

        # Configure window and build GUI components
        self._configure_window_form("Tic-Tac-Toe Game - Log in", 850, 500)
        self._set_header_form()
        self._set_main_form()


    def _init_attributes(self) -> None:
        """
        Initialize internal state and control structures.

        Args:
            validator (UserCredentialsValidator): The validator instance.
        
        Raises:
            TypeError: If the provided validator is not a UserCredentialsValidator instance.
        """

        # Containers for widgets, data, state
        self.filters: Dict[str, Optional[str]] = {}
        self.items: Dict[str, List[str]] = {}
        self.widgets: Dict[str, tk.Widget] = {}
        self.lasts: Dict[str, str] = {}
        self.logs: List[str] = []
        self.credentials: Dict = {}

        # Player turn cycle (not fully used here but kept for consistency)
        self.user_iter = cycle(range(NUM_PLAYERS))
        self.current_user: Optional[int] = None

        # Initialize lasts for animals and colors per player
        for i in range(1, NUM_PLAYERS + 1):
            self.lasts[ANIMAL + str(i)] = EMPTY
            self.lasts[COLOR + str(i)] = EMPTY


    def _init_vars(self) -> None:
        """Initialize BooleanVars and StringVars for GUI widget bindings."""
        expr_bool = lambda val: tk.BooleanVar(value=val)
        expr_str = lambda val: tk.StringVar(value=val)

        # Helper for the "All matches" labels
        def expr_all_matches(items_dict: Dict[str, any], item_type: str) -> str:
            return f"All matches\n({len(items_dict)} {item_type})"

        for i in range(1, NUM_PLAYERS + 1):
            self.String_Vars[USERNAME + str(i)] = expr_str(EMPTY)
            self.String_Vars[ANIMAL + str(i)] = expr_str(EMPTY)
            self.String_Vars[COLOR + str(i)] = expr_str(EMPTY)

            self.String_Vars[ANIMAL + str(i) + SELECT] = expr_str(EMPTY)
            self.String_Vars[COLOR + str(i) + SELECT] = expr_str(EMPTY)

            self.String_Vars[ANIMAL + str(i) + CHECKBUTTON] = expr_str(expr_all_matches(self.animals, ANIMALS))
            self.String_Vars[COLOR + str(i) + CHECKBUTTON] = expr_str(expr_all_matches(self.colors, COLORS))

            self.Boolean_Vars[ANIMAL + str(i) + ALL_MATCHES] = expr_bool(False)
            self.Boolean_Vars[COLOR + str(i) + ALL_MATCHES] = expr_bool(False)

            self.Boolean_Vars[ANIMAL + str(i) + RADIOBUTTON] = expr_bool(False)


    # ───────────────────────────────────────────────
    # 2. Window and GUI Setup
    # ───────────────────────────────────────────────

    def _configure_window_form(self, title: str, width: int, height: int, y_offset: int = 0) -> None:
        """
        Configure the main window of the GUI.

        Args:
            title (str): Window title.
            width (int): Window width in pixels.
            height (int): Window height in pixels.
            y_offset (int, optional): Vertical offset for window placement. Defaults to 0.
        """
        self.title(title)
        self.resizable(False, False)
        self.minsize(width=width, height=height)

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        pos_x = (screen_w - width) // 2
        pos_y = (screen_h - height) // 2 - y_offset

        self.geometry(f"{width}x{height - y_offset}+{pos_x}+{pos_y}")
        self.configure(background=BLACK, padx=0, pady=0)


    def _set_header_form(self) -> None:
        """Create and pack the header section of the GUI."""
        self.header_frame = tk.Frame(self, bg=COLOR_BG_DEFAULT)
        self.header_frame.pack(padx=5, pady=5)

        self.header_label = tk.Label(
            self.header_frame,
            text=TEXT_START_CREDENTIALS,
            bg=COLOR_BG_DEFAULT,
            fg=COLOR_BOX_CREDENTIALS,
            font=FONT_DISPLAY,
            highlightbackground=COLOR_HIGHLIGHT_TEXT_CREDENTIALS,
            highlightthickness=1
        )
        self.header_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)


    def _set_main_form(self) -> None:
        """Create the main section of the GUI for user input."""
        self.frame = tk.Frame(
            self,
            name=FRAME,
            bg=COLOR_BG_DEFAULT,
            highlightbackground=COLOR_HIGHLIGHT_TEXT_CREDENTIALS,
            highlightcolor=COLOR_HIGHLIGHT_TEXT_CREDENTIALS,
            highlightthickness=1
        )
        self.frame.pack(padx=10, pady=5)

        for player_id in range(1, NUM_PLAYERS + 1):
            self._create_user_section(player_id)
        self._create_submit_button_if_last_user(NUM_PLAYERS)


    def _create_user_section(self, player_num: int) -> None:
        """
        Create the full user input section (form) for a given player.

        Args:
            player_num (int): Player number (1 or 2).
        """       
        self._create_main_user_frame(player_num)
        self._create_username_fields(player_num)
        self._create_fields(ANIMAL, player_num, 3, SELECT_ANIMAL)
        self._create_fields(COLOR, player_num, 7, SELECT_COLOR)


    # ───────────────────────────────────────────────
    # 3. User Interface Setup (Per Player Section)
    # ───────────────────────────────────────────────

    def _create_main_user_frame(self, player_num: int) -> None:
        """
        Create the main container frame for the user credentials section.

        Args:
            player_num (int): The current player number.
        """
        self.main_frame = tk.LabelFrame(
            self.frame,
            name=build_name(str(player_num), suffix=FRAME),
            text=f' USER PLAYER {player_num} 🎮 ',
            bg=COLOR_BG_DEFAULT,
            fg=COLOR_HIGHLIGHT_TEXT_CREDENTIALS,
            font=FONT_MEDIUM_BOLD,
            labelanchor=tk.N
        )
        self.main_frame.pack(padx=15, pady=15, ipadx=5, ipady=5, side=tk.LEFT)


    def _create_username_fields(self, player_num: int) -> None:
        """
        Create the username label and entry widgets for the current user.

        Args:
            player_num (int): Player number.
        """
        row, col = 2, 0
        entry_name = build_name(str(player_num), prefix=USERNAME)
        self._create_new_label(
            build_name(entry_name, suffix=LABEL), 
            row, col, sticky=tk.NSEW, text=USERNAME_COLON
        )
        self._create_new_entry(
            entry_name, row, col + 1, colspan=2, 
            length=18, sticky=tk.EW
        )


    def _create_fields(self, prefix: str, player_num: int, row: int, label_text: str) -> None:
        """
        Create a generic set of widgets (entry, listbox, checkbutton, etc.)
        for the current user based on the given prefix (ANIMAL or COLOR).

        Args:
            prefix (str): The prefix for widget names (e.g., ANIMAL, COLOR).
            player_num (int): The player number (1 or 2).
            row (int): Starting row position in the layout.
            label_text (str): Text for the main label (e.g., 'SELECT ANIMAL:', 'SELECT COLOR:').
        """
        widget_names = build_widget_names(prefix, str(player_num), [CHECKBUTTON, ALL_MATCHES, SELECT, LABEL, LIST])

        self._create_new_label(widget_names[LABEL], row, 0, sticky=tk.NS, text=label_text)
        self._create_new_entry(widget_names['base'], row, 1, sticky=tk.NS)
        self._create_new_checkbutton(widget_names[CHECKBUTTON], widget_names[ALL_MATCHES], player_num, row, 2)

        self._create_new_listbox_and_scrollbar(
            widget_names[LIST],
            player_num,
            row + 1,
            1,
            colspan=2,
            rowspan=2 if prefix == ANIMAL else None,  
            sticky=tk.NSEW if prefix == ANIMAL else tk.EW
        )

        if prefix == COLOR:
            self._create_new_label(widget_names[SELECT], row + 1, 0, sticky=tk.NSEW)
        elif prefix == ANIMAL:
            self._create_new_label(widget_names[SELECT], row + 1, 0, sticky=tk.NSEW, font=FONT_LARGE_BOLD)
            self._create_animal_radiobuttons(player_num, widget_names)


    def _create_submit_button_if_last_user(self, player_num: int) -> None:
        """
        Create and place the submit button to start the game if this is the last user being configured.

        Args:
            player_num (int): Player number.
        """
        if player_num == NUM_PLAYERS:
            self.btn_frame = tk.Frame(self, bg=BLACK, highlightbackground=BLACK, highlightthickness=1)
            self.btn_frame.pack(ipadx=10, ipady=10)
            self.button = tk.Button(
                self.btn_frame,
                text=TEXT_START_BUTTON,
                fg=COLOR_BG_DEFAULT,
                bg=COLOR_HIGHLIGHT_TEXT_CREDENTIALS,
                font=FONT_MEDIUM_BOLD,
                command=self._on_play_pressed
            )
            self.button.grid(sticky=tk.NSEW, pady=5)


    # ───────────────────────────────────────────────
    # 4. Widget Factory Methods
    # ───────────────────────────────────────────────

    def _create_new_label(
        self,
        name: str,
        row: int,
        col: int,
        colspan: Optional[int] = None,
        rowspan: Optional[int] = None,
        sticky: Optional[str] = None,
        text: Optional[str] = None,
        font: str = FONT_SMALL_BOLD,
    ) -> None:
        """
        Creates a Label widget that may be bound to a StringVar.

        Args:
            name (str): Widget name.
            row (int): Grid row.
            col (int): Grid column.
            colspan (int, optional): Column span.
            rowspan (int, optional): Row span.
            sticky (str, optional): Sticky alignment.
            text (str, optional): Text to display (if None, binds to StringVar).
            font (str, optional): Font specification.
        """
        self.widgets[name] = tk.Label(
            self.main_frame,
            name=name,
            text=text if text is not None else None,
            textvariable=self.String_Vars[name] if text is None else None,
            font=font,
            fg=COLOR_HIGHLIGHT_TEXT_CREDENTIALS,
            bg=COLOR_BG_DEFAULT
        )
        self.widgets[name].grid(row=row, column=col, columnspan=colspan, rowspan=rowspan, sticky=sticky, padx=5)


    def _create_new_entry(
        self, 
        name: str, 
        row: int, 
        col: int, 
        colspan: Optional[int] = None, 
        length: int = MAX_LENGHT, 
        sticky: Optional[str] = None
    ) -> None:
        """
        Creates a custom Entry widget with a trace on input.

        Args:
            name (str): Widget name.
            row (int): Grid row.
            col (int): Grid column.
            colspan (int, optional): Column span.
            length (int, optional): Max length for entry input.
            sticky (str, optional): Sticky alignment.
        """
        is_username = USERNAME in name
        font = FONT_MEDIUM_BOLD if is_username else FONT_SMALL_BOLD

        self.widgets[name] = tk.Entry(
            self.main_frame,
            name=name,
            textvariable=self.String_Vars[name],
            font=font,
            justify=tk.CENTER,
            bg=COLOR_BOX_CREDENTIALS,
            fg=COLOR_BG_DEFAULT
        )
        self.widgets[name].grid(row=row, column=col, columnspan=colspan, sticky=sticky, pady=5)

        last_key = build_name(name, suffix=LAST)
        self.lasts[last_key] = EMPTY
        self.String_Vars[name].set(EMPTY)

        self.String_Vars[name].trace_add(
            WRITE,
            lambda *args, n=name, l=last_key, length=length: self._callbacks.on_entry_updated(n, l, length),
        )


    def _create_new_checkbutton(self, name: str, all_matches: str, player_num: int, row: int, col: int) -> None:
        """
        Creates a custom Checkbutton widget with automatic update command.

        Args:
            name (str): Widget name.
            all_matches (str): Name of the related all_matches variable.
            player_num (int): Player number.
            row (int): Grid row.
            col (int): Grid column.
        """
        prefix = (ANIMAL if ANIMAL in name else COLOR)
        field = build_name(str(player_num), prefix=prefix)

        self.widgets[name] = tk.Checkbutton(
            self.main_frame,
            name=name,
            variable=self.Boolean_Vars[all_matches],
            textvariable=self.String_Vars[name],
            selectcolor=BLACK,
            onvalue=True,
            offvalue=False,
            font=(FONT_FAMILY_DEFAULT, 7, BOLD),
            bg=COLOR_BG_DEFAULT,
            fg=COLOR_BOX_CREDENTIALS,
            command=lambda n=field: self._callbacks.on_checkbutton_toggled(n)
        )
        self.widgets[name].grid(row=row, column=col)


    def _create_new_listbox_and_scrollbar(
        self, 
        name: str, 
        player_num: int, 
        row: int, 
        col: int, 
        rowspan: Optional[int] = None, 
        colspan: Optional[int] = None, 
        sticky: Optional[str] = None
    ) -> None:
        """
        Creates a Listbox widget with vertical scrollbar and live filtering.

        Args:
            name (str): Widget name.
            player_num (int): Player number.
            row (int): Grid row.
            col (int): Grid column.
            rowspan (int, optional): Row span.
            colspan (int, optional): Column span.
            sticky (str, optional): Sticky alignment.
        """
        self.widgets[name] = tk.Listbox(
            self.main_frame,
            name=name,
            height=5,
            bg=COLOR_HIGHLIGHT_TEXT_CREDENTIALS,
            font=FONT_SMALL_BOLD,
            justify=tk.CENTER
        )
        self.widgets[name].grid(row=row, column=col, columnspan=colspan, rowspan=rowspan, sticky=sticky)

        scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL)
        scrollbar.grid(row=row, column=col + 1, rowspan=rowspan, sticky=(tk.NS, tk.E))
        self.yscrollbar = scrollbar

        self.widgets[name].config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.widgets[name].yview)

        self.widgets[name].bind(
            '<<ListboxSelect>>', lambda e, n=name: self._callbacks.on_listbox_selected(n, e),
        )

        prefix = (ANIMAL if ANIMAL in name else COLOR)
        field = build_name(str(player_num), prefix=prefix)

        self.filters[field] = None
        self.items[field] = (
            sorted(self.animals.keys()) if ANIMAL in name else list(self.colors.keys())
        )

        self._callbacks._refresh_listbox(field)


    def _create_animal_radiobuttons(self, player_num: int, widget_names: Dict[str, str]) -> None:
        """
        Create radio buttons to toggle between dark and light themes for the selected animal.

        Args:
            player_num (int): Player number.
            widget_names (Dict[str, str]): Widget name dictionary.
        """
        self.rbtn_frame = tk.Frame(self.main_frame)
        self.rbtn_frame.grid(row=6, column=0)

        switch_key = build_name(str(player_num), prefix=ANIMAL, suffix=RADIOBUTTON)
        target_key = widget_names[SELECT]

        for value, text, side in [(False, DARK, tk.LEFT), (True, LIGHT, tk.RIGHT)]:
            suffix = BLACK if value else WHITE
            name = build_name(switch_key, suffix=suffix)
            self._create_new_radiobutton(name, text, value, side, target_key, switch_key)


    def _create_new_radiobutton(
        self, name: str, text: str, value: bool, side: str, target: str, switch: str
    ) -> None:
        """
        Create a Radiobutton to select animal background color (dark/light).

        Args:
            name (str): Widget name.
            text (str): Label text.
            value (bool): Value assigned to radiobutton.
            side (str): Side to pack the widget.
            target (str): Target widget name.
            switch (str): Switch widget name.
        """
        self.widgets[name] = tk.Radiobutton(
            self.rbtn_frame,
            name=name,
            text=text,
            variable=self.Boolean_Vars[switch],
            value=value,
            selectcolor=WHITE,
            activebackground=COLOR_BOX_CREDENTIALS,
            activeforeground=COLOR_BG_DEFAULT,
            font=(FONT_FAMILY_DEFAULT, 8, BOLD),
            bg=COLOR_BOX_CREDENTIALS,
            fg=COLOR_BG_DEFAULT,
            command=lambda t=target, s=switch: self._callbacks.on_radiobutton_changed(t, s),
        )
        self.widgets[name].pack(side=side)


    # ───────────────────────────────────────────────
    # 5. Callback Methods
    # ───────────────────────────────────────────────

    def _show_error_message(self, title: str, msg: str) -> bool:
        """
        Show an error message dialog and reset credentials.

        Args:
            title (str): Dialog title.
            msg (str): Error message.

        Returns:
            bool: Always returns False.
        """
        msgbox.showerror(title=title,message=msg)
        self.credentials = dict()
        return False
    

    def _on_play_pressed(self):
        """Callback for the play/start button press. Validates input and proceeds if valid."""
        usr_1 = self.String_Vars[FIRST_USER].get().strip()
        usr_2 = self.String_Vars[SECOND_USER].get().strip()
        anml_1 = self.String_Vars[FIRST_ANIMAL + SELECT].get()
        anml_2 = self.String_Vars[SECOND_ANIMAL + SELECT].get()
        clr_1 = self.String_Vars[FIRST_COLOR + SELECT].get()
        clr_2 = self.String_Vars[SECOND_COLOR + SELECT].get()

        anml_1_name = get_animal_name(anml_1, self.animal_icons_to_names)
        anml_2_name = get_animal_name(anml_2, self.animal_icons_to_names)

        valid, msg = validate_all(
            usr_1, usr_2, anml_1_name, anml_2_name,
            clr_1, clr_2, self.animals, self.colors
        )

        if not valid:
            msgbox.showerror("Validation Error", msg)
            return
        
        msgbox.showinfo('TicTacToe Game ✅', msg)
        
        self.credentials = loading_credentials(
            self.animals, self.colors, self.widgets, 
            usr_1, usr_2, anml_1, anml_2, clr_1, clr_2
        )

        process_logs(
            user=self.current_user,
            animals=self.animals,
            colors=self.colors,
            string_vars=self.String_Vars,
            lasts=self.lasts,
            logs=self.logs,
            credentials=self.credentials
        )

        store_data(credentials=self.credentials, logs=self.logs)

        self.destroy()










    
