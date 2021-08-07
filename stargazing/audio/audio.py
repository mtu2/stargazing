from blessed import Terminal
from functools import partial
from typing import Callable

from utils.menu import Menu


class AudioMenu(Menu):
    """Menu interface to change the auto start option of the pomodoro.

    @param term: Instance of a Blessed terminal.
    @param on_close: Callback function to run when menu is closed."""

    def __init__(self, term: Terminal, on_close: Callable[[], None]) -> None:
        super().__init__(on_close, term.gray20_on_lavender)

        self.term = term

        self.playing = "rain.ogg"
        self.volume = 100

        self.setup_menu()

    def set_playing_and_close(self, option: str) -> None:
        self.playing = option
        super().handle_close()

    def setup_menu(self) -> None:
        for option in ["rain.ogg", "fire.ogg", "lofi radio"]:
            on_item_select = partial(
                self.set_playing_and_close, option)
            index = super().add_item(option, on_item_select)

            if option == self.playing:
                super().set_hover(index)
