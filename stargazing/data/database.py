from datetime import datetime, timedelta
from typing import Dict, List
import sqlite3

from pomodoro.timer import Timer
from project.project import Project


conn = sqlite3.connect("data/stargazing.db")  # (":memory:")  #
c = conn.cursor()

time_format = "%d/%m/%Y %H:%M:%S"


def create_tables() -> None:
    c.execute("""CREATE TABLE project (
                    name TEXT NOT NULL PRIMARY KEY
                )""")
    c.execute("""CREATE TABLE pomodoro (
                    project_name TEXT,
                    start_time TEXT,
                    length REAL,
                    FOREIGN KEY(project_name) REFERENCES project(name) ON UPDATE CASCADE
                )""")


def insert_project(project: Project) -> None:
    with conn:
        c.execute("INSERT INTO project VALUES(:name)", {"name": project.name})


def get_all_projects() -> List[Project]:
    c.execute("SELECT * FROM project")
    names = c.fetchall()
    projects = {name[0]: Project(name[0]) for name in names}

    pomos = get_pomodoros()
    current_time = datetime.now()
    current_time.year

    for project_name, start_time, length in pomos:
        start_time = datetime.strptime(start_time, time_format)
        is_current_day = (start_time.year == current_time.year and start_time.month ==
                          current_time.month and start_time.day == current_time.day)
        projects[project_name].add_time(length, is_current_day)

    return list(projects.values())


def insert_pomodoro(project: Project, timer: Timer) -> None:
    with conn:
        start_time = timer.local_start_time.strftime(time_format)
        c.execute("INSERT INTO pomodoro VALUES(:project_name, :start_time, :length)", {
                  "project_name": project.name, "start_time": start_time, "length": timer.elapsed_time})


def get_pomodoros() -> Dict[str, float]:
    c.execute("""SELECT * FROM pomodoro""")
    pomodoros = c.fetchall()
    return pomodoros


if __name__ == "__main__":
    # create_tables()

    test_project1 = Project("fnce30002")
    insert_project(test_project1)

    test_project2 = Project("comp10001")
    insert_project(test_project2)

    test_project3 = Project("info20003")
    insert_project(test_project3)

    test_timer1 = Timer(1800)
    t = datetime.now()

    test_timer1.elapsed_time = 1700
    insert_pomodoro(test_project1, test_timer1)
    insert_pomodoro(test_project1, test_timer1)
    insert_pomodoro(test_project1, test_timer1)
    insert_pomodoro(test_project1, test_timer1)
    insert_pomodoro(test_project1, test_timer1)
    insert_pomodoro(test_project1, test_timer1)
    insert_pomodoro(test_project1, test_timer1)
    test_timer1.local_start_time = datetime.now() - timedelta(days=1)
    insert_pomodoro(test_project1, test_timer1)
    insert_pomodoro(test_project1, test_timer1)
    insert_pomodoro(test_project1, test_timer1)
    insert_pomodoro(test_project1, test_timer1)
    insert_pomodoro(test_project2, test_timer1)
    insert_pomodoro(test_project2, test_timer1)
    insert_pomodoro(test_project2, test_timer1)
    insert_pomodoro(test_project2, test_timer1)
    insert_pomodoro(test_project2, test_timer1)
    insert_pomodoro(test_project2, test_timer1)
    insert_pomodoro(test_project2, test_timer1)
    insert_pomodoro(test_project2, test_timer1)
    insert_pomodoro(test_project2, test_timer1)
    insert_pomodoro(test_project2, test_timer1)
    insert_pomodoro(test_project2, test_timer1)
    insert_pomodoro(test_project2, test_timer1)
    insert_pomodoro(test_project2, test_timer1)
    insert_pomodoro(test_project2, test_timer1)
    insert_pomodoro(test_project2, test_timer1)

    projects = get_all_projects()
    for project in projects:
        print(project)
