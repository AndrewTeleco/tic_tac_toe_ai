#!/usr/bin/env python3

"""
USER CREDENTIALS CALLBACKS MODULE
---------------------------------

This module defines the `UserCredentialsCallbacks` class, which centralizes 
all callback and event-handling logic for the `UserCredentialsGUI`. 
Its purpose is to keep the GUI class lean by delegating the logic 
of entry updates, listbox selections, checkbutton toggles, and 
radiobutton changes to a separate, cohesive component.

Responsibilities:
-----------------
1. **Entry Management**  
   - Validate input in entry widgets (e.g., usernames).
   - Update internal state and enforce input constraints.

2. **Listbox Handling**  
   - Update listbox contents dynamically based on user filters.
   - Handle item selection and refresh related labels and widgets.

3. **Checkbutton and Radiobutton Control**  
   - Filter listboxes when checkbuttons are toggled.
   - Change background colors and states of widgets based on user actions.

4. **User Turn Management**  
   - Keep track of the currently active user based on GUI focus.

5. **Logging and Synchronization**  
   - Trigger log updates for selected animal and color combinations.
   - Synchronize GUI state with internal variables (`StringVar`, `BooleanVar`).

Structure:
----------
- `UserCredentialsCallbacks`: Main class containing:
    1. Initialization
    2. Callback methods (public)
    3. Callback helper methods (private)
    4. Player turn management
    5. Utility helper methods for widget name construction

Author:
-------
Andrés David Aguilar Aguilar

Date:
-----
2025-07-24
"""


import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from user_credentials_gui import UserCredentialsGUI 

from tic_tac_toe.core.helper_methods import (
    build_name, 
    parse_entry_bg,
    format_key
)
from tic_tac_toe.core.literals import *
from tic_tac_toe.user_config.user_credentials_storage import process_logs
from tic_tac_toe.user_config.user_credentials_validator import validate_username


