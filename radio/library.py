import glob
import os
import random
import time
from threading import Thread
from typing import List


class ClipLibrary:
    def __init__(self, folder: str):
        print("Building clip library...")
        self.hosts = ClipPool(os.path.join(folder, "hosts"))
        self.music = ClipPool(os.path.join(folder, "music"))
        self.night = ClipPool(os.path.join(folder, "night"))
        self.other = ClipPool(folder)
        print(" ->", self.music.size(), "songs")
        print(" ->", self.hosts.size(), "host clips")
        Thread(target=self._update_thread, daemon=True)

    def _update_thread(self) -> None:
        while(True):
            # wait 30min
            time.sleep(30 * 60)
            # update library
            print("Updating library...")
            self.hosts.scan()
            self.music.scan()
            self.night.scan()
            self.other.scan()


class ClipPool:
    def __init__(self, folder: str):
        self.clips: List[str] = []
        self._history: List[int] = []
        self._history_len: int = 0
        self._folder = folder
        self.scan()

    def next(self) -> str:
        # find a clip that is not in the recent history
        idx = random.randrange(0, len(self.clips))
        while idx in self._history:
            idx = random.randrange(0, len(self.clips))

        # add to recent history
        self._history.append(idx)
        if len(self._history) > self._history_len:
            del self._history[0]

        return self.clips[idx]

    def empty(self) -> bool:
        return len(self.clips) == 0

    def size(self) -> int:
        return len(self.clips)

    def scan(self) -> None:
        self.clips = glob.glob(os.path.join(self._folder, "*.mp3"))
        size = len(self.clips)
        self._history_len = min(size - 1, min(max(size//10, 10), 42))
        self._history = []
