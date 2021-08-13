import concurrent.futures
import re
import urllib.request

from audio.audio_player import AudioPlayer, YoutubeAudioPlayer
from utils.helper_funcs import silent_stderr, start_daemon_thread

YOUTUBE_URLS = {
    "lofi radio": "https://www.youtube.com/watch?v=5qap5aO4i9A&ab_channel=LofiGirl",
    "sunny flower room": "https://www.youtube.com/watch?v=Qh63phquoYk&ab_channel=AmeliaStyle",
    "island in the sun": "https://www.youtube.com/watch?v=erG5rgNYSdk&ab_channel=WeezerVEVO",
    "get got": "https://www.youtube.com/watch?v=HIrKSqb4H4A&ab_channel=DeathGripsVEVO",
    "one more time": "https://www.youtube.com/watch?v=A2VpR8HahKc&ab_channel=DaftPunk",
    "stupid horse": "https://www.youtube.com/watch?v=9YO5ruvFSCU&ab_channel=100gecs"
}


class AudioController():
    def __init__(self) -> None:
        self.loaded_players = {name: None for name in YOUTUBE_URLS}
        start_daemon_thread(target=self.__load_audio_players)

        self.playing = None
        self.playing_name = "offline"

        self.volume = 100

    def stop(self) -> None:
        if self.playing:
            self.playing.stop()

    def offline(self) -> None:
        self.stop()
        self.playing = None

    def set_volume(self, vol: int) -> None:
        self.volume = vol
        if self.playing:
            self.playing.set_volume(vol)

    def get_volume(self) -> int:
        return self.volume

    def set_loaded_player(self, loaded_player_name: str) -> None:
        """Stops the current player, loads the given player name and closes the menu"""

        self.stop()

        # If player has not loaded (not enough time or error)
        if not self.loaded_players[loaded_player_name]:
            start_daemon_thread(target=self.set_youtube_player_from_url,
                                args=[loaded_player_name, YOUTUBE_URLS[loaded_player_name]])
            # TODO: set self.loaded_players[loaded_player_name] with this player

        # If player has loaded
        else:
            self.playing = self.loaded_players[loaded_player_name]
            self.playing_name = loaded_player_name

            self.playing.set_volume(self.volume)
            self.playing.play()

    def set_youtube_player_from_url(self, player_name: str, youtube_url: str) -> str:

        self.stop()

        self.playing_name = "loading audio..."
        self.playing = YoutubeAudioPlayer.safe_create(youtube_url, True)

        if self.playing:
            self.playing_name = self.playing.video_titles[0]
            self.playing.set_volume(self.volume)
            self.playing.play()
        else:
            self.playing_name = "error loading audio"

    def set_youtube_player_from_query(self, search_query: str) -> str:

        self.stop()

        self.playing_name = "searching youtube..."

        search = search_query.replace(" ", "+")
        youtube_search = f"https://www.youtube.com/results?search_query={search}"

        html = urllib.request.urlopen(youtube_search)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        url = "https://www.youtube.com/watch?v=" + video_ids[0]

        self.set_youtube_player_from_url(search_query, url)

    def __load_audio_players(self) -> None:
        silent_yt_audio_init = silent_stderr(
            lambda url: YoutubeAudioPlayer.safe_create(url, True))

        with concurrent.futures.ThreadPoolExecutor() as exec:
            futures_to_name = {exec.submit(
                silent_yt_audio_init, url): name for name, url in YOUTUBE_URLS.items()}

            for future in concurrent.futures.as_completed(futures_to_name):
                name = futures_to_name[future]
                player = future.result()

                self.loaded_players[name] = player
