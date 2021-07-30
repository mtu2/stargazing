
import math
import time
from blessed import Terminal

from autostart import AutoStartMenu
from pomodoro import PomodoroMenu
from project import ProjectMenu
from utils.logger import logger
import utils.print_funcs as pf
from utils.menu import Menu


class Stargazing(Menu):

    def __init__(self, term: Terminal) -> None:
        self.term = term
        super().__init__(self.term.gray20_on_white)

        self.project_menu = ProjectMenu(term, self.close_project_submenu)
        self.pomodoro_menu = PomodoroMenu(term, self.close_pomodoro_submenu)
        self.autostart_menu = AutoStartMenu(term, self.close_autostart_submenu)

        self.playing = "rain.ogg"
        self.volume = 100

        self.start_time = None

        self.menu = None
        self.submenu = None

        self.setup_menu()
        self.focused_menu = self

        self.running = False

    def start(self) -> None:
        self.running = True

        with self.term.fullscreen(), self.term.cbreak(), self.term.hidden_cursor():
            print(self.term.home + self.term.clear)

            self.print_logo()
            self.print_gazing()
            self.print_stars()

            while self.running:
                self.print_menu()
                self.print_submenu()
                self.print_pomodoro()

                inp = self.term.inkey(10)

                if inp.is_sequence and inp.name == "KEY_UP":
                    self.focused_menu.handle_key_up()
                elif inp.is_sequence and inp.name == "KEY_DOWN":
                    self.focused_menu.handle_key_down()
                elif inp.is_sequence and inp.name == "KEY_ENTER":
                    self.focused_menu.handle_key_enter()
                elif inp.is_sequence and inp.name == "KEY_ESCAPE":
                    self.focused_menu.handle_key_escape()
                elif inp.is_sequence and inp.name == "KEY_BACKSPACE":
                    self.focused_menu.handle_key_backspace()
                elif inp and not inp.is_sequence:
                    self.focused_menu.handle_char_input(inp)

    def handle_char_input(self, char: str) -> None:
        if char.lower() == "q":
            self.handle_close()
            return

    def handle_close(self) -> None:
        # save to sqlite...
        self.running = False

    def open_project_submenu(self) -> None:
        self.submenu = self.project_menu
        self.focused_menu = self.submenu

    def close_project_submenu(self) -> None:
        self.print_stars()

        super().replace_item(0,
                             f"{self.term.bold('project')}: {self.term.lightcoral(self.project_menu.current_project_name)}", self.open_project_submenu)
        super().replace_item(1,
                             f"{self.term.bold('todays time')}: {self.term.lightskyblue3(self.project_menu.current_project_todays_time)}")
        super().replace_item(2,
                             f"{self.term.bold('total time')}: {self.term.lightskyblue3(self.project_menu.current_project_total_time)}")

        self.submenu = None
        self.focused_menu = self

    def open_pomodoro_submenu(self) -> None:
        self.submenu = self.pomodoro_menu
        self.focused_menu = self.submenu

    def close_pomodoro_submenu(self) -> None:
        self.print_stars()

        super().replace_item(
            3, f"{self.term.bold('pomodoro')}: {self.pomodoro_menu.current_pomodoro_settings_name}", self.open_pomodoro_submenu)

        self.submenu = None
        self.focused_menu = self

    def open_autostart_submenu(self) -> None:
        self.submenu = self.autostart_menu
        self.focused_menu = self.submenu

    def close_autostart_submenu(self, updated_option: bool) -> None:
        self.print_stars()

        super().replace_item(
            4, f"{self.term.bold('auto-start')}: {self.autostart_menu.current_option}", self.open_autostart_submenu)

        self.pomodoro_menu.set_autostart(updated_option)

        self.submenu = None
        self.focused_menu = self

    def setup_menu(self) -> Menu:
        super().add_item(
            f"{self.term.bold('project')}: {self.term.lightcoral(self.project_menu.current_project_name)}", self.open_project_submenu)
        super().add_item(
            f"{self.term.bold('todays time')}: {self.term.lightskyblue3(self.project_menu.current_project_todays_time)}")
        super().add_item(
            f"{self.term.bold('total time')}: {self.term.lightskyblue3(self.project_menu.current_project_total_time)}")

        super().add_divider()

        super().add_item(
            f"{self.term.bold('pomodoro')}: {self.pomodoro_menu.current_pomodoro_settings_name}", self.open_pomodoro_submenu)
        super().add_item(
            f"{self.term.bold('auto-start')}: {self.autostart_menu.current_option}", self.open_autostart_submenu)

        super().add_divider()

        super().add_item(f"{self.term.bold('playing')}: {self.playing}")
        super().add_item(f"{self.term.bold('volume')}: {self.volume}")

        super().add_item(f"{self.pomodoro_menu.status}",
                         self.pomodoro_menu.toggle_start_stop)

    # ========================================================
    # Terminal printing methods
    # ========================================================

    def print_menu(self) -> None:
        lines = super().get_print_strings()
        menu_lines, pomo_line = lines[:-1], lines[-1]

        mx, my = 6, 3
        pf.print_lines_xy(self.term, mx, my, menu_lines, max_width=30)

        px, py = round(self.term.width / 2 - self.term.length(pomo_line) /
                       2), self.term.height - 4
        pf.print_xy(self.term, px, py, pomo_line)

    def print_submenu(self) -> None:
        if self.submenu is None:
            return

        lines = self.submenu.get_print_strings()
        x, y = 40, 3

        if self.submenu is self.project_menu:
            max_width = 30
        elif self.submenu is self.pomodoro_menu:
            max_width = 7
        elif self.submenu is self.autostart_menu:
            max_width = 5

        pf.print_lines_xy(self.term, x, y, lines, max_width)

    def print_pomodoro(self) -> None:
        if self.start_time == None:
            text = "START POMODORO"
        else:
            text = f"{math.floor(time.time() - self.start_time)}s"

    def print_logo(self) -> None:
        pf.print_xy(self.term, 0, 0,
                    self.term.gray20_on_white(self.term.bold(' stargazing ')))

    def print_gazing(self) -> None:
        with open("res/gazing.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            dec_lines = [self.term.aliceblue(line) for line in lines]

            x, y = 1, self.term.height - len(lines)

            pf.print_lines_xy(self.term, x, y, dec_lines)

    def print_stars(self) -> None:
        with open("res/stars.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            dec_lines = [self.term.aliceblue(line) for line in lines]

            x, y = 2, 1  # self.term.width // 2, 3

            pf.print_lines_xy(self.term, x, y, dec_lines)
