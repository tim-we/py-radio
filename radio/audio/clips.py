from abc import ABC, abstractmethod
import audio2numpy
import sounddevice as sd
import time
import os.path


class Clip(ABC):
    _aborted: bool = False
    user_req: bool = False

    @abstractmethod
    def start(self):
        pass

    def stop(self):
        self._aborted = True


class MP3Clip(Clip):
    def __init__(self, file: str):
        self.file = file

    def start(self):
        data, sr = audio2numpy.open_audio(self.file)
        sd.play(data, sr)
        sd.wait()

    def stop(self):
        sd.stop()
        super.stop()

    def __str__(self):
        return os.path.basename(self.file)


class Pause(Clip):
    def __init__(self, duration: float = 600):
        self.duration = duration

    def start(self):
        time.sleep(self.duration)

    def stop(self):
        pass  # TODO

    def __str__(self):
        return "" + self.duration + "s pause"
