from unittest import TestCase
import tempfile
import os
from radio import ClipLibrary
from radio.scheduler import Scheduler
from radio.audio import Clip
import shutil
from unittest.mock import patch
from typing import Any
from tests.library_test_utils import create_wav_file, create_pool, audio_clip_file_contains


class TestClip(Clip):
    def __init__(self) -> None:
        super().__init__("TestClip")

    def copy(self) -> Clip:
        return TestClip()


class TestLibraryAndScheduler(TestCase):
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

    def test_create_library(self) -> None:
        library = ClipLibrary(self.test_lib_folder, log=False, auto_update=False)
        self.assertGreater(library.music.size(), 0)
        self.assertGreater(library.hosts.size(), 0)
        self.assertGreater(library.night.size(), 0)
        self.assertGreater(library.other.size(), 0)

    def test_library_update(self) -> None:
        library = ClipLibrary(self.test_lib_folder, log=False, auto_update=False)
        n = library.music.size()
        filepath = os.path.join(self.test_lib_folder, "music", "new_song.wav")
        create_wav_file(filepath)
        library.update()
        self.assertEqual(library.music.size(), n+1)
        os.remove(filepath)
        library.update()
        self.assertEqual(library.music.size(), n)

    def test_library_search(self) -> None:
        library = ClipLibrary(self.test_lib_folder, log=False, auto_update=False)
        res1 = library.search_clips("song_")
        self.assertGreater(len(res1), 0)
        res2 = library.search_clips("song_night")
        self.assertGreater(len(res2), 0)
        self.assertGreater(len(res1), len(res2))
        res3 = library.search_clips("dj_")
        self.assertEqual(len(res3), 0)

    def test_library_search_no_duplicates(self) -> None:
        library = ClipLibrary(self.test_lib_folder, log=False, auto_update=False)
        results = library.search_clips("song_")
        unique_results = set(results)
        self.assertEqual(len(results), len(unique_results))

    def test_scheduler_start(self) -> None:
        library = ClipLibrary(self.test_lib_folder, log=False, auto_update=False)
        self.assertGreater(library.hosts.size(), 0)
        scheduler = Scheduler(library, preload=False)
        # first clip should be a host announcement
        first_clip = scheduler.next()
        self.assertTrue(audio_clip_file_contains(first_clip, "dj_"))
        # second clip should be from "music"
        snd_clip = scheduler.next()
        self.assertTrue(audio_clip_file_contains(snd_clip, "song_"))

    def test_scheduler_manual(self) -> None:
        library = ClipLibrary(self.test_lib_folder, log=False, auto_update=False)
        scheduler = Scheduler(library, preload=False)
        test_clip = TestClip()
        scheduler.schedule(test_clip)
        next_clip = scheduler.next()
        self.assertIsInstance(next_clip, TestClip)

    def test_scheduler_prepend(self) -> None:
        library = ClipLibrary(self.test_lib_folder, log=False, auto_update=False)
        scheduler = Scheduler(library, preload=False)
        clip1 = TestClip()
        clip2 = TestClip()
        clip3 = TestClip()
        scheduler.schedule(clip1)
        scheduler.schedule(clip2)
        scheduler.schedule(clip3, prepend=True)
        self.assertEqual(scheduler.next(), clip3)
        self.assertEqual(scheduler.next(), clip1)
        self.assertEqual(scheduler.next(), clip2)

    @patch("random.uniform", return_value=1.0)
    @patch("time.time", return_value=0.0)
    def test_scheduler_host_frequency(self, patched_time: Any, patched_random: Any) -> None:
        library = ClipLibrary(self.test_lib_folder, log=False, auto_update=False)
        scheduler = Scheduler(library, preload=False)
        for i in range(10):
            patched_time.return_value += 10*60  # 10min
            self.assertTrue(audio_clip_file_contains(scheduler.next(), "dj_"))
            patched_time.return_value += 42
            self.assertFalse(audio_clip_file_contains(scheduler.next(), "dj_"))
