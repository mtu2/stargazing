from abc import ABC, abstractmethod
from typing import Callable

from utils.helper_funcs import check_null_fn


class MenuItem():
    """Item for the menu user interface.

    @param text: Display text for the item
    @param handle_select: Callback function when the item is selected"""

    def __init__(self, text: str, handle_select: Callable[[], None] = None):
        self.text = text
        self.handle_select = check_null_fn(handle_select)


class Menu(ABC):
    """Menu user interface - all user interaction occurs through a main menu and several submenus.
    Astract class that requires implementing handle_close.

    @param hover_dec: Blessed terminal function to provide colour for the currently hovered item."""

    def __init__(self, hover_dec: Callable[[str], str] = None) -> None:

        # List of menu items ordered top to bottom in appearance
        self.items = []

        # List of indexes for dividers - appears after the index of the corresponding menu item
        self.dividers = []

        # Index of currently hovered item
        self.hover_index = 0

        # Function to decorate currently hovered item
        self.hover_dec = check_null_fn(hover_dec)

    # ========================================================
    # Create menu methods
    # ========================================================

    def add_item(self, text: str, handle_item_select: Callable[[], None] = None, index: int = None) -> int:
        """Creates and adds a menu item at the given index. If no index is given, the item 
        is added to the bottom of the menu. Returns the index of the added item."""

        if index is None:
            index = len(self.items)

        if index < 0 or index > len(self.items):
            raise IndexError

        item = MenuItem(text, handle_item_select)
        self.items.insert(index, item)

        return index

    def replace_item(self, index, text: str, handle_item_select: Callable[[], None] = None) -> None:
        """Creates and replaces a menu item at the given index."""

        if index < 0 or index >= len(self.items):
            raise IndexError(f"Entered invalid index: {index}")

        item = MenuItem(text, handle_item_select)
        self.items[index] = item

    def add_divider(self) -> int:
        """Creates and adds a divider (a blank menu item) to the bottom of the menu.
        Returns the index of the added divider."""

        self.dividers.append(len(self.items) - 1)

        return len(self.dividers) - 1

    # ========================================================
    # User interaction handlers
    # ========================================================

    def handle_key_up(self) -> None:
        """Moves the hover index up to the next menu item."""

        new_hover_index = max(self.hover_index - 1, 0)
        self.hover_index = new_hover_index

    def handle_key_down(self) -> None:
        """Moves the hover index down to the next menu item."""

        new_hover_index = min(self.hover_index + 1, len(self.items) - 1)
        self.hover_index = new_hover_index

    def handle_key_enter(self) -> None:
        """Selects the current hovered menu item and closes the menu (if function is given)"""

        self.items[self.hover_index].handle_select()

    def handle_key_escape(self) -> None:
        """Handles escape key sequences"""
        pass

    def handle_key_backspace(self) -> None:
        """Handles backspace key sequences"""
        pass

    def handle_char_input(self, char) -> None:
        """Handles character keyboard input"""
        pass

    @abstractmethod
    def handle_close(self, *args) -> None:
        """Handles menu close - must be implemented by children classes"""
        pass

    # ========================================================
    # Manual interaction handlers
    # ========================================================

    def set_hover(self, index: int) -> None:
        """Manually sets the hover index"""

        if index < 0 or index >= len(self.items):
            raise IndexError

        self.hover_index = index

    # ========================================================
    # Terminal printing helper methods
    # ========================================================

    def get_print_strings(self) -> str:
        """Returns a list of strings formatted for terminal printing"""

        print_strings = []
        dividers_p = 0

        for i, item in enumerate(self.items):
            while dividers_p < len(self.dividers) and self.dividers[dividers_p] < i:
                print_strings.append("")
                dividers_p += 1

            if self.hover_index == i:
                print_strings.append(self.hover_dec(item.text))
            else:
                print_strings.append(item.text)

        return print_strings
