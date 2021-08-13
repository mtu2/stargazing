from blessed import Terminal
from functools import partial
import sys

from audio.audio_controller import AudioController
from audio.player_menu import PlayerMenu
from audio.volume_menu import VolumeMenu

from pomodoro.autostart_menu import AutoStartMenu
from pomodoro.interval_menu import IntervalMenu
from pomodoro.pomodoro_controller import PomodoroController
from pomodoro.status_menu import StatusMenu

from project.project_controller import ProjectController
from project.project_menu import ProjectMenu

from utils.logger import logger
from utils.menu import Menu
import utils.print_funcs as print_funcs
from utils.stars import StarsGenerator


GAZING_PATH = "res/gazing.txt"


class Stargazing(Menu):

    def __init__(self) -> None:

        self.term = Terminal()

        super().__init__(on_close=self.handle_close, hover_dec=self.term.gray20_on_lavender)

        self.audio_controller = AudioController()
        self.project_controller = ProjectController()
        self.pomodoro_controller = PomodoroController(
            self.project_controller, self.audio_controller)

        self.project_menu = ProjectMenu(
            self.term, partial(self.close_submenu, (0, 1, 2)), self.project_controller)

        self.interval_menu = IntervalMenu(
            self.term, partial(self.close_submenu, (3, 8), True), self.pomodoro_controller)
        self.autostart_menu = AutoStartMenu(
            self.term, partial(self.close_submenu, (4,)), self.pomodoro_controller)
        self.status_menu = StatusMenu(
            self.term, partial(self.close_submenu, (5, 8), True), self.pomodoro_controller)

        self.player_menu = PlayerMenu(
            self.term, partial(self.close_submenu, (6,)), self.audio_controller)
        self.volume_menu = VolumeMenu(
            self.term, partial(self.close_submenu, (7,)), self.audio_controller)

        self.menu = None
        self.submenu = None
        self.focused_menu = self

        self.running = False
        self.refresh_speed = 0.3

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

                inp = self.term.inkey(self.refresh_speed)

                self.pomodoro_controller.update_timer()

                self.refresh_menu_items((1, 2, 5, 8))

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

        print("Exiting stargazing...")

    def handle_close(self) -> None:
        self.pomodoro_controller.finish_timer(disable_sound=True)
        self.running = False

    def open_submenu(self, submenu: Menu) -> None:
        self.submenu = submenu
        self.focused_menu = self.submenu

    def close_submenu(self, refresh_indexes, update_timer=False) -> None:
        self.print_stars()

        if update_timer:
            self.pomodoro_controller.update_timer()

        self.refresh_menu_items(refresh_indexes)

        self.submenu = None
        self.focused_menu = self

    def refresh_menu_items(self, indexes) -> None:
        for index in indexes:
            if index == 0:
                super().replace_item(0,
                                     f"{self.term.bold('project')}: {self.term.lightcoral(self.project_controller.current.name)}", partial(self.open_submenu, self.project_menu))
            elif index == 1:
                super().replace_item(1,
                                     f"{self.term.bold('todays time')}: {self.term.lightskyblue3(self.project_controller.current.formatted_todays_time  + ' | ' + self.project_controller.formatted_todays_total_time)}")
            elif index == 2:
                super().replace_item(2,
                                     f"{self.term.bold('total time')}: {self.term.lightskyblue3(self.project_controller.current.formatted_total_time)}")
            elif index == 3:
                super().replace_item(3,
                                     f"{self.term.bold('pomodoro')}: {self.pomodoro_controller.interval_settings.name}", partial(self.open_submenu, self.interval_menu))
            elif index == 4:
                super().replace_item(4,
                                     f"{self.term.bold('auto-start')}: {self.pomodoro_controller.autostart_setting}", partial(self.open_submenu, self.autostart_menu))
            elif index == 5:
                super().replace_item(5,
                                     f"{self.term.bold('status')}: {self.pomodoro_controller.status.value}", partial(self.open_submenu, self.status_menu))
            elif index == 6:
                super().replace_item(6,
                                     f"{self.term.bold('playing')}: {self.audio_controller.playing_name}", partial(self.open_submenu, self.player_menu))
            elif index == 7:
                super().replace_item(7,
                                     f"{self.term.bold('volume')}: {self.audio_controller.volume}", partial(self.open_submenu, self.volume_menu))
            elif index == 8:
                super().replace_item(8,
                                     f"{self.pomodoro_controller.timer_display}", self.toggle_pomodoro_display)

    def toggle_pomodoro_display(self) -> None:
        self.pomodoro_controller.toggle_start_stop()
        self.pomodoro_controller.update_timer()

        self.refresh_menu_items((5, 8))

    def setup_menu(self) -> Menu:

        super().add_item(
            f"{self.term.bold('project')}: {self.term.lightcoral(self.project_controller.current.name)}", partial(self.open_submenu, self.project_menu))
        super().add_item(
            f"{self.term.bold('todays time')}: {self.term.lightskyblue3(self.project_controller.current.formatted_todays_time + ' | ' + self.project_controller.formatted_todays_total_time)}")
        super().add_item(
            f"{self.term.bold('total time')}: {self.term.lightskyblue3(self.project_controller.current.formatted_total_time)}")

        super().add_divider()

        super().add_item(
            f"{self.term.bold('pomodoro')}: {self.pomodoro_controller.interval_settings.name}", partial(self.open_submenu, self.interval_menu))
        super().add_item(
            f"{self.term.bold('auto-start')}: {self.pomodoro_controller.autostart_setting}", partial(self.open_submenu, self.autostart_menu))
        super().add_item(
            f"{self.term.bold('status')}: {self.pomodoro_controller.status.value}", partial(self.open_submenu, self.status_menu))

        super().add_divider()

        super().add_item(
            f"{self.term.bold('playing')}: {self.audio_controller.playing_name}", partial(self.open_submenu, self.player_menu))
        super().add_item(
            f"{self.term.bold('volume')}: {self.audio_controller.volume}", partial(self.open_submenu, self.volume_menu))

        super().add_divider()

        super().add_item(f"{self.pomodoro_controller.timer_display}",
                         self.toggle_pomodoro_display)

    # ========================================================
    # Terminal printing methods
    # ========================================================

    def print_menu(self) -> None:
        lines = super().get_print_strings()
        menu_lines, pomo_line = lines[:-1], lines[-1]

        mx, my = 6, 3
        print_funcs.print_lines_xy(self.term, mx, my, menu_lines,
                                   flush=False, max_width=30)

        px, py = round(self.term.width / 2), self.term.height - 4
        print_funcs.print_xy(self.term, px, py, pomo_line,
                             flush=False, max_width=19, center=True)

    def print_submenu(self) -> None:
        if self.submenu is None:
            return

        lines = self.submenu.get_print_strings()
        x, y = 40, 3

        if self.submenu is self.project_menu:
            max_width = 30
        elif self.submenu is self.interval_menu:
            max_width = 7
        elif self.submenu is self.autostart_menu:
            max_width = 5
        elif self.submenu is self.status_menu:
            max_width = 12
        elif self.submenu is self.player_menu:
            max_width = 10
        elif self.submenu is self.volume_menu:
            max_width = 3

        print_funcs.print_lines_xy(self.term, x, y, lines,
                                   flush=False, max_width=max_width)

    def print_logo(self) -> None:
        print_funcs.print_xy(self.term, 0, 0,
                             self.term.gray20_on_white(self.term.bold(' stargazing ')))

    def print_gazing(self) -> None:
        with open(GAZING_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            dec_lines = [self.term.aliceblue(line) for line in lines]

            x, y = 1, self.term.height - len(lines)

            print_funcs.print_lines_xy(self.term, x, y, dec_lines)

    def print_stars(self) -> None:
        stars = self.stars_generator.get_stars()
        dec_lines = [self.term.aliceblue(line) for line in stars]

        x, y = 2, 1

        print_funcs.print_lines_xy(self.term, x, y, dec_lines, flush=False)
