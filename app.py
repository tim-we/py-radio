from util import await_internet, JSONFile
from radio import Player, ClipLibrary
from radio.extensions import add_extensions
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
player = Player(library)
player.start()

# extensions
add_extensions(player, ["tagesschau"])

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
