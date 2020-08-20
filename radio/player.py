from threading import Thread
import time
from queue import Queue, LifoQueue
from radio.audio.clips import Clip
from radio.scheduler import Scheduler
from radio.library import ClipLibrary
from typing import Optional, List

HISTORY_LEN: int = 7


class Player:
    def __init__(self, library: ClipLibrary):
        self._queue: Queue = LifoQueue()
        self._scheduler = Scheduler(library)
        self._history: List[Clip] = []
        self._current: Optional[Clip] = None
        self._thread: Optional[Thread] = None

    def get_history(self, num: int = 0, format_title: str = '{}', format_skip: str = ' (skipped)') -> List[str]:
        """Returns a list of strings, each representing a clip."""
        cl = self._history if num > 0 else self._history[-min(num, HISTORY_LEN):]
        sl = []
        for clip in cl:
            t = clip.started
            assert t is not None
            sl.append('{:02d}:{:02d} '.format(t.tm_hour, t.tm_min) + format_title.format(clip.__str__())
                      + format_skip*clip.aborted)
        return sl

    def now(self) -> Optional[Clip]:
        return self._current

    def schedule(self, clip: Clip) -> None:
        clip.user_req = True
        self._queue.put(clip)

    def skip(self) -> None:
        if self._current is not None:
            msg = "Skipped {}".format(self._current)
            self._current.stop()
            print(msg)
        else:
            print("Skip failed: Nothing to skip.")

    def start(self) -> None:
        if self._thread is None:
            self._thread = Thread(target=self._play, name="PlayerThread", daemon=False)
            self._thread.start()

    def _add_to_history(self, clip: Clip) -> None:
        if clip.show_in_history():
            # t = clip.started
            # "[{:02d}:{:02d}] {}".format(t.tm_hour, t.tm_min, clip.__str__())
            self._history.append(clip)
            if len(self._history) > HISTORY_LEN:
                self._history.pop(0)

    def _play(self) -> None:
        while True:
            time.sleep(0.1)
            
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
            self._add_to_history(clip)
            self._current = None
