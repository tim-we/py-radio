from abc import ABC, abstractmethod
from radio.audio.reader import ffmpeg_load_audio
import sounddevice as sd
import os.path
from threading import Thread, Event
import time
import numpy as np
from queue import Queue
from typing import Optional


class Clip(ABC):
    def __init__(self, name: str):
        self.aborted: bool = False
        self.user_req: bool = False
        self.name: str = name
        self._completed = Event()
        self.hide: bool = False
        self.started: Optional[time.struct_time] = None
        self.duration: float = 0.0

    def start(self) -> None:
        self.started = time.localtime()

    def stop(self) -> None:
        if not self._completed.is_set():
            self.aborted = True
            self._completed.set()

    def show_in_history(self) -> bool:
        return (not self.hide) and (self.started is not None)

    def __str__(self) -> str:
        return self.name

    @abstractmethod
    def copy(self) -> 'Clip':
        pass


class AudioClip(Clip):
    _loading_queue: Queue = Queue()
    loading_thread: Optional[Thread] = None

    def __init__(self, file: str, name: str = ""):
        if name == "":
            name = os.path.splitext(os.path.basename(file))[0]
        super().__init__(name)
        self.file = file
        self.loaded = Event()
        self._data: Optional[np.array] = None
        self._sr: int

        # audio files get preloaded (read & decoded)
        if AudioClip.loading_thread is None:
            AudioClip.loading_thread = Thread(target=AudioClip._load, name="LoadingThread", daemon=True)
            AudioClip.loading_thread.start()
        AudioClip._loading_queue.put(self)

    def start(self) -> None:
        super().start()
        if self.aborted:
            return

        # wait until MP3 file is loaded
        if not self.loaded.is_set():
            self.loaded.wait()
        assert self._data is not None

        # play & free memory
        sd.play(self._data, self._sr)
        self._data = None

        # block thread until completed (or aborted)
        self._completed.wait(self.duration)
        self._completed.set()

    def stop(self) -> None:
        sd.stop()
        super().stop()
        time.sleep(0.1)

    def copy(self) -> Clip:
        return AudioClip(self.file, self.name)

    @classmethod
    def _load(cls) -> None:
        while True:
            # (pre)load next audio clip
            clip = cls._loading_queue.get()
            data, sr = ffmpeg_load_audio(clip.file)
            clip.duration = len(data) / sr  # type: ignore
            # store data
            clip._data = data
            clip._sr = sr
            # send signal that the clip is loaded as .start() might be waiting
            clip.loaded.set()
            time.sleep(0.1)


class Pause(Clip):
    def __init__(self, duration: float = 10):
        super().__init__("Pause ({}min)".format(duration))
        self.duration = duration

    def start(self) -> None:
        super().start()
        self._completed.wait(self.duration * 60)
        self._completed.set()

    def copy(self) -> Clip:
        return Pause(self.duration)
