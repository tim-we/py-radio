import threading
import queue
from audio.clips import Clip, MP3Clip

q = queue.Queue()
c: Clip = None  # currently playing clip


def play(file: str, user_req: bool = False):
    clip = MP3Clip(file)
    clip.user_req = True
    q.put(clip)


def player():
    global c
    while True:
        clip = q.get()
        print("playing", clip)
        c = clip
        try:
            clip.start()
        except Exception as e:
            print("Unexpected error", e)
        c = None


threading.Thread(target=player, daemon=False).start()
