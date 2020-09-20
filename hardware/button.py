import radio.player
from radio.audio import Pause
from gpiozero import Button
from time import time, sleep


class RadioButton:
    def _check(self):
        start = time()
        while self._button.is_active:
            sleep(0.01)
            if time() - start > 1:
                break
        else:
            self._player.skip()
            return

        # if pressed long enough, initialize pause
        if not isinstance(self._player.now(), Pause):
            self._player.schedule(Pause())
            self._player.skip()

    def __init__(
        self,
        player: 'radio.player.Player',
        pause: bool,
        skip: bool
    ):
        self._button = Button(2)
        self._player = player
        self._pause = pause
        self._skip = skip
        self._button.when_activated = self._check
