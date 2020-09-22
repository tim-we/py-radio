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
library = ClipLibrary(cfg.get_or_fail("library", str))
if library.music.size() == 0:
    sys.exit("Library does not contain any music.")
player = Player(library, cfg)
player.start()

# extensions
add_extensions(player, cfg.get_or_default("extensions", [], list))

# hardware
if cfg.get_or_default("hardware.button.enabled", False, bool):
    RadioButton(
        player=player,
        pause=cfg.get_or_default("hardware.button.pause", False, bool),
        skip=cfg.get_or_default("hardware.button.skip", True, bool)
    )

# the following modules require internet
await_internet()

# start bots & web server
if cfg.get_or_default("web.enabled", False, bool):
    web.server.create(
        player=player,
        library=library,
        config=cfg
    )

if cfg.get_or_default("telegram.enabled", False, bool):
    telegram = Telegram(
        cfg.get_or_fail("telegram.token", str),
        player,
        library
    )
    telegram.start()
