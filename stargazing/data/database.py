from collections import namedtuple
from datetime import datetime, timedelta
from typing import List, Union

from pomodoro.timer import Timer
from project.project_controller import Project


PomodoroRecord = namedtuple(
    "PomodoroRecord", ["project_name", "start_time", "length"])

TIME_FORMAT = "%d/%m/%Y %H:%M:%S"

PROJECT_DATABASE_PATH = "data/projects.txt"
POMODORO_DATABASE_PATH = "data/pomodoros.txt"

DATABASE_DELIMITER_CHAR = "|"


def insert_project(project: Project) -> bool:
    with open(PROJECT_DATABASE_PATH, "r") as file:
        lines = file.readlines()

    stripped_lines = [line.rstrip("\n") for line in lines]
    if project.name in stripped_lines:
        return False

    with open(PROJECT_DATABASE_PATH, "a") as file:
        file.write(f"{project.name}\n")

    return True


def get_all_projects() -> List[Project]:
    with open(PROJECT_DATABASE_PATH, "r") as file:
        lines = file.readlines()

    stripped_lines = [line.rstrip("\n") for line in lines]
    projects = {name: Project(name) for name in stripped_lines}

    pomo_records = get_all_pomodoros()
    current_time = datetime.now()

    for pomo_record in pomo_records:
        if pomo_record.project_name in projects:
            is_current_day = (pomo_record.start_time.year == current_time.year and pomo_record.start_time.month ==
                              current_time.month and pomo_record.start_time.day == current_time.day)
            projects[pomo_record.project_name].add_time(
                pomo_record.length, is_current_day)

    return list(projects.values())


def get_todays_total_time() -> int:
    pomo_records = get_all_pomodoros()
    current_time = datetime.now()
    todays_total_time = 0

    for pomo_record in pomo_records:
        is_current_day = (pomo_record.start_time.year == current_time.year and pomo_record.start_time.month ==
                          current_time.month and pomo_record.start_time.day == current_time.day)
        if is_current_day:
            todays_total_time += pomo_record.length

    return todays_total_time


def insert_pomodoro(project: Project, timer: Timer) -> None:
    with open(POMODORO_DATABASE_PATH, "a") as file:
        start_time = timer.local_start_time.strftime(TIME_FORMAT)
        file.write(f"{project.name}|{start_time}|{timer.elapsed_time}\n")


def get_all_pomodoros() -> List[PomodoroRecord]:
    with open(POMODORO_DATABASE_PATH, "r") as file:
        lines = file.readlines()

    pomo_records = []
    for line in lines:
        project_name, start_time_str, length_str = line.split(
            DATABASE_DELIMITER_CHAR)

        start_time = datetime.strptime(start_time_str, TIME_FORMAT)
        length = float(length_str)

        pomo_records.append(PomodoroRecord(
            project_name, start_time, float(length)))

    return pomo_records


if __name__ == "__main__":
    print(get_todays_total_time())
