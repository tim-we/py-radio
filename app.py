from config import Config
from radio import Player, ClipLibrary
from radio.extensions import add_extensions
from bots.tg import Telegram
import web.server
from util.internet import await_internet
import sys

# user configuration
cfg = Config("config.json")

# start radio
print("Radio starting...")
library = ClipLibrary(cfg.get("library"))
if library.music.size() == 0:
    sys.exit("Library does not contain any music.")
player = Player(library)
player.start()

# extensions
add_extensions(player, ["tagesschau"])

# the following modules require internet
await_internet()

# start bots & web server
if cfg.get("web.enabled"):
    web.server.create(
        player=player,
        library=library,
        port=cfg.get("web.port")
    )

if cfg.get("telegram.enabled"):
    telegram = Telegram(cfg.get("telegram.token"), player, library)
    telegram.start()
