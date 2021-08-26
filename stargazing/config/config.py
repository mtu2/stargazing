from __future__ import annotations
from typing import List, Tuple
import ujson

import pomodoro.pomodoro_controller as pomo_pc

CONFIG_FILE_PATH = "config/settings.json"


def get_saved_youtube_player_urls() -> List[str]:
    with open(CONFIG_FILE_PATH) as file:
        data = ujson.load(file)
        return data["saved_youtube_player_urls"]


def get_interval_times() -> List[List[int]]:
    with open(CONFIG_FILE_PATH) as file:
        data = ujson.load(file)
        return data["interval_times"]


def get_last_session_data() -> Tuple[str, pomo_pc.PomodoroIntervalSettings, bool, int]:
    with open(CONFIG_FILE_PATH) as file:
        data = ujson.load(file)
        return (data["last_project_name"], pomo_pc.PomodoroIntervalSettings(*data["last_interval_time"]),
                data["last_autostart"], data["last_volume"])


def update_last_session_data(project_name: str, interval_settings: pomo_pc.PomodoroIntervalSettings,
                             autostart: bool, volume: int) -> None:
    with open(CONFIG_FILE_PATH, 'r+') as file:
        data = ujson.load(file)

        data["last_project_name"] = project_name
        data["last_interval_time"] = [
            interval_settings.work_secs, interval_settings.break_secs]
        data["last_autostart"] = autostart
        data["last_volume"] = volume

        file.seek(0)
        ujson.dump(data, file, indent=4)
        file.truncate()
