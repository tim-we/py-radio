from util import await_internet, JSONFile
from radio import Player, ClipLibrary
from radio.extensions import add_extensions
from hardware.button import RadioButton
from bots.tg import Telegram
import web.server
import sys

# user configuration
cfg = JSONFile("config.json")

# start radio
print("Radio starting...")
library = ClipLibrary(cfg.get("library", "test_library", expected_type=str))
if library.music.size() == 0:
    sys.exit("Library does not contain any music.")
player = Player(library, cfg)
player.start()

# extensions
add_extensions(player, cfg.get("extensions", [], expected_type=list))

# hardware
if cfg.get("hardware.button.enabled", False, expected_type=bool):
    RadioButton(
        player=player,
        pause=cfg.get("hardware.button.pause", False, expected_type=bool),
        skip=cfg.get("hardware.button.skip", True, expected_type=bool)
    )

# the following modules require internet
await_internet()

# start bots & web server
if cfg.get("web.enabled", False, expected_type=bool):
    web.server.create(
        player=player,
        library=library,
        config=cfg
    )

if cfg.get("telegram.enabled", False, expected_type=bool):
    telegram = Telegram(
        cfg.get("telegram.token", "", fail=True, expected_type=str),
        player,
        library
    )
    telegram.start()
