import requests
import xml.etree.ElementTree as ET
import tempfile
import os
import time


class Tagesschau100s:
    PODCAST_URL: str = "http://www.tagesschau.de/export/podcast/hi/tagesschau-in-100-sekunden/"

    def __init__(self):
        self.latest: str = ""
        self.time: float = 0.0
        self.update()
        print("Tagesschau in 100s now available.")

    def update(self):
        try:
            # get MP3 URL of latest episode
            res1 = requests.get(Tagesschau100s.PODCAST_URL)
            tree = ET.fromstring(res1.content)
            url = tree.find(".//item/enclosure[@type='audio/mp3']").get("url")

            # download MP3 file
            res2 = requests.get(url)
            tmp_folder = os.path.join(tempfile.gettempdir(), "radio")
            if not os.path.exists(tmp_folder):
                os.makedirs(tmp_folder)
            tmp_file = os.path.join(tmp_folder, "news.mp3")
            with open(tmp_file, 'wb') as tf:
                tf.write(res2.content)

            # update instance vars
            self.latest = tmp_file
            self.time = time.time()
        except Exception as e:
            print("Tagesschau in 100s update failed.")
            print(e)
