from queue import Queue
import time
import random


class Scheduler():
    _queue: Queue = Queue()
    _force_song: bool = False
    _other_clips: int = 0
    _last_host_time: float = 0.0

    def next(self):
        if not self._queue.empty():
            self._force_song = True
            return self._queue.get()
        else:
            if self._force_song:
                self._other_clips = 0
                self._force_song = False
                pass  # TODO: return song

            if self._host_time():
                self._last_host_time = time.time()
                self._other_clips = 0
                self._force_song = True
                pass  # TODO: return host clip

            song: bool = self._other_clips > 2 or random.uniform(0, 1) < 0.7

            if not song:
                self._other_clips += 1

            return  # TODO

    def reset(self, hard: bool = False):
        self._force_song = False
        self._other_clips = 0
        self._last_host_time = 0.0
        if hard:
            self._queue = Queue()

    def _host_time(self):
        # TODO host clips available & enough time has passed
        return False
