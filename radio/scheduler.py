from queue import Queue
import time
import random
from radio.audio.clips import Clip, MP3Clip
from radio.library import ClipLibrary


class Scheduler:
    def __init__(self, library: ClipLibrary):
        self.library = library
        self._queue: Queue = Queue()
        self._force_song: bool = False
        self._other_clips: int = 0
        self._last_host_time: float = 0.0

    def next(self) -> Clip:
        if not self._queue.empty():
            self._force_song = True
            return self._queue.get()
        else:
            if self._force_song:
                self._other_clips = 0
                self._force_song = False
                return MP3Clip(self.library.music.next())

            if self._host_time():
                self._last_host_time = time.time()
                self._other_clips = 0
                self._force_song = True
                return MP3Clip(self.library.hosts.next())

            if self._other_clips > 2 or random.uniform(0, 1) < 0.7:
                return self.library.music.next()
            else:
                self._other_clips += 1
                return self.library.other.next()

    def reset(self, hard: bool = False):
        self._force_song = False
        self._other_clips = 0
        self._last_host_time = 0.0
        if hard:
            self._queue = Queue()

    def _host_time(self) -> bool:
        if self.library.hosts.empty():
            return False

        t: float = time.time() - self._last_host_time
        r: float = 4.0 + random.uniform(0.0, 6.0)
        return t > r
