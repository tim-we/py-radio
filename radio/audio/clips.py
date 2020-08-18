from abc import ABC, abstractmethod
import audio2numpy
import sounddevice
import os.path
from threading import Thread, Event
import time
import numpy as np
from queue import Queue
from typing import Optional


class Clip(ABC):
    def __init__(self, name: str):
        self._aborted: bool = False
        self.user_req: bool = False
        self.name: str = name
        self._completed = Event()

    @abstractmethod
    def start(self) -> None:
        pass

    def stop(self) -> None:
        if not self._completed.is_set():
            self._aborted = True
            self._completed.set()

    def __str__(self) -> str:
        return self.name


class MP3Clip(Clip):
    _dev = sounddevice
    _loading_queue: Queue = Queue()
    loading_thread: Optional[Thread] = None

    def __init__(self, file: str):
        super().__init__(os.path.basename(file))
        self.file = file
        self._loaded = Event()
        self._data: Optional[np.array] = None
        self._sr: int

        # MP3 files get preloaded (read & decoded)
        if MP3Clip.loading_thread is None:
            MP3Clip.loading_thread = Thread(target=MP3Clip._load, daemon=True)
            MP3Clip.loading_thread.start()
        MP3Clip._loading_queue.put(self)

    def start(self) -> None:
        # wait until MP3 file is loaded
        if not self._loaded.is_set():
            self._loaded.wait()

        duration = len(self._data) / self._sr  # type: ignore

        # play and block thread until completed (or aborted)
        MP3Clip._dev.play(self._data, self._sr)
        self._completed.wait(duration)
        self._completed.set()

    def stop(self) -> None:
        MP3Clip._dev.stop()
        super().stop()
        time.sleep(0.1)

    @staticmethod
    def _load() -> None:
        while True:
            # (pre)load next MP3 clip
            clip = MP3Clip._loading_queue.get()
            data, sr = audio2numpy.open_audio(clip.file)
            # store data
            clip._data = data
            clip._sr = sr
            # send signal that the clip is loaded as .start() might be waiting
            clip._loaded.set()
            time.sleep(0.1)


class Pause(Clip):
    def __init__(self, duration: float = 600):
        super().__init__("{}s pause".format(duration))
        self.duration = duration

    def start(self) -> None:
        self._completed.wait(self.duration)
        self._completed.set()
