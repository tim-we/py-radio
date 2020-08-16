import threading
import time
import queue
from audio.clips import Clip, MP3Clip
from scheduler import Scheduler

q = queue.LifoQueue()
c: Clip = None  # currently playing clip
s: Scheduler = Scheduler()


def play(file: str):
    clip = MP3Clip(file)
    clip.user_req = True
    q.put(clip)


def skip():
    if c is not None:
        c.stop()


def player():
    global c

    time.sleep(0.01)

    while True:
        if q.empty():
            q.put(s.next())

        clip = q.get()
        print("playing", clip)
        c = clip
        try:
            clip.start()
        except Exception as e:
            print("Unexpected error", e)
        c = None


threading.Thread(target=player, daemon=False).start()
