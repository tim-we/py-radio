import glob
import os
import random
import time
from threading import Thread
from itertools import chain
from more_itertools import peekable
import re
from typing import List, Iterable


class ClipLibrary:
    def __init__(self, folder: str, log: bool = True, auto_update: bool = True):
        if log:
            print("Building clip library...")
        self.hosts = ClipPool(os.path.join(folder, "hosts"))
        self.music = ClipPool(os.path.join(folder, "music"))
        self.night = ClipPool(os.path.join(folder, "night"))
        self.other = ClipPool(folder)
        self.folder = folder
        self.abs_path = os.path.abspath(folder)
        if log:
            print(" ->", self.music.size() + self.night.size(), "songs")
            print(" ->", self.hosts.size(), "host clips")
        if auto_update:
            Thread(target=self._update_thread, name="LibUpdateThread", daemon=True).start()

    def update(self) -> None:
        print("Updating library...")
        self.hosts.scan()
        self.music.scan()
        self.night.scan()
        self.other.scan()

    def _update_thread(self) -> None:
        while(True):
            # wait 30min
            time.sleep(30 * 60)
            # update library
            self.update()

    def _filter(self, search: str) -> Iterable[str]:
        return chain(
            self.music.filter(search),
            self.night.filter(search),
            self.other.filter(search),
            self.night.filter(search)
        )

    def search_clips(self, search: str, short_path: bool = False) -> List[str]:
        # get all paths matching the search term
        raw_results = peekable(self._filter(search))
        # do extended search if there are no matches
        if raw_results.peek(None) is None:
            delimiters = [".", " ", "-", "_"]
            search_parts = list(filter(
                lambda s: len(s.strip()) > 0,
                re.split("|".join(map(re.escape, delimiters)), search)
            ))
            if len(search_parts) > 0 and (search is not search_parts[0]):
                parts = iter(search_parts)
                results = self._filter(next(parts))
                for search_part in parts:
                    results = filter(
                        lambda x: search_part in x.lower(),
                        results
                    )
                raw_results = peekable(results)

        # return only relative paths if short_path is true
        n = 0
        if short_path:
            n = len(self.folder)
            # also remove /
            if not self.folder[-1] == os.sep:
                n += 1
        clean_results = map(lambda x: x[n:], raw_results)
        return list(clean_results)


class ClipPool:
    def __init__(self, folder: str):
        assert os.path.exists(folder), "The folder for this ClipPool does not exist"
        self.clips: List[str] = []
        self._history: List[int] = []
        self._history_len: int = 0
        self.folder = folder
        self.scan()

    def empty(self) -> bool:
        return len(self.clips) == 0

    def next(self) -> str:
        assert not self.empty(), "Cannot pick clip from empty pool"

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
        self.clips = glob.glob(os.path.join(self.folder, "*.*"))
        size = len(self.clips)
        self._history_len = min(size - 1, min(max(size//10, 10), 42))
        self._history = []
