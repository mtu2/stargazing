from blessed import Terminal
import time
import sys

from pomodoro.autostart import AutoStartMenu
from pomodoro.pomodoro import PomodoroMenu
from project.project_menu import ProjectMenu
from pomodoro.status import StatusMenu

from utils.logger import logger
from utils.menu import Menu
import utils.print_funcs as pf
from utils.stars import StarsGenerator


GAZING_PATH = "res/gazing.txt"


class Stargazing(Menu):

    def __init__(self) -> None:
        self.term = Terminal()

        super().__init__(on_close=self.handle_close, hover_dec=self.term.gray20_on_lavender)

        self.project_menu = ProjectMenu(self.term, self.close_project_submenu)
        self.pomodoro_menu = PomodoroMenu(
            self.term, self.close_pomodoro_submenu, self.project_menu)
        self.autostart_menu = AutoStartMenu(
            self.term, self.close_autostart_submenu, self.pomodoro_menu)
        self.status_menu = StatusMenu(
            self.term, self.close_status_submenu, self.pomodoro_menu)

        self.playing = "rain.ogg"
        self.volume = 100

        self.start_time = None

        self.menu = None
        self.submenu = None
        self.focused_menu = self

        self.running = False

        self.stars_generator = StarsGenerator()
        self.setup_menu()

    def start(self) -> None:
        self.running = True

        with self.term.fullscreen(), self.term.cbreak(), self.term.hidden_cursor():
            print(self.term.home + self.term.clear)

            self.print_logo()
            self.print_gazing()
            self.print_stars()

            while self.running:
                self.print_stars()
                self.print_menu()
                self.print_submenu()

                sys.stdout.flush()

                inp = self.term.inkey(0.3)

                self.pomodoro_menu.update_timer()

                super().replace_item(1,
                                     f"{self.term.bold('todays time')}: {self.term.lightskyblue3(self.project_menu.current.todays_time)}")
                super().replace_item(2,
                                     f"{self.term.bold('total time')}: {self.term.lightskyblue3(self.project_menu.current.total_time)}")

                super().replace_item(5,
                                     f"{self.term.bold('status')}: {self.pomodoro_menu.current_status}", self.open_status_submenu)
                super().replace_item(8,
                                     f"{self.pomodoro_menu.current_display}", self.toggle_pomodoro_display)

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

    def handle_close(self) -> None:
        self.pomodoro_menu.finish_timer()
        self.running = False

    def open_project_submenu(self) -> None:
        self.submenu = self.project_menu
        self.focused_menu = self.submenu

    def close_project_submenu(self) -> None:

        self.print_stars()

        super().replace_item(0,
                             f"{self.term.bold('project')}: {self.term.lightcoral(self.project_menu.current.name)}", self.open_project_submenu)
        super().replace_item(1,
                             f"{self.term.bold('todays time')}: {self.term.lightskyblue3(self.project_menu.current.todays_time)}")
        super().replace_item(2,
                             f"{self.term.bold('total time')}: {self.term.lightskyblue3(self.project_menu.current.total_time)}")

        self.submenu = None
        self.focused_menu = self

    def open_pomodoro_submenu(self) -> None:
        self.submenu = self.pomodoro_menu
        self.focused_menu = self.submenu

    def close_pomodoro_submenu(self) -> None:

        self.print_stars()

        self.pomodoro_menu.update_timer()
        super().replace_item(
            3, f"{self.term.bold('pomodoro')}: {self.pomodoro_menu.current_pomodoro_settings_name}", self.open_pomodoro_submenu)
        super().replace_item(8,
                             f"{self.pomodoro_menu.current_display}", self.toggle_pomodoro_display)

        self.submenu = None
        self.focused_menu = self

    def open_autostart_submenu(self) -> None:
        self.submenu = self.autostart_menu
        self.focused_menu = self.submenu

    def close_autostart_submenu(self) -> None:

        self.print_stars()

        super().replace_item(
            4, f"{self.term.bold('auto-start')}: {self.pomodoro_menu.autostart}", self.open_autostart_submenu)

        self.submenu = None
        self.focused_menu = self

    def open_status_submenu(self) -> None:
        self.submenu = self.status_menu
        self.focused_menu = self.submenu

    def close_status_submenu(self) -> None:

        self.print_stars()

        self.pomodoro_menu.update_timer()

        super().replace_item(5,
                             f"{self.term.bold('status')}: {self.pomodoro_menu.current_status}", self.open_status_submenu)
        super().replace_item(8,
                             f"{self.pomodoro_menu.current_display}", self.toggle_pomodoro_display)
        self.submenu = None
        self.focused_menu = self

    def toggle_pomodoro_display(self) -> None:
        self.pomodoro_menu.toggle_start_stop()
        self.pomodoro_menu.update_timer()
        super().replace_item(5,
                             f"{self.term.bold('status')}: {self.pomodoro_menu.current_status}", self.open_status_submenu)
        super().replace_item(8,
                             f"{self.pomodoro_menu.current_display}", self.toggle_pomodoro_display)

    def setup_menu(self) -> Menu:
        super().add_item(
            f"{self.term.bold('project')}: {self.term.lightcoral(self.project_menu.current.name)}", self.open_project_submenu)
        super().add_item(
            f"{self.term.bold('todays time')}: {self.term.lightskyblue3(self.project_menu.current.todays_time)}")
        super().add_item(
            f"{self.term.bold('total time')}: {self.term.lightskyblue3(self.project_menu.current.total_time)}")

        super().add_divider()

        super().add_item(
            f"{self.term.bold('pomodoro')}: {self.pomodoro_menu.current_pomodoro_settings_name}", self.open_pomodoro_submenu)
        super().add_item(
            f"{self.term.bold('auto-start')}: {self.pomodoro_menu.autostart}", self.open_autostart_submenu)
        super().add_item(
            f"{self.term.bold('status')}: {self.pomodoro_menu.current_status}", self.open_status_submenu)

        super().add_divider()

        super().add_item(f"{self.term.bold('playing')}: {self.playing}")
        super().add_item(f"{self.term.bold('volume')}: {self.volume}")

        super().add_divider()

        super().add_item(f"{self.pomodoro_menu.current_display}",
                         self.toggle_pomodoro_display)

    # ========================================================
    # Terminal printing methods
    # ========================================================

    def print_menu(self) -> None:
        lines = super().get_print_strings()
        menu_lines, pomo_line = lines[:-1], lines[-1]

        mx, my = 6, 3
        pf.print_lines_xy(self.term, mx, my, menu_lines,
                          flush=False, max_width=30)

        px, py = round(self.term.width / 2), self.term.height - 4
        pf.print_xy(self.term, px, py, pomo_line,
                    flush=False, max_width=19, center=True)

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
        elif self.submenu is self.status_menu:
            max_width = 12

        pf.print_lines_xy(self.term, x, y, lines,
                          flush=False, max_width=max_width)

    def print_logo(self) -> None:
        pf.print_xy(self.term, 0, 0,
                    self.term.gray20_on_white(self.term.bold(' stargazing ')))

    def print_gazing(self) -> None:
        with open(GAZING_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            dec_lines = [self.term.aliceblue(line) for line in lines]

            x, y = 1, self.term.height - len(lines)

            pf.print_lines_xy(self.term, x, y, dec_lines)

    def print_stars(self) -> None:
        stars = self.stars_generator.get_stars()
        dec_lines = [self.term.aliceblue(line) for line in stars]

        x, y = 2, 1

        pf.print_lines_xy(self.term, x, y, dec_lines, flush=False)
