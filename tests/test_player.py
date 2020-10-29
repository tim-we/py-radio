from unittest import TestCase
from tests.library_test_utils import create_pool, TestClip
import shutil
import os
from radio import ClipLibrary, Player
from util import JSONFile
import tempfile
import time
from radio.audio import Pause
from radio.scheduler import Scheduler


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
        Scheduler.preload_default = False
        player = Player(library, json)
        player.schedule(TestClip())
        player.schedule(TestClip())
        player.schedule(TestClip())
        player.start(True)
        player.pause()
        time.sleep(0.25)
        self.assertIsInstance(player.now(), Pause)
        player.skip()
        time.sleep(0.25)
        self.assertIsInstance(player.now(), TestClip)
