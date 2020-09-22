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
        self._button = Button(2)
        self._player = player
        self._pause = pause
        self._skip = skip
        self._event = Event()
        self._time_limit: float = 0
        self._button.when_activated = self._pressed
        self._button.when_deactivated = self._released

    def _pressed(self) -> None:
        if self._time_limit > now():
            return
        self._event = Event()
        self._event.wait(timeout=1)
        if self._button.is_active and self._pause:
            self._player.schedule(Pause())
            self._player.skip()
        else:
            if self._skip:
                self._player.skip()

    def _released(self) -> None:
        self._time_limit = now() + 0.5
        self._event.set()
