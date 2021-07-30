from functools import partial
import time
from typing import Callable

from blessed import Terminal
from utils.format_funcs import format_pomodoro_time
from utils.logger import logger
from utils.menu import Menu


class PomodoroSettings():

    def __init__(self, work_secs: int, rest_secs: int) -> None:
        self.work_secs = work_secs
        self.rest_secs = rest_secs

    @property
    def name(self) -> str:
        return f"{format_pomodoro_time(self.work_secs, False)} + {format_pomodoro_time(self.rest_secs, False)}"


class PomodoroMenu(Menu):

    def __init__(self, term: Terminal, on_close: Callable[[], None]) -> None:
        self.term = term
        super().__init__(term.gray20_on_lavender)

        # NOTE TEMP SETUP TEMP SETUP TEMP SETUP
        pomo_settings0 = PomodoroSettings(1200, 600)
        pomo_settings1 = PomodoroSettings(1800, 600)
        pomo_settings2 = PomodoroSettings(2400, 1200)
        pomo_settings3 = PomodoroSettings(2700, 900)
        pomo_settings4 = PomodoroSettings(3000, 600)

        self.pomo_settings_names = [pomo_settings0.name,
                                    pomo_settings1.name, pomo_settings2.name, pomo_settings3.name, pomo_settings4.name]
        self.pomo_settings = {
            pomo_settings0.name: pomo_settings0,
            pomo_settings1.name: pomo_settings1,
            pomo_settings2.name: pomo_settings2,
            pomo_settings3.name: pomo_settings3,
            pomo_settings4.name: pomo_settings4
        }

        self.current = pomo_settings0
        # NOTE TEMP SETUP TEMP SETUP TEMP SETUP

        self.autostart = True

        self.setup_menu()
        self.on_close = on_close

        self.status = "start"
        self.start_time = None

    def toggle_start_stop(self) -> None:
        pass

    def set_autostart(self, option: bool) -> None:
        self.autostart = option

    def set_current_pomodoro_settings_and_close(self, pomo_settings_name):
        self.current = self.pomo_settings[pomo_settings_name]
        self.handle_close()

    def setup_menu(self) -> None:
        for pomo_setttings_name in self.pomo_settings_names:
            on_item_select = partial(
                self.set_current_pomodoro_settings_and_close, pomo_setttings_name)
            index = super().add_item(pomo_setttings_name, on_item_select)

            if pomo_setttings_name == self.current.name:
                super().set_hover(index)

    def handle_key_escape(self) -> None:
        self.handle_close()

    def handle_char_input(self, char: str) -> None:
        if char.lower() == "q":
            self.handle_close()

    def handle_close(self) -> None:
        self.on_close()

    @property
    def current_pomodoro_settings_name(self) -> str:
        return self.current.name
