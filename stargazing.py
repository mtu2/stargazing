import math
import time

from blessed import Terminal
from menu import Menu
from project import ProjectManager
import utils.print_tools as pt


class Stargazing():

    def __init__(self, term: Terminal) -> None:
        self.term = term
        self.projects = ProjectManager(term)

        self.pomodoro = "50 + 10"
        self.auto_start = True

        self.playing = "rain.ogg"
        self.volume = 100

        self.start_time = None

        self.menu = None
        self.submenu = None

        self.open_menu()
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

                inp = self.term.inkey(10)

                if inp.lower() == "q":
                    break

                if inp.name == "KEY_UP":
                    self.focused_menu.handle_hover_up()
                elif inp.name == "KEY_DOWN":
                    self.focused_menu.handle_hover_down()
                elif inp.name == "KEY_ENTER":
                    self.focused_menu.handle_select()

    def print_menu(self) -> None:
        lines = self.menu.get_print_strings()
        x, y = 6, 3

        pt.print_lines_xy(self.term, x, y, lines, max_width=30)

    def print_submenu(self) -> None:
        if self.submenu is None:
            return

        lines = self.submenu.get_print_strings()
        x, y = 40, 3

        pt.print_lines_xy(self.term, x, y, lines)

    def print_pomodoro(self) -> None:
        if self.start_time == None:
            text = "START POMODORO"
        else:
            text = f"{math.floor(time.time() - self.start_time)}s"

        x, y = round(self.term.width / 2 - len(text) / 2), self.term.height - 4

        # if row_num == self.hover_row:
        #     text = self.term.gray20_on_white(text)
        pt.print_xy(self.term, x, y, text)

    # HELPER FUNCTIONS

    def print_logo(self) -> None:
        pt.print_xy(self.term, 0, 0,
                    self.term.gray20_on_white(self.term.bold(' stargazing ')))

    def print_gazing(self) -> None:
        with open("gazing.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            dec_lines = [self.term.aliceblue(line) for line in lines]

            x, y = 1, self.term.height - len(lines)

            pt.print_lines_xy(self.term, x, y, dec_lines)

    def print_stars(self) -> None:
        with open("stars.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            dec_lines = [self.term.aliceblue(line) for line in lines]

            x, y = self.term.width // 2, 3

            pt.print_lines_xy(self.term, x, y, dec_lines)

    def close_submenu(self) -> None:
        self.open_menu()
        self.print_stars()

        self.submenu = None
        self.focused_menu = self.menu

    def open_submenu_projects(self) -> None:
        self.submenu = self.projects.create_menu(
            self.close_submenu, self.term.gray20_on_white)
        self.focused_menu = self.submenu

    def open_menu(self) -> Menu:
        menu = Menu(hover_dec=self.term.gray20_on_white)

        menu.add_item(
            f"{self.term.bold('project')}: {self.term.lightcoral(self.projects.current.name)}", self.open_submenu_projects)
        menu.add_item(
            f"{self.term.bold('todays time')}: {self.term.lightskyblue3(self.projects.current.todays_time)}")
        menu.add_item(
            f"{self.term.bold('total time')}: {self.term.lightskyblue3(self.projects.current.total_time)}")

        menu.add_divider()

        menu.add_item(f"{self.term.bold('pomodoro')}: {self.pomodoro}")
        menu.add_item(f"{self.term.bold('auto-start')}: {self.auto_start}")

        menu.add_divider()

        menu.add_item(f"{self.term.bold('playing')}: {self.playing}")
        menu.add_item(f"{self.term.bold('volume')}: {self.volume}")

        self.menu = menu
