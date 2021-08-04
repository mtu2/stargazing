from blessed import Terminal
from typing import Callable

from pomodoro.pomodoro import PomodoroMenu
from utils.menu import Menu


class StatusMenu(Menu):
    """Menu interface to manually change the status of the pomodoro.

    @param term: Instance of a Blessed terminal.
    @param on_close: Callback function to run when menu is closed.
    @param pomodoro_menu: Instance of a pomodoro menu."""

    def __init__(self, term: Terminal, on_close: Callable[[], None], pomodoro_menu: PomodoroMenu) -> None:
        super().__init__(on_close, term.gray20_on_lavender)

        self.term = term
        self.pomodoro_menu = pomodoro_menu

        self.setup_menu()

    def finish_timer_and_close(self) -> None:
        self.pomodoro_menu.finish_timer()
        super().handle_close()

    def reset_timer_and_close(self) -> None:
        self.pomodoro_menu.reset_timer()
        super().handle_close

    def setup_menu(self) -> None:
        super().add_item("finish timer", self.finish_timer_and_close)
        super().add_item("reset timer", self.reset_timer_and_close)
