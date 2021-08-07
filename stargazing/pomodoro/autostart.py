from blessed import Terminal
from functools import partial
from typing import Callable

from pomodoro.pomodoro import PomodoroMenu
from utils.menu import Menu


class AutoStartMenu(Menu):
    """Menu interface to change the auto start option of the pomodoro.

    @param term: Instance of a Blessed terminal.
    @param on_close: Callback function to run when menu is closed.
    @param pomodoro_menu: Instance of a pomodoro menu."""

    def __init__(self, term: Terminal, on_close: Callable[[], None], pomodoro_menu: PomodoroMenu) -> None:
        super().__init__(on_close, term.gray20_on_lavender)

        self.term = term
        self.pomodoro_menu = pomodoro_menu

        self.setup_menu()

    def set_autostart_and_close(self, option: bool) -> None:
        self.pomodoro_menu.autostart = option
        super().handle_close()

    def setup_menu(self) -> None:
        for option in [True, False]:
            on_item_select = partial(
                self.set_autostart_and_close, option)
            index = super().add_item(str(option), on_item_select)

            if option == self.pomodoro_menu.autostart:
                super().set_hover(index)