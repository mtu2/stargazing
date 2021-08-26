from __future__ import annotations
from enum import Enum
from typing import List

import data.database as database
import audio.audio_controller as audio_ac
import audio.audio_player as audio_ap
import pomodoro.timer as pomo_t
import project.project_controller as proj_pc
from utils.format_funcs import format_pomodoro_time

ALARM_START_PATH = "res/alarm_start.mp3"
ALARM_FINISH_PATH = "res/alarm_finish.mp3"


class PomodoroIntervalSettings():
    """Interval settings for the pomodoro timer.

    @param work_secs: Number of seconds for the work interval of the timer.
    @param break_secs: Number of seconds for the break interval of the timer."""

    def __init__(self, work_secs: int, break_secs: int) -> None:
        self.work_secs = work_secs
        self.break_secs = break_secs

    @property
    def name(self) -> str:
        return f"{format_pomodoro_time(self.work_secs, False)} + {format_pomodoro_time(self.break_secs, False)}"

    def __eq__(self, o: PomodoroIntervalSettings) -> bool:
        return self.work_secs == o.work_secs and self.break_secs == o.break_secs

    def __ne__(self, o: PomodoroIntervalSettings) -> bool:
        return not self.__eq__(o)


class PomodoroStatus(Enum):
    INACTIVE = "inactive"
    WORK = "work"
    BREAK = "break"
    PAUSED_WORK = "paused work"
    PAUSED_BREAK = "paused break"
    FINISHED_WORK = "finished work"
    FINISHED_BREAK = "finished break"


class PomodoroController():
    """Pomodoro manager, containing current pomodoro timer, status, autostart option and interval settings.

    @param project_controller: Instance of a project controller.
    @param audio_controller: Instance of an audio controller."""

    def __init__(self, project_controller: proj_pc.ProjectController, audio_controller: audio_ac.AudioController,
                 interval_time: PomodoroIntervalSettings = None, last_autostart=True) -> None:

        self.project_controller = project_controller
        self.audio_controller = audio_controller

        self.interval_settings = interval_time if interval_time else PomodoroIntervalSettings(
            2400, 600)
        self.autostart_setting = last_autostart

        self.timer = pomo_t.Timer(self.interval_settings.work_secs)
        self.status = PomodoroStatus.INACTIVE

    def finish_timer(self, disable_sound=False) -> None:
        if self.status in (PomodoroStatus.WORK, PomodoroStatus.PAUSED_WORK):
            database.insert_pomodoro(
                self.project_controller.current, self.timer)
            self.timer = pomo_t.Timer(self.interval_settings.break_secs)

            if not disable_sound:
                self.__play_alarm_sound(ALARM_FINISH_PATH)

            if self.autostart_setting:
                self.timer.start()
                self.status = PomodoroStatus.BREAK
            else:
                self.status = PomodoroStatus.FINISHED_WORK
        elif self.status in (PomodoroStatus.BREAK, PomodoroStatus.PAUSED_BREAK):
            self.timer = pomo_t.Timer(self.interval_settings.work_secs)

            if self.autostart_setting:
                self.timer.start()
                self.status = PomodoroStatus.WORK

                if not disable_sound:
                    self.__play_alarm_sound(ALARM_START_PATH)
            else:
                self.status = PomodoroStatus.FINISHED_BREAK

    def reset_timer(self) -> None:
        if self.status in (PomodoroStatus.WORK, PomodoroStatus.PAUSED_WORK, PomodoroStatus.FINISHED_WORK):
            database.insert_pomodoro(
                self.project_controller.current, self.timer)
            self.timer = pomo_t.Timer(self.interval_settings.work_secs)

            self.timer.start()
            self.status = PomodoroStatus.WORK
        elif self.status in (PomodoroStatus.BREAK, PomodoroStatus.PAUSED_BREAK, PomodoroStatus.FINISHED_BREAK):
            self.timer = pomo_t.Timer(self.interval_settings.break_secs)

            self.timer.start()
            self.status = PomodoroStatus.BREAK

    def update_timer(self) -> None:

        time_diff, timer_complete = self.timer.update()

        if self.status == PomodoroStatus.WORK:
            self.project_controller.add_todays_total_time(time_diff)
            self.project_controller.current.add_time(time_diff, True)

        if timer_complete:
            self.finish_timer()

    def toggle_start_stop(self) -> None:
        if self.status in (PomodoroStatus.INACTIVE, PomodoroStatus.FINISHED_BREAK):
            self.timer.start()
            self.status = PomodoroStatus.WORK

            self.__play_alarm_sound(ALARM_START_PATH)

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

    def set_interval_settings(self, interval_settings: PomodoroIntervalSettings) -> None:
        self.interval_settings = interval_settings

        # Edit current timer settings without resetting
        if self.status in (PomodoroStatus.INACTIVE, PomodoroStatus.WORK, PomodoroStatus.PAUSED_WORK):
            self.timer.interval = interval_settings.work_secs
        else:
            self.timer.interval = interval_settings.break_secs

    def __play_alarm_sound(self, path) -> None:
        curr_vol = self.audio_controller.get_volume()
        audio_decr = 15

        self.audio_controller.set_volume(max(curr_vol - audio_decr, 0))

        alarm = audio_ap.AudioPlayer(path)
        alarm.set_volume(curr_vol)
        alarm.play()

        # TODO: this needs to be async - wait for the alarm length
        self.audio_controller.set_volume(curr_vol)

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
