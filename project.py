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

        self.current = Project("stargazing")
        self.projects = [self.current, Project("pomodoro"), Project("comp10001 foc")]

    def create_menu(self) -> Menu:
        menu = Menu(self.term.gray20_on_white)

        for i, project in enumerate(self.projects):
            menu.add_item(project.name)

            if project is self.current:
                menu.set_hover(i)

        return menu
