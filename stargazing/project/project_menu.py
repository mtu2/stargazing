from blessed import Terminal
from functools import partial
from typing import Callable

import data.database as database
from project.project import Project
from utils.logger import logger
from utils.menu import Menu


class ProjectMenu(Menu):
    """Project menu user interface - handles switching between and creating new projects.

    @param term: Instance of a blessed terminal.
    @param on_close: Callback function to run when the project menu is closed."""

    def __init__(self, term: Terminal, on_close: Callable[[], None]) -> None:
        super().__init__(on_close, term.gray20_on_lavender)

        self.term = term

        self.projects = []
        self.current = None
        self.load_projects()

        self.create_new_project_mode = False
        self.create_new_project_name = ""

        self.setup_menu()

    def set_current_project_and_close(self, project):
        self.current = project
        super().handle_close()

    def start_create_new_project_mode(self):
        self.create_new_project_mode = True
        super().replace_item(-1,
                             "> enter project name", self.finish_create_new_project_mode)

    def update_create_new_project_name(self, name):
        self.create_new_project_name = name
        super().replace_item(-1, "> " + self.create_new_project_name +
                             self.term.lightsteelblue1("█"), self.finish_create_new_project_mode)

    def cancel_create_new_project_mode(self):
        self.create_new_project_name = ""
        self.finish_create_new_project_mode()

    def finish_create_new_project_mode(self):
        self.create_new_project_name = self.create_new_project_name.strip()

        if self.create_new_project_name:
            new_project = Project(self.create_new_project_name)
            insert_successful = database.insert_project(new_project)

            if insert_successful:
                self.projects.append(new_project)

                on_item_select = partial(
                    self.set_current_project_and_close, new_project)
                super().add_item(new_project.name,
                                 on_item_select, -1)

        self.create_new_project_name = ""
        self.create_new_project_mode = False
        super().replace_item(-1, self.term.underline("create new project"),
                             self.start_create_new_project_mode)

    def load_projects(self) -> None:
        self.projects = database.get_all_projects()

        if not self.projects:
            self.projects = [Project("Default")]

        self.current = self.projects[0]

    def setup_menu(self) -> None:
        for project in self.projects:
            on_item_select = partial(
                self.set_current_project_and_close, project)
            index = super().add_item(project.name, on_item_select)

            if project == self.current:
                super().set_hover(index)

        super().add_item(self.term.underline("create new project"),
                                 self.start_create_new_project_mode)

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
            super().handle_key_escape()
            return

        self.cancel_create_new_project_mode()

    def handle_key_backspace(self) -> None:
        if not self.create_new_project_mode or not self.create_new_project_name:
            return

        new_name = self.create_new_project_name[:-1]
        self.update_create_new_project_name(new_name)

    def handle_char_input(self, char: str) -> None:
        if not self.create_new_project_mode:
            super().handle_char_input(char)
            return

        if char == database.DATABASE_DELIMITER_CHAR:
            return

        new_name = self.create_new_project_name + char
        self.update_create_new_project_name(new_name)
