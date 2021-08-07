from blessed import Terminal
from enum import Enum
from functools import partial
from typing import Callable

import data.database as database
from pomodoro.timer import Timer
from project.project_menu import ProjectMenu
from utils.format_funcs import format_pomodoro_time
from utils.logger import logger
from utils.menu import Menu


POMO_SETTING_TIMES = [(1200, 600), (1800, 600),
                      (2400, 1200), (2700, 900), (3000, 600), (3600, 0)]


class PomodoroStatus(Enum):
    INACTIVE = "inactive"
    WORK = "work"
    BREAK = "break"
    PAUSED_WORK = "paused work"
    PAUSED_BREAK = "paused break"
    FINISHED_WORK = "finished work"
    FINISHED_BREAK = "finished break"


class PomodoroSettings():
    """Timer settings for the pomodoro timer.

    @param work_secs: Number of seconds for the work interval of the timer.
    @param break_secs: Number of seconds for the break interval of the timer."""

    def __init__(self, work_secs: int, break_secs: int) -> None:
        self.work_secs = work_secs
        self.break_secs = break_secs

    @property
    def name(self) -> str:
        return f"{format_pomodoro_time(self.work_secs, False)} + {format_pomodoro_time(self.break_secs, False)}"


class PomodoroMenu(Menu):
    """Pomodoro manager, containing current pomodoro timer, status, autostart option and settings.
    Contains the menu interface to change the timer settings of the pomodoro.

    @param term: Instance of a Blessed terminal.
    @param on_close: Callback function to run when menu is closed.
    @param project_menu: Instance of a project menu."""

    def __init__(self, term: Terminal, on_close: Callable[[], None], project_menu: ProjectMenu) -> None:
        super().__init__(on_close, term.gray20_on_lavender)

        self.term = term
        self.project_menu = project_menu

        self.pomo_settings = []
        self.settings = None
        self.load_settings()

        self.autostart = True

        self.timer = Timer(self.settings.work_secs)
        self.status = PomodoroStatus.INACTIVE

        self.setup_menu()

    def finish_timer(self):
        if self.status in (PomodoroStatus.WORK, PomodoroStatus.PAUSED_WORK):
            database.insert_pomodoro(self.project_menu.current, self.timer)
            self.timer = Timer(self.settings.break_secs)

            if self.autostart:
                self.timer.start()
                self.status = PomodoroStatus.BREAK
            else:
                self.status = PomodoroStatus.FINISHED_WORK
        elif self.status in (PomodoroStatus.BREAK, PomodoroStatus.PAUSED_BREAK):
            self.timer = Timer(self.settings.work_secs)

            if self.autostart:
                self.timer.start()
                self.status = PomodoroStatus.WORK
            else:
                self.status = PomodoroStatus.FINISHED_BREAK

    def reset_timer(self):
        if self.status in (PomodoroStatus.WORK, PomodoroStatus.PAUSED_WORK, PomodoroStatus.FINISHED_WORK):
            database.insert_pomodoro(self.project_menu.current, self.timer)
            self.timer = Timer(self.settings.work_secs)

            self.timer.start()
            self.status = PomodoroStatus.WORK
        elif self.status in (PomodoroStatus.BREAK, PomodoroStatus.PAUSED_BREAK, PomodoroStatus.FINISHED_BREAK):
            self.timer = Timer(self.settings.break_secs)

            self.timer.start()
            self.status = PomodoroStatus.BREAK

    def update_timer(self) -> None:

        time_diff, timer_complete = self.timer.update()

        if self.status == PomodoroStatus.WORK:
            self.project_menu.current.add_time(time_diff, True)

        if timer_complete:
            self.finish_timer()

    def toggle_start_stop(self) -> None:
        if self.status in (PomodoroStatus.INACTIVE, PomodoroStatus.FINISHED_BREAK):
            self.timer.start()
            self.status = PomodoroStatus.WORK
        elif self.status == PomodoroStatus.PAUSED_WORK:
            self.timer.continue_()
            self.status = PomodoroStatus.WORK

        elif self.status == PomodoroStatus.FINISHED_WORK:
            self.timer.start()
            self.status = PomodoroStatus.BREAK
        elif self.status == PomodoroStatus.PAUSED_BREAK:
            self.timer.continue_()
            self.status = PomodoroStatus.BREAK

        elif self.status == PomodoroStatus.WORK:
            self.timer.pause()
            self.status = PomodoroStatus.PAUSED_WORK
        elif self.status == PomodoroStatus.BREAK:
            self.timer.pause()
            self.status = PomodoroStatus.PAUSED_BREAK

    def load_settings(self) -> None:
        for pomo_setting_time in POMO_SETTING_TIMES:
            pomo_settings = PomodoroSettings(*pomo_setting_time)
            self.pomo_settings.append(pomo_settings)

            if not self.settings:
                self.settings = pomo_settings

    def set_current_settings_and_close(self, pomo_settings: PomodoroSettings) -> None:
        self.settings = pomo_settings

        # Edit current timer settings without reseting
        if self.status in (PomodoroStatus.INACTIVE, PomodoroStatus.WORK, PomodoroStatus.PAUSED_WORK):
            self.timer.interval = pomo_settings.work_secs
        else:
            self.timer.interval = pomo_settings.break_secs

        super().handle_close()

    def setup_menu(self) -> None:
        for pomo_setting in self.pomo_settings:
            on_item_select = partial(
                self.set_current_settings_and_close, pomo_setting)
            index = super().add_item(pomo_setting.name, on_item_select)

            if pomo_setting == self.settings:
                super().set_hover(index)

    @property
    def timer_display(self) -> str:
        if self.status in (PomodoroStatus.INACTIVE, PomodoroStatus.FINISHED_BREAK):
            return "START TIMER"
        elif self.status == PomodoroStatus.WORK:
            return f"BREAK IN {self.timer.remaining_time}"
        elif self.status == PomodoroStatus.BREAK:
            return f"POMODORO IN {self.timer.remaining_time}"
        elif self.status == PomodoroStatus.PAUSED_WORK:
            return f"PAUSED [WORK {self.timer.remaining_time}]"
        elif self.status == PomodoroStatus.PAUSED_BREAK:
            return f"PAUSED [BREAK {self.timer.remaining_time}]"
        elif self.status == PomodoroStatus.FINISHED_WORK:
            return "START BREAK"
