import requests
import xml.etree.ElementTree as ET
import tempfile
import os
import time
from radio.extensions.extension import Extension
from radio.audio import Clip, AudioClip
from typing import Optional

PODCAST_URL = "http://www.tagesschau.de" \
              "/export/podcast/hi/tagesschau-in-100-sekunden/"


class Tagesschau100s(Extension):
    def __init__(self) -> None:
        super().__init__("Tagesschau in 100s")
        self.command = "news"

        self._latest: str = ""
        self._last_update: float = 0.0
        self._update()

    def _update(self) -> None:
        try:
            # get MP3 URL of latest episode
            res1 = requests.get(PODCAST_URL)
            tree = ET.fromstring(res1.content)
            elem = tree.find(".//item/enclosure[@type='audio/mp3']")
            url = elem.get("url")  # type: ignore

            # download MP3 file
            res2 = requests.get(url)  # type: ignore
            tmp_folder = os.path.join(tempfile.gettempdir(), "radio")
            if not os.path.exists(tmp_folder):
                os.makedirs(tmp_folder)
            tmp_file = os.path.join(tmp_folder, "news.mp3")
            with open(tmp_file, 'wb') as tf:
                tf.write(res2.content)

            # update instance vars
            self._latest = tmp_file
            self._last_update = time.time()
        except Exception as e:
            print("Tagesschau in 100s update failed.")
            print(e)

    def get_clip(self) -> Optional[Clip]:
        if self._latest == "":
            return None
        else:
            return AudioClip(self._latest, "Tagesschau in 100s")

    def time_until_next_clip(self) -> Optional[float]:
        # time until next full hour
        lt = time.localtime()
        remaining_time = max(0, 60 - lt.tm_min) * 60

        # time since last update
        t = time.time() - self._last_update
        if t > 25:
            self._update()

        return remaining_time
