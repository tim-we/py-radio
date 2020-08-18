from abc import ABC, abstractmethod
import audio2numpy
import sounddevice
import os.path
from threading import Thread, Event
import time
import numpy as np
from typing import Optional


class Clip(ABC):
    def __init__(self, name: str):
        self._aborted: bool = False
        self.user_req: bool = False
        self.name: str = name
        self._abort = Event()

    @abstractmethod
    def start(self) -> None:
        pass

    def stop(self) -> None:
        if not self._abort.is_set():
            self._aborted = True
            self._abort.set()

    def __str__(self) -> str:
        return self.name


class MP3Clip(Clip):
    _dev = sounddevice

    def __init__(self, file: str):
        super().__init__(os.path.basename(file))
        self.file = file
        self._loaded = Event()
        self._data: Optional[np.array] = None
        Thread(target=self._load, daemon=True).start()

    def start(self) -> None:
        while not self._loaded.is_set():
            self._loaded.wait(0.25)
        duration = len(self._data) / self._sr  # type: ignore
        MP3Clip._dev.play(self._data, self._sr)
        self._abort.wait(duration)

    def stop(self) -> None:
        MP3Clip._dev.stop()
        super().stop()
        time.sleep(0.1)

    def _load(self) -> None:
        data, sr = audio2numpy.open_audio(self.file)
        self._data = data
        self._sr = sr
        self._loaded.set()


class Pause(Clip):
    def __init__(self, duration: float = 600):
        super().__init__("{}s pause".format(duration))
        self.duration = duration

    def start(self) -> None:
        self._abort.wait(self.duration)
