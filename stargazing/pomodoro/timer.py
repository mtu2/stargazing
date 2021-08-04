from datetime import datetime
import math
import time
from typing import Union

from utils.format_funcs import format_pomodoro_time


class Timer():

    def __init__(self, secs: int) -> None:
        self.interval = secs
        self.local_start_time = datetime.now()
        self.start_time = None
        self.paused_time = None
        self.elapsed_time = 0

    def start(self) -> None:
        self.start_time = time.time()
        self.elapsed_time = 0
        self.paused_time = None

    def continue_(self) -> None:
        paused_time_elapsed = time.time() - self.paused_time
        self.start_time += paused_time_elapsed
        self.paused_time = None

    def pause(self) -> None:
        self.paused_time = time.time()

    def update(self) -> Union[int, bool]:
        if not self.start_time:
            return 0, False

        old_elapsed_time = self.elapsed_time

        if self.paused_time:
            self.elapsed_time = self.paused_time - self.start_time
        else:
            self.elapsed_time = time.time() - self.start_time

        time_diff = self.elapsed_time - old_elapsed_time if old_elapsed_time else 0

        if self.elapsed_time > self.interval:
            return time_diff, True
        return time_diff, False

    def __str__(self) -> str:
        elapsed_time_secs = math.floor(self.elapsed_time)
        return format_pomodoro_time(self.interval - elapsed_time_secs)
