from queue import Queue
import time
import random
from threading import Thread
from radio.audio import Clip, AudioClip
import radio.library


class Scheduler:
    def __init__(self, library: 'radio.library.ClipLibrary', preload: bool = True):
        self.library = library
        self._queue: Queue = Queue()
        self._force_song = False
        self._other_clips: int = 0
        self._last_host_time: float = 0.0
        if preload:
            Thread(target=self._prepare_next, daemon=True).start()

    def next(self) -> Clip:
        if not self._queue.empty():
            self._force_song = True
            return self._queue.get()
        else:
            if self._force_song:
                self._other_clips = 0
                self._force_song = False
                return AudioClip(self.library.music.next())

            if self._host_time():
                self._last_host_time = time.time()
                self._other_clips = 0
                self._force_song = True
                clip = AudioClip(self.library.hosts.next())
                clip.hide = True
                return clip

            force_music = self.library.other.size() == 0 or self._other_clips > 2

            if force_music or random.uniform(0, 1) < 0.7:
                return AudioClip(self.library.music.next())
            else:
                self._other_clips += 1
                return AudioClip(self.library.other.next())

    def reset(self, hard: bool = False) -> None:
        self._force_song = False
        self._other_clips = 0
        self._last_host_time = 0.0
        if hard:
            self._queue = Queue()

    def schedule(self, clip: Clip) -> None:
        assert clip is not None
        self._queue.put(clip)

    def _host_time(self) -> bool:
        if self.library.hosts.empty():
            return False

        t: float = time.time() - self._last_host_time
        r: float = 4.0 + random.uniform(0.0, 6.0)
        return t > r

    def _prepare_next(self) -> None:
        while True:
            time.sleep(0.5)
            if self._queue.empty():
                clip = self.next()
                self._queue.put(clip)
                if isinstance(clip, AudioClip):
                    clip.loaded.wait()
