from threading import Thread
import time
from queue import Queue, LifoQueue
from radio.audio.clips import Clip
from radio.scheduler import Scheduler
from radio.library import ClipLibrary
from typing import Optional, List


class Player:
    def __init__(self, library: ClipLibrary):
        self._queue: Queue = LifoQueue()
        self._scheduler = Scheduler(library)
        self._history = []
        self._history_len = 7
        self._current: Optional[Clip] = None
        self._thread: Optional[Thread] = None

    def get_history(self, num: int = 0) -> List[str]:
        if num > 0:
            return self._history[-min(num, self._history_len):]
        else:
            return self._history

    def now(self) -> str:
        if self._current is not None:
            return self._current.name
        else:
            return "silence"

    def schedule(self, clip: Clip) -> None:
        clip.user_req = True
        self._queue.put(clip)

    def skip(self) -> None:
        if self._current is not None:
            self._current.stop()
            print("Skipped", self._current)
        else:
            print("Skip failed: Nothing to skip.")

    def start(self) -> None:
        if self._thread is None:
            self._thread = Thread(target=self._play, daemon=False)
            self._thread.start()

    def _add_to_history(self, name: str) -> None:
        self._history.append(name)
        if len(self._history) > self._history_len:
            self._history.pop(0)

    def _play(self) -> None:
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
            self._add_to_history(clip.name)
            try:
                clip.start()
            except Exception as e:
                print("Unexpected error", e)
                time.sleep(1.0)
            self._current = None
