from blessed import Terminal
from functools import partial
from typing import Callable

from pomodoro.pomodoro_controller import PomodoroController, PomodoroIntervalSettings
from utils.menu import Menu

INTERVAL_TIMES = [(20 * 60, 10 * 60), (30 * 60, 10 * 60), (40 * 60, 20 * 60),
                  (45 * 60, 15 * 60), (50 * 60, 10 * 60), (60 * 60, 0), (10, 10)]


class IntervalMenu(Menu):
    """Pomodoro manager, containing current pomodoro timer, status, autostart option and settings.
    Contains the menu interface to change the timer settings of the pomodoro.

    @param term: Instance of a Blessed terminal.
    @param on_close: Callback function to run when menu is closed.
    @param project_menu: Instance of a project menu."""

    def __init__(self, term: Terminal, on_close: Callable[[], None], pomo_controller: PomodoroController) -> None:
        super().__init__(on_close, term.gray20_on_lavender)

        self.term = term
        self.pomo_controller = pomo_controller

        self.interval_settings = self.__load_interval_settings()

        self.setup_menu()

    def __load_interval_settings(self) -> None:
        settings = [PomodoroIntervalSettings(
            *interval_time) for interval_time in INTERVAL_TIMES]
        return settings

    def set_interval_settings_and_close(self, interval_settings: PomodoroIntervalSettings) -> None:
        self.pomo_controller.set_interval_settings(interval_settings)
        super().handle_close()

    def setup_menu(self) -> None:
        for interval_setting in self.interval_settings:
            on_item_select = partial(
                self.set_interval_settings_and_close, interval_setting)
            index = super().add_item(interval_setting.name, on_item_select)

            if interval_setting == self.pomo_controller.interval_settings:
                super().set_hover(index)