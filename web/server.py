from radio.player import Player
from radio.library import ClipLibrary
from flask import Flask, jsonify
from typing import Any
from threading import Thread
from waitress import serve

api_prefix = "/radio/api/v1.0"


def create(player: Player, library: ClipLibrary, port: int = 5000) -> None:
    flask = Flask("py-radio web-server")

    @flask.route(api_prefix + "/all", methods=["GET"])
    def api_now() -> Any:
        return jsonify({
            "status": "ok",
            "current": player.now(),
            "history": player.get_history()
        })

    @flask.route(api_prefix + "/skip", methods=["PUT"])
    def api_skip() -> Any:
        player.skip()
        return jsonify({"status": "ok"})

    def start() -> None:
        serve(
            flask,
            host="127.0.0.1",
            port=port,
            ident="py-radio web-server"
        )

    Thread(target=start, daemon=True).start()
