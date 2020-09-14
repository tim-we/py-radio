from unittest import TestCase
import tempfile
import os
import soundfile
import numpy as np
from radio import ClipLibrary
from radio.scheduler import Scheduler
from radio.audio import Clip, AudioClip
import shutil


def create_wav_file(file: str) -> None:
    sr = 48000
    data = np.zeros((sr,), dtype=np.float32)
    soundfile.write(file, data, sr)


def create_pool(folder: str, prefix: str, n: int = 10) -> None:
    if not os.path.exists(folder):
        os.makedirs(folder)
    for i in range(n):
        file = os.path.join(folder, prefix + str(i+1) + ".wav")
        create_wav_file(file)

def audio_clip_file_contains(clip: Clip, name: str) -> bool:
    assert isinstance(clip, AudioClip), "Clip is not an AudioClip!"
    audio_clip: AudioClip = clip  # type: ignore
    return name in audio_clip.file


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
        create_pool(os.path.join(folder, "night"), "song_", 5)
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
