import math
import time

from blessed import Terminal
from menu import Menu
from project import ProjectManager


class Stargazing():

    def __init__(self, term: Terminal) -> None:
        self.term = term
        self.projects = ProjectManager(term)

        self.pomodoro = "50 + 10"
        self.auto_start = True

        self.playing = "rain.ogg"
        self.volume = 100

        self.start_time = None

        self.menu = self.create_menu()
        self.submenu = None
        self.focused_menu = self.menu

    def start(self) -> None:
        with self.term.fullscreen(), self.term.cbreak(), self.term.hidden_cursor():
            print(self.term.home + self.term.clear)

            self.print_logo()
            self.print_gazing()
            self.print_stars()

            while True:
                self.print_menu()
                self.print_submenu()
                self.print_pomodoro()

                inp = self.term.inkey(timeout=0.05)

                if inp.lower() == "1":
                    break

                if inp.name == "KEY_UP":
                    self.focused_menu.hover_up()
                elif inp.name == "KEY_DOWN":
                    self.focused_menu.hover_down()
                elif inp.name == "KEY_ENTER":
                    self.focused_menu.select()

    def print_menu(self) -> None:
        rows = self.menu.get_print_rows()
        x, y = 6, 3

        for i, row in enumerate(rows):
            print(self.term.move_xy(x, y + i) + row, end="", flush=True)

    def print_submenu(self) -> None:
        if self.submenu is None:
            return

        rows = self.submenu.get_print_rows()
        x, y = 36, 3

        for i, row in enumerate(rows):
            print(self.term.move_xy(x, y + i) + row, end="", flush=True)

    def print_pomodoro(self) -> None:
        if self.start_time == None:
            text = "START POMODORO"
        else:
            text = f"{math.floor(time.time() - self.start_time)}s"

        x, y = round(self.term.width / 2 - len(text) / 2), self.term.height - 4

        # if row_num == self.hover_row:
        #     text = self.term.gray20_on_white(text)
        print(self.term.move_xy(x, y) + text, end="", flush=True)

    # HELPER FUNCTIONS

    def print_logo(self) -> None:
        print(self.term.move_xy(0, 0) +
              self.term.gray20_on_white(self.term.bold(' stargazing ')), end="", flush=True)

    def print_gazing(self) -> None:
        with open("gazing.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            x, y = 1, self.term.height - len(lines)

            for i, line in enumerate(lines):
                print(self.term.move_xy(x, y + i) +
                      self.term.aliceblue(line), end="", flush=True)

    def print_stars(self) -> None:
        with open("stars.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            x, y = self.term.width // 2, 3

            for i, line in enumerate(lines):
                print(self.term.move_xy(x, y + i) +
                      self.term.aliceblue(line), end="", flush=True)

    def create_project_submenu(self) -> None:
        self.submenu = self.projects.create_menu()
        self.focused_menu = self.submenu

    def create_menu(self) -> Menu:
        menu = Menu(self.term.gray20_on_white)

        menu.add_item(
            f"{self.term.bold('project')}: {self.term.lightcoral(self.projects.current.name)}", self.create_project_submenu)
        menu.add_item(
            f"{self.term.bold('todays time')}: {self.term.lightskyblue3(self.projects.current.todays_time)}")
        menu.add_item(
            f"{self.term.bold('total time')}: {self.term.lightskyblue3(self.projects.current.total_time)}")

        menu.add_blank_row()

        menu.add_item(f"{self.term.bold('pomodoro')}: {self.pomodoro}")
        menu.add_item(f"{self.term.bold('auto-start')}: {self.auto_start}")

        menu.add_blank_row()

        menu.add_item(f"{self.term.bold('playing')}: {self.playing}")
        menu.add_item(f"{self.term.bold('volume')}: {self.volume}")

        return menu
