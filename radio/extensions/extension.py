from abc import ABC
from radio.audio.clips import Clip
from radio.scheduler import Scheduler
from threading import Thread
from time import sleep
from typing import Optional


class Extension(ABC):
    def __init__(self, name: str, poll_interval: float = 30*60):
        self.name = name
        self.command: Optional[str] = None
        self.poll_interval = poll_interval
        self.poll_delay: float = 5*60
        self.start_delay: float = 10

    def get_clip(self) -> Optional[Clip]:
        return None

    def time_until_next_clip(self) -> Optional[float]:
        return None


def run_extension(scheduler: Scheduler, extension: Extension) -> Thread:
    def thread_func(scheduler: Scheduler, extension: Extension) -> None:
        sleep(extension.start_delay)
        while True:
            time = extension.time_until_next_clip()

            if (time is None) or (time > extension.poll_interval):
                sleep(extension.poll_interval)
                continue

            assert time >= 0.0, "Cannot travel back in time"
            sleep(time)
            clip = extension.get_clip()
            if clip is not None:
                # schedule the clip so it will be played next
                scheduler.schedule(clip)
                # sleep a little while to avoid immediate rescheduling
                sleep(extension.poll_delay)

    thread = Thread(target=thread_func, daemon=True, args=(scheduler, extension))
    thread.start()
    return thread
