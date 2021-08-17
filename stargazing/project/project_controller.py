from __future__ import annotations
import math
from typing import List, Union

import data.database as database
from utils.format_funcs import format_project_time


class Project():
    """A named project counting total pomodoro time.

    @param name: Display name for the project"""

    def __init__(self, name: str) -> None:
        self.name = name
        self.todays_time = 0
        self.total_time = 0

    def add_time(self, secs: float, today_time=False) -> None:
        self.total_time += secs
        if today_time:
            self.todays_time += secs

    @property
    def formatted_todays_time(self) -> str:
        return format_project_time(math.floor(self.todays_time))

    @property
    def formatted_total_time(self) -> str:
        return format_project_time(math.floor(self.total_time))

    def __str__(self) -> str:
        return f"{self.name} | Today: {self.todays_time}secs, Total: {self.total_time}secs"

    def __eq__(self, o: Project) -> bool:
        return self.name == o.name

    def __ne__(self, o: Project) -> bool:
        return not self.__eq__(o)


class ProjectController():

    def __init__(self, project_name="") -> None:
        self.projects = self.__load_projects()
        self.current = self.projects[0]
        if project_name:
            for project in self.projects:
                if project.name == project_name:
                    self.current = project
                    break
        self.todays_total_time = self.__load_todays_total_time()

    def set_current_project(self, project: Project) -> None:
        self.current = project

    def create_and_insert_new_project(self, project_name: str) -> Union[Project, None]:
        project_name = project_name.strip()

        if not project_name:
            return None

        new_project = Project(project_name)
        insert_successful = database.insert_project(new_project)

        if not insert_successful:
            return None

        self.projects.append(new_project)
        return new_project

    def add_todays_total_time(self, secs: float) -> None:
        self.todays_total_time += secs

    def __load_projects(self) -> List[Project]:
        projects = database.get_all_projects()
        if not projects:
            return [Project("Add a project")]
        return projects

    def __load_todays_total_time(self) -> int:
        return database.get_todays_total_time()

    @property
    def formatted_todays_total_time(self) -> str:
        return format_project_time(math.floor(self.todays_total_time))
