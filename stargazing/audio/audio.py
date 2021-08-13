from blessed import Terminal
import concurrent.futures
from functools import partial
from typing import Callable, Dict, List, Union
import re
import threading
import urllib.request

from audio.audio_player import AudioPlayer, YoutubeAudioPlayer
from utils.helper_funcs import silent_stderr, start_daemon_thread
from utils.menu import Menu

YOUTUBE_URLS = {
    "lofi radio": "https://www.youtube.com/watch?v=5qap5aO4i9A&ab_channel=LofiGirl",
    "sunny flower room": "https://www.youtube.com/watch?v=Qh63phquoYk&ab_channel=AmeliaStyle",
    "island in the sun": "https://www.youtube.com/watch?v=erG5rgNYSdk&ab_channel=WeezerVEVO",
    "get got": "https://www.youtube.com/watch?v=HIrKSqb4H4A&ab_channel=DeathGripsVEVO",
    "one more time": "https://www.youtube.com/watch?v=A2VpR8HahKc&ab_channel=DaftPunk",
    "stupid horse": "https://www.youtube.com/watch?v=9YO5ruvFSCU&ab_channel=100gecs"
}

class AudioMenu(Menu):
    """Menu interface to change the auto start option of the pomodoro.

    @param term: Instance of a Blessed terminal.
    @param on_close: Callback function to run when menu is closed."""

    def __init__(self, term: Terminal, on_close: Callable[[], None]) -> None:
        super().__init__(on_close, term.gray20_on_lavender)

        self.term = term
        
        self.loaded_players = {name: None for name in YOUTUBE_URLS}
        start_daemon_thread(target=self.__load_audio_players)
        
        self.playing = None
        self.playing_name = "offline"

        self.volume = 100

        self.search_youtube_mode = False
        self.search_youtube_query = ""

        self.setup_menu()
    
    def stop(self) -> None:
        if self.playing:
            self.playing.stop()

    def set_volume(self, vol: int) -> None:
        self.volume = vol
        if self.playing:
            self.playing.set_volume(vol)

    def get_volume(self) -> int:
        return self.volume

    def set_offline_and_close(self) -> None:
        self.stop()
        self.playing = None
        super().handle_close()

    def set_loaded_player_and_close(self, loaded_player_name: str) -> None:
        """Stops the current player, loads the given player name and closes the menu"""

        self.stop()

        # If player has not loaded (not enough time or error)
        if not self.loaded_players[loaded_player_name]:
            start_daemon_thread(target=self.create_and_set_youtube_player_from_url, 
                                args=[loaded_player_name, YOUTUBE_URLS[loaded_player_name]])
            # TODO: set self.loaded_players[loaded_player_name] with this player
            
        # If player has loaded
        else:
            self.playing = self.loaded_players[loaded_player_name]
            self.playing_name = loaded_player_name

            self.playing.set_volume(self.volume)
            self.playing.play()

        super().handle_close()

    def create_and_set_youtube_player_from_url(self, player_name: str, youtube_url: str) -> str:

        self.stop()

        self.playing_name = "loading audio..."
        self.playing = YoutubeAudioPlayer.safe_create(youtube_url, True)
        
        if self.playing:
            self.playing_name = self.playing.video_titles[0]
            self.playing.set_volume(self.volume)
            self.playing.play()
        else:
            self.playing_name = "error loading audio"

    def create_and_set_youtube_player_from_query(self, search_query: str) -> str:
        self.playing_name = "searching youtube..."

        search = search_query.replace(" ", "+")
        youtube_search = f"https://www.youtube.com/results?search_query={search}"

        html = urllib.request.urlopen(youtube_search)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        url = "https://www.youtube.com/watch?v=" + video_ids[0]
        
        self.create_and_set_youtube_player_from_url(search_query, url)

    def __load_audio_players(self) -> None:
        silent_yt_audio_init = silent_stderr(lambda url: YoutubeAudioPlayer.safe_create(url, True))

        with concurrent.futures.ThreadPoolExecutor() as exec:
            futures_to_name = {exec.submit(silent_yt_audio_init, url): name for name, url in YOUTUBE_URLS.items()}

            for future in concurrent.futures.as_completed(futures_to_name):
                name = futures_to_name[future]
                player = future.result()

                self.loaded_players[name] = player

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
            self.stop()
            start_daemon_thread(target=self.create_and_set_youtube_player_from_query, args=(self.search_youtube_query,))
            super().handle_close()

        self.search_youtube_query = ""
        self.search_youtube_mode = False
        super().replace_item(-1,
                             self.term.underline("search youtube"), self.start_search_youtube_mode)

    def setup_menu(self) -> None:
        super().add_item("offline", self.set_offline_and_close)

        for loaded_player_name in self.loaded_players:
            on_item_select = partial(self.set_loaded_player_and_close, loaded_player_name)
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