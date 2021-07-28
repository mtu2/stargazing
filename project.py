from functools import partial

from blessed import Terminal
from menu import Menu


def format_time_str(seconds: int, show_seconds=False) -> str:
    s = seconds
    h = s // 3600
    m = (s - h * 3600) // 60

    if show_seconds:
        s -= h * 3600 + m * 60
        return f"{h}h {m}m {s}s"
    return f"{h}h {m}m"


class Project():

    def __init__(self, name: str) -> None:
        self.name = name
        self.todays_seconds = 6300
        self.total_seconds = 43980

    @property
    def todays_time(self) -> str:
        return format_time_str(self.todays_seconds)

    @property
    def total_time(self) -> str:
        return format_time_str(self.total_seconds)


class ProjectManager():

    def __init__(self, term: Terminal) -> None:
        self.term = term

        project0 = Project("stargazing ")
        project1 = Project("pomodoro")
        project2 = Project("comp10001 foc")
        project3 = Project("work & internships")

        self.project_names = [project0.name,
                              project1.name, project2.name, project3.name]
        self.projects = {
            project0.name: project0,
            project1.name: project1,
            project2.name: project2,
            project3.name: project3
        }

        self.current = project0

    def set_current_project(self, project_name):
        self.current = self.projects[project_name]

    def create_menu(self, on_close, hover_dec) -> Menu:
        menu = Menu(hover_dec)

        def set_and_close(project_name):
            self.set_current_project(project_name)
            on_close()

        for project_name in self.project_names:
            on_item_select = partial(set_and_close, project_name)
            index = menu.add_item(project_name, on_item_select)

            if project_name == self.current.name:
                menu.set_hover(index)

        menu.add_item(self.term.underline("create new project"))

        return menu
