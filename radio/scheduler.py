from collections import deque
import time
import random
from threading import Thread
from radio.audio import Clip, AudioClip
import radio.library
from math import sqrt
from typing import Deque


class Scheduler:
    def __init__(self, library: 'radio.library.ClipLibrary', preload: bool = True):
        self.library = library
        self._queue: Deque[Clip] = deque()
        self._force_song = False
        self._other_clips: int = 0
        self._last_host_time: float = 0.0
        if preload:
            Thread(target=self._prepare_next, daemon=True).start()

    def next(self) -> Clip:
        if len(self._queue) > 0:
            return self._queue.popleft()
        else:
            now = time.localtime()
            is_day = (now.tm_hour > 7 and now.tm_hour < 23) or (self.library.night.size() == 0)
            night_ratio = 0.75 * sqrt((min(25, self.library.night.size())/25))
            assert night_ratio >= 0.0 and night_ratio <= 1.0
            day_ratio = 1.0 - night_ratio
            music_pool = self.library.music if (is_day or random.uniform(0, 1) < day_ratio) else self.library.night

            if self._force_song:
                self._other_clips = 0
                self._force_song = False
                return AudioClip(music_pool.next())

            if self._host_time():
                self._last_host_time = time.time()
                self._other_clips = 0
                self._force_song = True
                clip = AudioClip(self.library.hosts.next())
                clip.hide = True
                return clip

            force_music = self.library.other.size() == 0 or self._other_clips > 2

            if force_music or random.uniform(0, 1) < 0.7:
                return AudioClip(music_pool.next())
            else:
                self._other_clips += 1
                return AudioClip(self.library.other.next())

    def reset(self, hard: bool = False) -> None:
        self._force_song = False
        self._other_clips = 0
        self._last_host_time = 0.0
        if hard:
            self._queue.clear()

    def schedule(self, clip: Clip, prepend: bool = False) -> None:
        assert clip is not None
        if prepend:
            self._queue.appendleft(clip)
        else:
            self._queue.append(clip)

    def _host_time(self) -> bool:
        if self.library.hosts.empty():
            return False

        t: float = (time.time() - self._last_host_time)/60
        r: float = 4.0 + random.uniform(0.0, 6.0)
        return t > r

    def _prepare_next(self) -> None:
        while True:
            time.sleep(0.5)
            if len(self._queue) == 0:
                clip = self.next()
                self._queue.append(clip)
                if isinstance(clip, AudioClip):
                    clip.loaded.wait()
