from radio.player import Player
from radio.library import ClipLibrary

print("Radio starting...")
library = ClipLibrary("test_library")
player = Player(library)
player.start()
