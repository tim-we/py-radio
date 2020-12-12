import radio.player
from radio.audio import Pause
from gpiozero import Button
from threading import Event
from time import time as now


class RadioButton:
    def __init__(
        self,
        player: 'radio.player.Player',
        pause: bool,
        skip: bool
    ):
        # https://gpiozero.readthedocs.io/en/stable/recipes.html#button
        self._button = Button(2)
        self._player = player
        self._pause = pause
        self._skip = skip
        self._event = Event()
        self._time_limit: float = 0
        if skip or pause:
            self._button.when_activated = self._pressed
            self._button.when_deactivated = self._released

    def _pressed(self) -> None:
        # avoid accidental button spam
        if self._time_limit > now():
            return

        # reset event (unset)
        self._event.clear()

        if self._pause:
            # schedule pause to avoid further playback
            self._player.schedule(Pause())

        # skip immediately (instant feedback)
        self._player.skip()

        if self._pause and self._skip:
            # wait for button to be released or 1 second to pass
            self._event.wait(timeout=1)
            if not self._button.is_active:
                # the button was released within 1 second of being pressed
                # assume the user just wanted to skip the current song
                # thus skip the current pause
                self._player.skip()

    def _released(self) -> None:
        self._time_limit = now() + 0.5
        self._event.set()
