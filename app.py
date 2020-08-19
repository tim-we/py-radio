from config import Config
from radio.player import Player
from radio.library import ClipLibrary
from bots.tg import Telegram
import web.server
from time import sleep

# user configuration
cfg = Config("config.json")

# start radio
print("Radio starting...")
library = ClipLibrary(cfg.get("library"))
player = Player(library)
player.start()

sleep(20)

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
