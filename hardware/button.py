import radio.player
from radio.audio import Pause
from gpiozero import Button
from threading import Thread, Event
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

        def button_press_handler(button: RadioButton) -> None:
            if button._pause:
                # schedule pause to avoid further playback
                button._player.schedule(Pause())

            # skip immediately (instant feedback)
            button._player.skip()

            if button._pause and self._skip:
                # wait for button to be released or 1 second to pass
                # wait(timeout=1) returns True iff the event is set, not when it timed out
                if button._event.wait(timeout=1):
                    # the button was released within 1 second of being pressed
                    # assume the user just wanted to skip the current song
                    # thus skip the current pause
                    button._player.skip()

            button._event.clear()

        # reset event (unset)
        self._event.clear()
        # avoid thread blocking (otherwise _released() would wait for _pressed() to finish)
        Thread(target=button_press_handler, args=(self, )).start()

    def _released(self) -> None:
        self._time_limit = now() + 0.5
        self._event.set()
