from __future__ import annotations # allow typing of own class inside its class
from typing import Iterable, Union

import pafy
import pafy.backend_youtube_dl # prevent lazy importing
import vlc

from utils.helper_funcs import check_iterable
from utils.logger import logger

class AudioPlayer():

    def __init__(self, sources: Union[str, Iterable[str]], loop=False):
        self.vlc_instance = vlc.Instance()
        self.vlc_instance.log_unset()

        self.player = self.vlc_instance.media_list_player_new()
        self.media_list = self.create_media_list(check_iterable(sources))

        if loop:
            self.player.set_playback_mode(vlc.PlaybackMode.loop)
        
        self.player.set_media_list(self.media_list)

    def create_media_list(self, sources: Iterable[str]) -> vlc.MediaList:
        media_list = self.vlc_instance.media_list_new()
        
        for source in sources:
            media = self.vlc_instance.media_new(source)
            media.add_option(":no-video")
            media_list.add_media(media)

        return media_list

    def play(self) -> None:
        self.player.play()

    def pause(self) -> None:
        self.player.pause()

    def stop(self) -> None:
        self.player.stop()

    def set_volume(self, vol: int) -> None:
        self.player.get_media_player().audio_set_volume(vol)

    def get_volume(self) -> int:
        return self.player.get_media_player().audio_get_volume()


class YoutubeAudioPlayer(AudioPlayer):
    
    def __init__(self, youtube_urls: Union[str, Iterable[str]], loop=False) -> None:
        playurls = []

        for youtube_url in check_iterable(youtube_urls):
            video = pafy.new(youtube_url)
            best = video.getbest()
            playurl = best.url
            playurls.append(playurl)
            
        super().__init__(playurls, loop)     

    @staticmethod
    def safe_create(youtube_urls: Union[str, Iterable[str]], loop=False) -> Union[None, YoutubeAudioPlayer]:
        try:
            yt_audio_player = YoutubeAudioPlayer(youtube_urls, loop)
            return yt_audio_player
        except Exception as e:
            logger.error(f"Failed to create YoutubeAudioPlayer with inputs: {youtube_urls}, {loop}. Full message: {e}")
            return None