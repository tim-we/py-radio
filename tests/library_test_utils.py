import numpy as np
import os
import soundfile
from radio.audio import Clip, AudioClip


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


class TestClip(Clip):
    def __init__(self) -> None:
        super().__init__("TestClip")

    def copy(self) -> Clip:
        return TestClip()
