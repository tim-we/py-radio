from threading import Thread
import time
from collections import deque
from radio.audio import Clip, AudioClip, Pause
from radio.scheduler import Scheduler
from radio.extensions import Extension, run_extension
import radio.library
from util import JSONFile
from typing import Optional, List, Dict, Deque

HISTORY_LEN: int = 7


class Player:
    def __init__(self, library: 'radio.library.ClipLibrary', config: JSONFile):
        self._queue: Deque[Clip] = deque()
        self._scheduler = Scheduler(library)
        self._history: List[Clip] = []
        self._current: Optional[Clip] = None
        self._thread: Optional[Thread] = None
        self.extensions: Dict[str, Extension] = {}
        normalize = config.get_or_default("normalize", True, bool)
        AudioClip.normalize(normalize)
        if normalize:
            print("Audio normalization enabled.")

    def get_history(self, num: int = 0) -> List["HistoryEntry"]:
        """Returns a list of strings, each representing a clip."""
        cl = self._history if num > 0 else self._history[-min(num, HISTORY_LEN):]
        return list(map(lambda clip: HistoryEntry(clip), cl))

    def now(self) -> Optional[Clip]:
        return self._current

    def schedule(self, clip: Clip) -> None:
        clip.user_req = True
        self._queue.append(clip)

    def skip(self) -> None:
        clip = self._current
        if clip is not None:
            msg = "Skipped {}".format(clip)
            clip.stop()
            print(msg)
        else:
            print("Skip failed: Nothing to skip.")

    def pause(self) -> None:
        if not isinstance(self._current, Pause):
            self._queue.appendleft(Pause())
        self.skip()

    def repeat(self) -> None:
        clip = self._current
        if clip is not None:
            self.schedule(clip.copy())
        else:
            print("Nothing to repeat.")

    def start(self, daemon: bool = False) -> None:
        if self._thread is None:
            self._thread = Thread(target=self._play, name="PlayerThread", daemon=daemon)
            self._thread.start()

    def _add_to_history(self, clip: Clip) -> None:
        if clip.show_in_history():
            self._history.append(clip)
            if len(self._history) > HISTORY_LEN:
                self._history.pop(0)

    def _play(self) -> None:
        while True:
            time.sleep(0.1)

            if len(self._queue) == 0:
                next_clip = self._scheduler.next()
                if isinstance(next_clip, Clip):
                    self._queue.append(next_clip)
                else:
                    time.sleep(1.0)
                    continue

            clip = self._queue.popleft()
            print("Playing", clip)
            self._current = clip
            try:
                clip.start()
            except Exception as e:
                print("Unexpected error", e)
                time.sleep(1.0)
            self._add_to_history(clip)
            self._current = None

    def add_extension(self, extension: Extension) -> None:
        run_extension(self._scheduler, extension)
        if extension.command is not None:
            self.extensions[extension.command] = extension
        print("Extension: '{}' is now active.".format(extension.name))


class HistoryEntry:
    def __init__(self, clip: Clip):
        t = clip.started
        assert t is not None
        self.start = "{:02d}:{:02d}".format(t.tm_hour, t.tm_min)
        self.title = str(clip)
        self.skipped = clip.aborted
        self.userScheduled = clip.user_req

    def __str__(self) -> str:
        return self.start + " `{}`".format(self.title) + " (skipped)"*self.skipped
