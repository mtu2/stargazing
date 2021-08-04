import math

from utils.format_funcs import format_project_time


class Project():
    """A named project counting total pomodoro time.

    @param name: Display name for the project"""

    def __init__(self, name: str) -> None:
        self.name = name
        self.todays_seconds = 0
        self.total_seconds = 0

    def add_time(self, secs: float, today_time=False) -> None:
        self.total_seconds += secs
        if today_time:
            self.todays_seconds += secs

    @property
    def todays_time(self) -> str:
        return format_project_time(math.floor(self.todays_seconds))

    @property
    def total_time(self) -> str:
        return format_project_time(math.floor(self.total_seconds))

    def __str__(self) -> str:
        return f"{self.name} | Today: {self.todays_seconds}secs, Total: {self.total_seconds}secs"
