from enum import Enum
from functools import partial
import math
import time
from typing import Callable, Union

from blessed import Terminal
from project import ProjectMenu
from utils.format_funcs import format_pomodoro_time
from utils.logger import logger
from utils.menu import Menu


class PomodoroStatus(Enum):
    INACTIVE = "inactive"
    WORK = "work"
    BREAK = "break"
    PAUSED_WORK = "paused work"
    PAUSED_BREAK = "paused break"
    FINISHED_WORK = "finished work"
    FINISHED_BREAK = "finished break"


class PomodoroSettings():

    def __init__(self, work_secs: int, break_secs: int) -> None:
        self.work_secs = work_secs
        self.break_secs = break_secs

    @property
    def name(self) -> str:
        return f"{format_pomodoro_time(self.work_secs, False)} + {format_pomodoro_time(self.break_secs, False)}"


class PomodoroMenu(Menu):

    def __init__(self, term: Terminal, on_close: Callable[[], None], project_menu: ProjectMenu) -> None:
        super().__init__(on_close, term.gray20_on_lavender)

        self.term = term
        self.project_menu = project_menu

        self.pomo_settings = []
        self.current_settings = None
        self.load_settings()

        self.autostart = True

        self.start_time = None
        self.paused_time = None
        self.elapsed_time = 0
        self.status = PomodoroStatus.INACTIVE

        self.setup_menu()

    def start_timer(self) -> None:
        self.start_time = time.time()
        self.elapsed_time = 0
        self.paused_time = None

    def continue_timer(self) -> None:
        paused_time_elapsed = time.time() - self.paused_time
        self.start_time += paused_time_elapsed
        self.paused_time = None

    def pause_timer(self) -> None:
        self.paused_time = time.time()

    def finish_timer(self):
        if self.status in (PomodoroStatus.WORK, PomodoroStatus.PAUSED_WORK):
            if self.autostart:
                self.start_timer()
                self.status = PomodoroStatus.BREAK
            else:
                self.status = PomodoroStatus.FINISHED_WORK
        elif self.status in (PomodoroStatus.BREAK, PomodoroStatus.PAUSED_BREAK):
            if self.autostart:
                self.start_timer()
                self.status = PomodoroStatus.WORK
            else:
                self.status = PomodoroStatus.FINISHED_BREAK

    def reset_timer(self):
        if self.status in (PomodoroStatus.WORK, PomodoroStatus.PAUSED_WORK, PomodoroStatus.FINISHED_WORK):
            self.start_timer()
            self.status = PomodoroStatus.WORK
        elif self.status in (PomodoroStatus.BREAK, PomodoroStatus.PAUSED_BREAK, PomodoroStatus.FINISHED_BREAK):
            self.start_timer()
            self.status = PomodoroStatus.BREAK

    def update_elapsed_time(self) -> None:
        if not self.start_time:
            return

        old_elapsed_time = self.elapsed_time

        if self.paused_time:
            self.elapsed_time = self.paused_time - self.start_time
        else:
            self.elapsed_time = time.time() - self.start_time

        if old_elapsed_time and self.status == PomodoroStatus.WORK:
            self.project_menu.current.add_time(
                self.elapsed_time - old_elapsed_time)
            if self.elapsed_time < old_elapsed_time:
                logger.debug(f"{self.elapsed_time} {self.old_elapsed_time}")

        if self.status == PomodoroStatus.WORK and self.elapsed_time > self.current_settings.work_secs:
            if self.autostart:
                self.start_timer()
                self.status = PomodoroStatus.BREAK
            else:
                self.status = PomodoroStatus.FINISHED_WORK
        elif self.status == PomodoroStatus.BREAK and self.elapsed_time > self.current_settings.break_secs:
            if self.autostart:
                self.start_timer()
                self.status = PomodoroStatus.WORK
            else:
                self.status = PomodoroStatus.FINISHED_BREAK

    def toggle_start_stop(self) -> None:
        if self.status in (PomodoroStatus.INACTIVE, PomodoroStatus.FINISHED_BREAK):
            self.start_timer()
            self.status = PomodoroStatus.WORK
        elif self.status == PomodoroStatus.PAUSED_WORK:
            self.continue_timer()
            self.status = PomodoroStatus.WORK

        elif self.status == PomodoroStatus.FINISHED_WORK:
            self.start_timer()
            self.status = PomodoroStatus.BREAK
        elif self.status == PomodoroStatus.PAUSED_BREAK:
            self.continue_timer()
            self.status = PomodoroStatus.BREAK

        elif self.status == PomodoroStatus.WORK:
            self.pause_timer()
            self.status = PomodoroStatus.PAUSED_WORK
        elif self.status == PomodoroStatus.BREAK:
            self.pause_timer()
            self.status = PomodoroStatus.PAUSED_BREAK

    def load_settings(self) -> None:
        pomo_settings0 = PomodoroSettings(1200, 600)
        pomo_settings1 = PomodoroSettings(1800, 600)
        pomo_settings2 = PomodoroSettings(2400, 1200)
        pomo_settings3 = PomodoroSettings(2700, 900)
        pomo_settings4 = PomodoroSettings(3000, 600)
        self.pomo_settings = [pomo_settings0, pomo_settings1,
                              pomo_settings2, pomo_settings3, pomo_settings4]
        self.current_settings = pomo_settings0

    def set_current_pomodoro_settings_and_close(self, pomo_settings: PomodoroSettings) -> None:
        self.current_settings = pomo_settings
        super().handle_close()

    def setup_menu(self) -> None:
        for pomo_setting in self.pomo_settings:
            on_item_select = partial(
                self.set_current_pomodoro_settings_and_close, pomo_setting)
            index = super().add_item(pomo_setting.name, on_item_select)

            if pomo_setting == self.current_settings:
                super().set_hover(index)

    @property
    def remaining_time(self) -> str:
        if self.status in (PomodoroStatus.INACTIVE, PomodoroStatus.WORK,
                           PomodoroStatus.PAUSED_WORK, PomodoroStatus.FINISHED_WORK):
            settings_secs = self.current_settings.work_secs
        elif self.status in (PomodoroStatus.BREAK, PomodoroStatus.PAUSED_BREAK,
                             PomodoroStatus.FINISHED_BREAK):
            settings_secs = self.current_settings.break_secs
        elapsed_time_secs = math.floor(self.elapsed_time)
        return format_pomodoro_time(settings_secs - elapsed_time_secs)

    @property
    def current_pomodoro_settings_name(self) -> str:
        return self.current_settings.name

    @property
    def current_status(self) -> str:
        return self.status.value

    @property
    def current_display(self) -> str:
        if self.status in (PomodoroStatus.INACTIVE, PomodoroStatus.FINISHED_BREAK):
            return "START TIMER"
        elif self.status == PomodoroStatus.WORK:
            return f"BREAK IN {self.remaining_time}"
        elif self.status == PomodoroStatus.BREAK:
            return f"POMODORO IN {self.remaining_time}"
        elif self.status == PomodoroStatus.PAUSED_WORK:
            return f"PAUSED [WORK {self.remaining_time}]"
        elif self.status == PomodoroStatus.PAUSED_BREAK:
            return f"PAUSED [BREAK {self.remaining_time}]"
        elif self.status == PomodoroStatus.FINISHED_WORK:
            return "START BREAK"
