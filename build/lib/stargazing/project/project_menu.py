from blessed import Terminal
from functools import partial
from typing import Callable

import data.database as database
import project.project_controller as proj_pc
from utils.menu import Menu


class ProjectMenu(Menu):
    """Menu interface to create and switch between projects.

    @param term: Instance of a Blessed terminal.
    @param on_close: Callback function to run when menu is closed.
    @param pomodoro_controller: Instance of a project controller."""

    def __init__(self, term: Terminal, on_close: Callable[[], None], project_controller: proj_pc.ProjectController) -> None:
        super().__init__(on_close, term.gray20_on_lavender)

        self.term = term
        self.project_controller = project_controller

        self.create_new_project_mode = False
        self.create_new_project_name = ""

        self.setup_menu()

    def set_current_project_and_close(self, project: proj_pc.Project) -> None:
        self.project_controller.set_current_project(project)
        super().handle_close()

    def start_create_new_project_mode(self) -> None:
        self.create_new_project_mode = True
        super().replace_item(-1,
                             "> enter project name", self.finish_create_new_project_mode)

    def update_create_new_project_name(self, name: str) -> None:
        self.create_new_project_name = name
        super().replace_item(-1, "> " + self.create_new_project_name +
                             self.term.lightsteelblue1("█"), self.finish_create_new_project_mode)

    def cancel_create_new_project_mode(self) -> None:
        self.create_new_project_name = ""
        self.finish_create_new_project_mode()

    def finish_create_new_project_mode(self) -> None:
        self.create_new_project_name = self.create_new_project_name.strip()

        created_project = self.project_controller.create_and_insert_new_project(
            self.create_new_project_name)

        if created_project:
            on_item_select = partial(
                self.set_current_project_and_close, created_project)
            super().add_item(created_project.name, on_item_select, -1)

        self.create_new_project_name = ""
        self.create_new_project_mode = False
        super().replace_item(-1, self.term.underline("create new project"),
                             self.start_create_new_project_mode)

    def setup_menu(self) -> None:
        for project in self.project_controller.projects:
            on_item_select = partial(
                self.set_current_project_and_close, project)
            index = super().add_item(project.name, on_item_select)

            if project == self.project_controller.current:
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
