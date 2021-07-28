from typing import Callable


class MenuItem():
    """Item for the menu user interface.

    @param text: Display text for the item
    @param handle_select: Callback function when the item is selected"""

    def __init__(self, text: str, handle_select: Callable[[], None] = None):
        self.text = text
        self.handle_select = handle_select

        self.handle_select = handle_select
        if handle_select is None:
            self.handle_select = lambda: None


class MenuDivider(MenuItem):
    """Divider for the menu user interface. Represented as a blank menu item."""

    def __init__(self):
        super().__init__("", None)


class Menu():
    """Menu user interface - all user interaction occurs through a main menu and several submenus.

    @param handle_close: Callback function to close the menu once an item is selected.
    @param hover_dec: Blessed Terminal function to provide colour for the currently hovered item.
    """

    def __init__(self, hover_dec: Callable[[str], str] = None) -> None:

        # List of menu items ordered top to bottom in appearance
        self.items = []

        # Index of currently hovered item
        self.hover_index = 0

        # Function to decorate currently hovered item
        self.hover_dec = hover_dec
        if hover_dec is None:
            self.hover_dec = lambda: None

    # ========================================================
    # Create menu methods
    # ========================================================

    def add_item(self, text: str, handle_item_select: Callable[[], None] = None) -> int:
        """Creates and adds a menu item to the bottom of the menu.
        Returns the index of the added item."""

        item = MenuItem(text, handle_item_select)
        self.items.append(item)

        return len(self.items) - 1

    def add_divider(self) -> int:
        """Creates and adds a divider (a blank menu item) to the bottom of the menu.
        Returns the index of the added divider."""

        divider = MenuDivider()
        self.items.append(divider)

        return len(self.items) - 1

    # ========================================================
    # User interaction handlers
    # ========================================================

    def handle_hover_up(self) -> None:
        """Moves the hover index up to the next menu item."""

        new_hover_index = self.hover_index - 1

        while new_hover_index >= 0 and isinstance(self.items[new_hover_index], MenuDivider):
            new_hover_index -= 1

        if new_hover_index == -1:
            return

        self.hover_index = new_hover_index

    def handle_hover_down(self) -> None:
        """Moves the hover index down to the next menu item."""

        new_hover_index = self.hover_index + 1
        n = len(self.items)

        while new_hover_index < n and isinstance(self.items[new_hover_index], MenuDivider):
            new_hover_index += 1

        if new_hover_index == n:
            return

        self.hover_index = new_hover_index

    def handle_select(self) -> None:
        """Selects the current hovered menu item and closes the menu (if function is given)"""

        self.items[self.hover_index].handle_select()

    # ========================================================
    # Override interaction handlers
    # ========================================================

    def set_hover(self, index: int) -> None:
        """Sets the hover index"""

        if index < 0 or index >= len(self.items):
            raise IndexError
        if isinstance(self.items[index], MenuDivider):
            raise Exception("Hover index cannot be set to a MenuDivider")

        self.hover_index = index

    # ========================================================
    # Terminal printing methods
    # ========================================================

    def get_print_strings(self) -> str:
        """Returns a list of strings formatted for printing"""

        print_strings = []

        for i, item in enumerate(self.items):
            if self.hover_index == i:
                print_strings.append(self.hover_dec(item.text))
            else:
                print_strings.append(item.text)

        return print_strings
