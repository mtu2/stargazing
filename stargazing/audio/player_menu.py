from blessed import Terminal
from functools import partial
from typing import Callable

import stargazing.audio.audio_controller as audio_ac
from stargazing.utils.helper_funcs import start_daemon_thread
from stargazing.utils.menu import Menu


class PlayerMenu(Menu):
    """Menu interface to change the current player in the audio controller.

    @param term: Instance of a Blessed terminal.
    @param on_close: Callback function to run when menu is closed.
    @param audio_controller: Instance of an audio controller."""

    def __init__(self, term: Terminal, on_close: Callable[[], None], audio_controller: audio_ac.AudioController) -> None:
        super().__init__(on_close, term.gray20_on_lavender)

        self.term = term
        self.audio_controller = audio_controller

        self.search_youtube_mode = False
        self.search_youtube_query = ""

        self.setup_menu()

    def set_offline_and_close(self) -> None:
        super().handle_close()
        self.audio_controller.offline()

    def set_loaded_player_and_close(self, loaded_player_name: str) -> None:
        """Stops the current player, loads the given player name and closes the menu"""
        super().handle_close()
        self.audio_controller.set_loaded_player(loaded_player_name)

    def set_youtube_player_from_url_and_close(self, player_name: str, youtube_url: str) -> str:
        super().handle_close()
        self.audio_controller.set_youtube_player_from_url(
            player_name, youtube_url)

    def set_youtube_player_from_query_and_close(self, search_query: str) -> str:
        super().handle_close()
        self.audio_controller.set_youtube_player_from_query(search_query)

    def start_search_youtube_mode(self):
        self.search_youtube_mode = True
        super().replace_item(-1,
                             "> search youtube", self.finish_search_youtube_mode)

    def update_search_youtube_query(self, query):
        self.search_youtube_query = query
        super().replace_item(-1, "> " + self.search_youtube_query +
                             self.term.lightsteelblue1("█"), self.finish_search_youtube_mode)

    def cancel_search_youtube_mode(self):
        self.search_youtube_query = ""
        self.finish_search_youtube_mode()

    def finish_search_youtube_mode(self):
        self.search_youtube_query = self.search_youtube_query.strip()

        if self.search_youtube_query:
            start_daemon_thread(target=self.set_youtube_player_from_query_and_close, args=(
                self.search_youtube_query,))

        self.search_youtube_query = ""
        self.search_youtube_mode = False
        super().replace_item(-1,
                             self.term.underline("search youtube"), self.start_search_youtube_mode)

    def setup_menu(self) -> None:
        super().add_item("offline", self.set_offline_and_close)

        for loaded_player_name in self.audio_controller.loaded_players:
            on_item_select = partial(
                self.set_loaded_player_and_close, loaded_player_name)
            super().add_item(loaded_player_name, on_item_select)

        super().add_item(self.term.underline("search youtube"),
                         self.start_search_youtube_mode)
        super().set_hover(0)

    def handle_key_up(self) -> None:
        if self.search_youtube_mode:
            return

        super().handle_key_up()

    def handle_key_down(self) -> None:
        if self.search_youtube_mode:
            return

        super().handle_key_down()

    def handle_key_escape(self) -> None:
        if not self.search_youtube_mode:
            super().handle_key_escape()
            return

        self.cancel_search_youtube_mode()

    def handle_key_backspace(self) -> None:
        if not self.search_youtube_mode or not self.search_youtube_query:
            return

        new_query = self.search_youtube_query[:-1]
        self.update_search_youtube_query(new_query)

    def handle_char_input(self, char: str) -> None:
        if not self.search_youtube_mode:
            super().handle_char_input(char)
            return

        new_query = self.search_youtube_query + char
        self.update_search_youtube_query(new_query)
