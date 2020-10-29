from unittest import TestCase
from tests.library_test_utils import create_pool
import shutil
import os
from radio import ClipLibrary, Player
from util import JSONFile
import tempfile
import time
from radio.audio import Clip, Pause


class TestClip(Clip):
    def __init__(self) -> None:
        super().__init__("TestClip")

    def start(self) -> None:
        super().start()
        self._completed.wait(1)
        self._completed.set()

    def copy(self) -> Clip:
        return TestClip()


class TestPlayer(TestCase):
    test_lib_folder: str = ""

    @classmethod
    def setUpClass(cls) -> None:
        folder = os.path.join(tempfile.gettempdir(), "py-radio-test-lib")
        if not os.path.exists(folder):
            os.makedirs(folder)
        cls.test_lib_folder = folder
        # generate library for tests
        create_pool(os.path.join(folder, "music"), "song_", 42)
        create_pool(os.path.join(folder, "hosts"), "dj_")
        create_pool(os.path.join(folder, "night"), "song_night_", 5)
        create_pool(folder, "other_clip_", 10)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.test_lib_folder != "":
            shutil.rmtree(cls.test_lib_folder)

    def test_pause_after_queue(self) -> None:
        library = ClipLibrary(self.test_lib_folder, log=False, auto_update=False)
        json = JSONFile(file_content='{"normalize":true}')
        player = Player(library, json)
        player.start(True)
        player.schedule(TestClip())
        player.schedule(TestClip())
        player.schedule(TestClip())
        player.pause()
        time.sleep(0.2)
        self.assertIsInstance(player.now(), Pause)
        player.skip()
        time.sleep(0.5)
        self.assertIsInstance(player.now(), TestClip)
