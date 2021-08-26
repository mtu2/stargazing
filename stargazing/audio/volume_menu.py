from blessed import Terminal
from functools import partial
from typing import Callable

import stargazing.audio.audio_controller as audio_ac
from stargazing.utils.menu import Menu


class VolumeMenu(Menu):
    """Menu interface to change the volume of the audio controller.

    @param term: Instance of a Blessed terminal.
    @param on_close: Callback function to run when menu is closed.
    @param audio_controller: Instance of an audio controller."""

    def __init__(self, term: Terminal, on_close: Callable[[], None], audio_controller: audio_ac.AudioController) -> None:
        super().__init__(on_close, term.gray20_on_lavender)

        self.term = term
        self.audio_controller = audio_controller

        self.setup_menu()

    def set_volume_and_close(self, option: bool) -> None:
        self.audio_controller.set_volume(option)
        super().handle_close()

    def setup_menu(self) -> None:
        for option in range(100, -1, -10):
            on_item_select = partial(
                self.set_volume_and_close, option)
            index = super().add_item(str(option), on_item_select)

            if option == self.audio_controller.volume:
                super().set_hover(index)