class UserCredentialsCallbacks:
    """
    Class responsible for handling callbacks and GUI-related events 
    for UserCredentialsGUI. It decouples the event logic from the 
    main GUI class to keep it clean and maintainable.
    """

    # ───────────────────────────────────────────────
    # 1. Initialization
    # ───────────────────────────────────────────────

    def __init__(self, gui: 'UserCredentialsGUI') -> None:
        """
        Initialize the callback manager with a reference to the main GUI.
        
        Args:
            gui (UserCredentialsGUI): The main GUI instance.
        """
        self.gui = gui


    # ───────────────────────────────────────────────
    # 2. Callback methods
    # ───────────────────────────────────────────────

    def on_entry_updated(self, name: str, last: str, length: int, *args: object) -> None:
        """
        Handle entry update events. Validates the content of the entry
        and updates the associated data structures.

        Args:
            name (str): Entry widget name.
            last (str): Key to track the previous valid value.
            length (int): Maximum allowed length.
            *args: Extra arguments passed by `trace_add`.
        """
        self._update_current_user()
        text = self.gui.String_Vars[name].get()

        if validate_username(text, length=length):
            self.gui.lasts[last] = text
        else:
            self.gui.String_Vars[name].set(self.gui.lasts[last])

        self._refresh_listbox(name)

        listbox = build_name(name, suffix=LIST)
        select = build_name(name, suffix=SELECT)

        if USERNAME not in name and self.gui.widgets[listbox].size():
            self._change_settings_label(listbox, select)


    def on_listbox_selected(self, listbox_name: str, *args: object) -> None:
        """
        Handle item selection in a listbox and update related labels
        and styles.

        Args:
            listbox_name (str): Name of the listbox widget.
            *args: Event arguments (optional).
        """
        event = args[0]
        listbox = self.gui.widgets.get(listbox_name)

        if not listbox: 
            return
        
        widget = getattr(event, WIDGET, listbox)
        focused = self.gui.focus_get()

        if (focused == listbox and
            widget.size() > 0 and
            widget.curselection()):
            
            index = widget.curselection()[0]
            self._change_settings_label(
                listbox_name,
                build_name(listbox_name.rstrip(LIST) , suffix=SELECT),
                event=widget,
                index=index
            )


    def on_checkbutton_toggled(self, name: str) -> None:
        """
        Handle checkbutton toggle events by refreshing the listbox.
        """
        self._refresh_listbox(name)


    def on_radiobutton_changed(self, anml: str, switch: str) -> None:
        """
        Handle animal radio button state changes and update widget background.

        Args:
            anml (str): Key for animal selection widget.
            switch (str): Key for the associated radio state variable.
        """
        is_light = self.gui.Boolean_Vars[switch].get()
        self.gui.widgets[anml].config(bg=WHITE if is_light else COLOR_BG_DEFAULT)


    # ───────────────────────────────────────────────
    # 3. Callback helper methods
    # ───────────────────────────────────────────────

    def _change_settings_label(
        self, listbox: str, select: str, 
        event: tk.Listbox | tk.Event | None = None, 
        index: int | None = None
    ) -> None:
        """
        Update label and widget styles when a listbox item is selected.

        Args:
            listbox (str): Name of the listbox.
            select (str): Key for the associated selection variable.
            event (tk.Event, optional): Event object if triggered by user action.
            index (int, optional): Index of the selected item.
        """
        key = EMPTY
        if event and index:
            key = event.get(index)
            self.gui.String_Vars[select].set(format_key(key, select, self.gui.animals))
        elif self.gui.widgets[listbox].get('0'):
            key = self.gui.widgets[listbox].get('0')
            self.gui.String_Vars[select].set(format_key(key, select, self.gui.animals))

        self._update_current_user()
        
        anml =  build_name(str(self.gui.current_user), prefix=ANIMAL, suffix=SELECT)
        clr = build_name(str(self.gui.current_user), prefix=COLOR, suffix=SELECT)
        color = self.gui.String_Vars[clr].get()

        if COLOR in select:
            self.gui.widgets[select].config(
                bg=color if color else COLOR_BG_DEFAULT, 
                fg=parse_entry_bg(color),
                font=FONT_SMALL_BOLD
            )

        self.gui.widgets[anml].config(
            fg=color if color else COLOR_HIGHLIGHT_TEXT_CREDENTIALS, 
            font=FONT_LARGE_BOLD
        )

        process_logs(
            user=self.gui.current_user,
            animals=self.gui.animals,
            colors=self.gui.colors,
            string_vars=self.gui.String_Vars,
            lasts=self.gui.lasts,
            logs=self.gui.logs,
            animal=self.gui.String_Vars[anml].get(), 
            color=color
        )


    def _change_settings_listbox(self, index: int, item: str, listbox: str) -> None:
        """
        Insert a new item in the listbox with custom colors.

        Args:
            index (int): Index to insert the item.
            item (str): Item text.
            listbox (str): Name of the listbox.
        """
        self.gui.widgets[listbox].insert(tk.END, item)
        self.gui.widgets[listbox].itemconfigure(
            index, 
            bg=item if COLOR in listbox else COLOR_HIGHLIGHT_TEXT_CREDENTIALS,
            fg=(parse_entry_bg(item) if COLOR in listbox 
                else COLOR_BG_DEFAULT)
        )


    def _refresh_listbox(self, name: str) -> None:
        """
        Refresh the contents of the listbox associated with the given entry name.
        Safely checks if the listbox exists before attempting to update it.

        Args:
            name (str): The base widget name (e.g., 'animal1', 'color2').
        """
        listbox = build_name(name, suffix=LIST)
        if listbox not in self.gui.widgets:
            return  
    
        all_matches = build_name(name, suffix=ALL_MATCHES)
        checkbutton = build_name(name, suffix=CHECKBUTTON)

        self.gui.widgets[listbox].delete(0, tk.END)

        entry_text = self.gui.String_Vars.get(name, tk.StringVar()).get().strip()
        include_all = self.gui.Boolean_Vars.get(all_matches, tk.BooleanVar(value=False)).get()

        items = self.gui.items.get(name, [])

        filtered_items = [
            item for item in items
            if (item.lower().startswith(entry_text.lower())
                or (include_all and entry_text.lower() in item.lower()))
        ]

        for index, item in enumerate(filtered_items):
            self._change_settings_listbox(index, item, listbox)

        category = ANIMALS if ANIMAL in name else COLORS
        size = len(filtered_items)
        self.gui.String_Vars[checkbutton].set(
            f'All matches\n({size} {category.rstrip("s") if size == 1 else category})'
        )


    # ───────────────────────────────────────────────
    # 4. Player turn management 
    # ───────────────────────────────────────────────

    def _update_current_user(self) -> None:
        """
        Update the current user index based on the focused widget.
        """
        focused = self.gui.focus_get()
        if not focused or focused == self.gui:
            return
        widget_name = focused.winfo_name()
        if str(self.gui.current_user) not in widget_name:
            self.gui.current_user = next(self.gui.user_iter) + 1



    



    




    


    

