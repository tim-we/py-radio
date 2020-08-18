from radio.player import Player
from radio.library import ClipLibrary
import json
import os

# defaults
lib_path = "test_library"
cfg_path = "config.json"

# user config
if os.path.exists(cfg_path):
    with open(cfg_path, "r") as config_file:
        cfg = json.loads(config_file.read())
        print("Using config file", config_file.name)
        if "library" in cfg:
            lib_path = cfg["library"]
else:
    print("Warning:", cfg_path, "not found.")

# start radio
print("Radio starting...")
library = ClipLibrary(lib_path)
player = Player(library)
player.start()
