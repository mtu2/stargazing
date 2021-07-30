from functools import partial
from typing import Callable

from blessed import Terminal
from utils.menu import Menu


class AutoStartMenu(Menu):

    def __init__(self, term: Terminal, on_close: Callable[[bool], None]) -> None:
        self.term = term
        super().__init__(term.gray20_on_lavender)

        self.current = True

        self.setup_menu()
        self.on_close = on_close

    def set_current_option_and_close(self, option: bool):
        self.current = option
        self.handle_close()

    def setup_menu(self) -> None:
        for option in [True, False]:
            on_item_select = partial(
                self.set_current_option_and_close, option)
            index = super().add_item(str(option), on_item_select)

            if on_item_select == self.current:
                super().set_hover(index)

    def handle_key_escape(self) -> None:
        self.handle_close()

    def handle_char_input(self, char: str) -> None:
        if char.lower() == "q":
            self.handle_close()

    def handle_close(self) -> None:
        self.on_close(self.current)

    @property
    def current_option(self) -> str:
        return str(self.current)
