from blessed import Terminal
from functools import partial
from typing import Callable

import stargazing.config.config as config
import stargazing.pomodoro.pomodoro_controller as pomo_pc
from stargazing.utils.menu import Menu


class IntervalMenu(Menu):
    """Menu interface to change the interval settings of the pomodoro timer.

    @param term: Instance of a Blessed terminal.
    @param on_close: Callback function to run when menu is closed.
    @param pomo_controller: Instance of a pomodoro controller."""

    def __init__(self, term: Terminal, on_close: Callable[[], None], pomo_controller: pomo_pc.PomodoroController) -> None:
        super().__init__(on_close, term.gray20_on_lavender)

        self.term = term
        self.pomo_controller = pomo_controller

        self.interval_settings = self.__load_interval_settings()

        self.setup_menu()

    def __load_interval_settings(self) -> None:
        interval_times = config.get_interval_times()
        settings = [pomo_pc.PomodoroIntervalSettings(
            *interval_time) for interval_time in interval_times]
        return settings

    def set_interval_settings_and_close(self, interval_settings: pomo_pc.PomodoroIntervalSettings) -> None:
        self.pomo_controller.set_interval_settings(interval_settings)
        super().handle_close()

    def setup_menu(self) -> None:
        for interval_setting in self.interval_settings:
            on_item_select = partial(
                self.set_interval_settings_and_close, interval_setting)
            index = super().add_item(interval_setting.name, on_item_select)

            if interval_setting == self.pomo_controller.interval_settings:
                super().set_hover(index)
