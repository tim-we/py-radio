from threading import Thread
import time
from queue import LifoQueue
from radio.audio.clips import Clip, MP3Clip
from radio.scheduler import Scheduler
from radio.library import ClipLibrary


class Player:
    _queue: LifoQueue = LifoQueue()
    _current: Clip = None
    _thread: Thread = None

    def __init__(self, library: ClipLibrary):
        self._scheduler = Scheduler(library)

    def schedule(self, file: str):
        clip = MP3Clip(file)
        clip.user_req = True
        self._queue.put(clip)

    def skip(self):
        if self._current is not None:
            self._current.stop()

    def start(self):
        if self._thread is None:
            self._thread = Thread(target=self._play, daemon=False).start()

    def _play(self):
        while True:
            if self._queue.empty():
                next_clip = self._scheduler.next()
                if isinstance(next_clip, Clip):
                    self._queue.put(next_clip)
                else:
                    time.sleep(1.0)
                    continue

            clip = self._queue.get()
            print("Playing", clip)
            self._current = clip
            try:
                clip.start()
            except Exception as e:
                print("Unexpected error", e)
                time.sleep(1.0)
            self._current = None
