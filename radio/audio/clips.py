from abc import ABC, abstractmethod
import audio2numpy
import sounddevice
import time
import os.path


class Clip(ABC):
    def __init__(self, name: str):
        self._aborted: bool = False
        self.user_req: bool = False
        self.name: str = name

    @abstractmethod
    def start(self):
        pass

    def stop(self):
        self._aborted = True

    def __str__(self):
        return self.name


class MP3Clip(Clip):
    _dev = sounddevice

    def __init__(self, file: str):
        super().__init__(os.path.basename(file))
        self.file = file

    def start(self):
        data, sr = audio2numpy.open_audio(self.file)
        MP3Clip._dev.play(data, sr)
        MP3Clip._dev.wait()

    def stop(self):
        MP3Clip._dev.stop()
        super().stop()


class Pause(Clip):
    def __init__(self, duration: float = 600):
        super().__init__("" + duration + "s pause")
        self.duration = duration

    def start(self):
        time.sleep(self.duration)

    def stop(self):
        pass  # TODO
