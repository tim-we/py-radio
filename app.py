from radio import Player, ClipLibrary
from radio.extensions import add_extensions
from bots.tg import Telegram
import web.server
from util import await_internet, JSONFile
import sys

# user configuration
cfg = JSONFile("config.json")

# start radio
print("Radio starting...")
library = ClipLibrary(cfg.get("library", "test_library"))
if library.music.size() == 0:
    sys.exit("Library does not contain any music.")
player = Player(library)
player.start()

# extensions
add_extensions(player, ["tagesschau"])

# the following modules require internet
await_internet()

# start bots & web server
if cfg.get("web.enabled", False):
    web.server.create(
        player=player,
        library=library,
        port=cfg.get("web.port", 6969)
    )

if cfg.get("telegram.enabled", False):
    telegram = Telegram(cfg.get("telegram.token", "", fail=True), player, library)
    telegram.start()
