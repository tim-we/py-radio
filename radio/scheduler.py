from queue import Queue
import time
import random
from threading import Thread
from radio.audio.clips import Clip, MP3Clip
from radio.library import ClipLibrary
from radio.services.tagesschau import Tagesschau100s


class Scheduler:
    def __init__(self, library: ClipLibrary):
        self.library = library
        self._queue = Queue()
        self._force_song = False
        self._other_clips: int = 0
        self._last_host_time: float = 0.0
        self.tagesschau = Tagesschau100s()
        Thread(target=self._news_thread, daemon=True).start()

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

    def _news_thread(self):
        while(True):
            # compute remaining time
            t = time.localtime()
            rm = max(0, 60 - t.tm_min)

            # await next full hour
            time.sleep(60*rm)

            # update & schedule news
            self.tagesschau.update()
            if not self.tagesschau.latest == "":
                self._queue.put(MP3Clip(self.latest))
