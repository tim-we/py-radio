from radio.player import Player
from radio.library import ClipLibrary
from radio.audio.clips import Pause
import time

print("Radio starting...")
library = ClipLibrary("test_library")
player = Player(library)
player.start()
time.sleep(10.0)
player.schedule(Pause(10))
time.sleep(3.14)
player.skip()
