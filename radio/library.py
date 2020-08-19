import glob
import os
import random
import time
from threading import Thread
from typing import List, Iterable
from itertools import chain


class ClipLibrary:
    def __init__(self, folder: str):
        print("Building clip library...")
        self.hosts = ClipPool(os.path.join(folder, "hosts"))
        self.music = ClipPool(os.path.join(folder, "music"))
        self.night = ClipPool(os.path.join(folder, "night"))
        self.other = ClipPool(folder)
        self.folder = folder
        print(" ->", self.music.size() + self.night.size(), "songs")
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

    def search_clips(self, search: str, short_path: bool = False) -> List[str]:
        # get all paths matching the search term
        raw_results = chain(
            self.music.filter(search),
            self.night.filter(search),
            self.other.filter(search)
        )
        # return only relative paths if short_path is true
        n = 0
        if short_path:
            n = len(self.folder)
            if not self.folder[-1] == os.sep:
                n += 1
        clean_results = map(lambda x: x[n:], raw_results)
        return list(clean_results)


class ClipPool:
    def __init__(self, folder: str):
        self.clips: List[str] = []
        self._history: List[int] = []
        self._history_len: int = 0
        self.folder = folder
        self.scan()

    def empty(self) -> bool:
        return len(self.clips) == 0

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

    def filter(self, search: str) -> Iterable[str]:
        ls = search.lower()
        return filter(
            lambda x: ls in x.lower(),
            self.clips
        )

    def size(self) -> int:
        return len(self.clips)

    def scan(self) -> None:
        self.clips = glob.glob(os.path.join(self.folder, "*.mp3"))
        size = len(self.clips)
        self._history_len = min(size - 1, min(max(size//10, 10), 42))
        self._history = []
