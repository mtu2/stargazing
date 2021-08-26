import concurrent.futures
import re
import urllib.request

import audio.audio_player as audio_ap
import config.config as config
from utils.helper_funcs import silent_stderr, start_daemon_thread


class AudioController():
    """Audio manager, pre-loads the audio players specified in the settings.json and allows audio players to be created and stream via YouTube search

    @param volume: Initial volume level."""

    def __init__(self, volume=100) -> None:
        self.saved_youtube_player_urls = config.get_saved_youtube_player_urls()
        self.loaded_players = {
            name: None for name in self.saved_youtube_player_urls}
        start_daemon_thread(target=self.__load_audio_players)

        self.playing = None
        self.playing_name = "offline"

        self.volume = volume

    def stop(self) -> None:
        if self.playing:
            self.playing.stop()

    def offline(self) -> None:
        self.stop()
        self.playing = None
        self.playing_name = "offline"

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
                                args=[self.saved_youtube_player_urls[loaded_player_name], loaded_player_name])
            # TODO: set self.loaded_players[loaded_player_name] with this player

        # If player has loaded
        else:
            self.playing = self.loaded_players[loaded_player_name]
            self.playing_name = loaded_player_name

            self.playing.set_volume(self.volume)
            self.playing.play()

    def set_youtube_player_from_url(self, youtube_url: str, player_name="") -> str:

        self.stop()

        self.playing_name = "loading audio..."
        self.playing = audio_ap.YoutubeAudioPlayer.safe_create(
            youtube_url, True)

        if self.playing:
            self.playing_name = self.playing.video_titles[0] if not player_name else player_name
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

        self.set_youtube_player_from_url(url)

    def __load_audio_players(self) -> None:
        silent_yt_audio_init = silent_stderr(
            lambda url: audio_ap.YoutubeAudioPlayer.safe_create(url, True))

        with concurrent.futures.ThreadPoolExecutor() as exec:
            futures_to_name = {exec.submit(
                silent_yt_audio_init, url): name for name, url in self.saved_youtube_player_urls.items()}

            for future in concurrent.futures.as_completed(futures_to_name):
                name = futures_to_name[future]
                player = future.result()

                self.loaded_players[name] = player
