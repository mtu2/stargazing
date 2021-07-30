from functools import partial
from typing import Callable

from blessed import Terminal
from utils.format_funcs import format_project_time
from utils.logger import logger
from utils.menu import Menu


class Project():
    """A named project counting total pomodoro time.

    @param name: Display name for the project"""

    def __init__(self, name: str) -> None:
        self.name = name
        self.todays_seconds = 6300
        self.total_seconds = 43980

    @property
    def todays_time(self) -> str:
        return format_project_time(self.todays_seconds)

    @property
    def total_time(self) -> str:
        return format_project_time(self.total_seconds)


class ProjectMenu(Menu):
    """Project menu user interface - handles switching between and creating new projects.

    @param term: Instance of a blessed terminal.
    @param on_close: Callback function to run when the project menu is closed."""

    def __init__(self, term: Terminal, on_close: Callable[[], None]) -> None:
        self.term = term
        super().__init__(term.gray20_on_lavender)

        # NOTE TEMP SETUP TEMP SETUP TEMP SETUP
        project0 = Project("stargazing")
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
        # NOTE TEMP SETUP TEMP SETUP TEMP SETUP

        self.create_new_project_mode = False
        self.create_new_project_mode_index = -1
        self.create_new_project_name = ""

        self.setup_menu()

        # Function to decorate currently hovered item
        self.on_close = on_close

    def set_current_project_and_close(self, project_name):
        self.current = self.projects[project_name]
        self.handle_close()

    def start_create_new_project_mode(self):
        self.create_new_project_mode = True
        super().replace_item(self.create_new_project_mode_index,
                             "> enter project name", self.finish_create_new_project_mode)

    def update_create_new_project_name(self, name):
        self.create_new_project_name = name
        super().replace_item(self.create_new_project_mode_index, "> " + self.create_new_project_name +
                             self.term.lightsteelblue1("█"), self.finish_create_new_project_mode)

    def cancel_create_new_project_mode(self):
        self.create_new_project_name = ""
        self.finish_create_new_project_mode()

    def finish_create_new_project_mode(self):
        self.create_new_project_name = self.create_new_project_name.strip()

        if self.create_new_project_name:
            new_project = Project(self.create_new_project_name)
            self.project_names.append(self.create_new_project_name)
            self.projects[self.create_new_project_name] = new_project

            on_item_select = partial(
                self.set_current_project_and_close, self.create_new_project_name)
            super().add_item(self.create_new_project_name,
                             on_item_select, self.create_new_project_mode_index)

            self.create_new_project_name = ""
            self.create_new_project_mode_index += 1

        self.create_new_project_mode = False
        super().replace_item(self.create_new_project_mode_index, self.term.underline("create new project"),
                             self.start_create_new_project_mode)

    def setup_menu(self) -> None:
        for project_name in self.project_names:
            on_item_select = partial(
                self.set_current_project_and_close, project_name)
            index = super().add_item(project_name, on_item_select)

            if project_name == self.current.name:
                super().set_hover(index)

        index = super().add_item(self.term.underline("create new project"),
                                 self.start_create_new_project_mode)
        self.create_new_project_mode_index = index

    def handle_key_up(self) -> None:
        if self.create_new_project_mode:
            return

        super().handle_key_up()

    def handle_key_down(self) -> None:
        if self.create_new_project_mode:
            return

        super().handle_key_down()

    def handle_key_escape(self) -> None:
        if not self.create_new_project_mode:
            self.handle_close()
            return

        self.cancel_create_new_project_mode()

    def handle_key_backspace(self) -> None:
        if not self.create_new_project_mode or not self.create_new_project_name:
            return

        new_name = self.create_new_project_name[:-1]
        self.update_create_new_project_name(new_name)

    def handle_char_input(self, char: str) -> None:
        if not self.create_new_project_mode and char.lower() == "q":
            self.handle_close()
            return

        new_name = self.create_new_project_name + char
        self.update_create_new_project_name(new_name)

    def handle_close(self) -> None:
        self.on_close()

    @property
    def current_project_name(self) -> str:
        return self.current.name

    @property
    def current_project_todays_time(self) -> str:
        return self.current.todays_time

    @property
    def current_project_total_time(self) -> str:
        return self.current.total_time
