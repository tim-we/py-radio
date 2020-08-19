from abc import ABC
from radio.audio.reader import ffmpeg_load_audio
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
        self.hide: bool = False
        self.started: Optional[time.struct_time] = None

    def start(self) -> None:
        self.started = time.localtime()

    def stop(self) -> None:
        if not self._completed.is_set():
            self._aborted = True
            self._completed.set()

    def show_in_history(self) -> bool:
        return (not self.hide) and (self.started is not None)

    def __str__(self) -> str:
        if self._aborted:
            return self.name + " (skipped)"
        else:
            return self.name


class MP3Clip(Clip):
    _dev = sounddevice
    _loading_queue: Queue = Queue()
    loading_thread: Optional[Thread] = None

    def __init__(self, file: str, name: str = ""):
        if name == "":
            name = os.path.splitext(os.path.basename(file))[0]
        super().__init__(name)
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
        super().start()
        if self._aborted:
            return

        # wait until MP3 file is loaded
        if not self._loaded.is_set():
            self._loaded.wait()

        duration = len(self._data) / self._sr  # type: ignore

        # play & free memory
        MP3Clip._dev.play(self._data, self._sr)
        self._data = None

        # block thread until completed (or aborted)
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
            data, sr = ffmpeg_load_audio(clip.file)
            # store data
            clip._data = data
            clip._sr = sr
            # send signal that the clip is loaded as .start() might be waiting
            clip._loaded.set()
            time.sleep(0.1)


class Pause(Clip):
    def __init__(self, duration: float = 10):
        super().__init__("Pause ({}min)".format(duration))
        self.duration = duration

    def start(self) -> None:
        super().start()
        self._completed.wait(self.duration * 60)
        self._completed.set()


def describe(clip: Optional[Clip]) -> str:
    if clip is None:
        return "silence"
    else:
        return clip.__str__()
