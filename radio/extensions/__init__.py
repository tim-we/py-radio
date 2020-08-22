from radio.extensions.extension import Extension
from radio.extensions.tagesschau import Tagesschau100s
import radio.player
from typing import List
from threading import Thread
from time import sleep
import radio.scheduler as rs


def add_extensions(player: 'radio.player.Player', exts: List[str]) -> None:
    for ext_id in exts:
        if ext_id == "tagesschau":
            player.add_extension(Tagesschau100s())


def run_extension(scheduler: 'rs.Scheduler', extension: Extension) -> Thread:
    def thread_func(scheduler: 'rs.Scheduler', extension: Extension) -> None:
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
