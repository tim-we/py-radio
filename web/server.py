from radio.player import Player
from radio.library import ClipLibrary
from flask import Flask, jsonify
from typing import Any
from threading import Thread
from waitress import serve


def create(player: Player, library: ClipLibrary, port: int = 5000) -> None:
    flask = Flask("py-radio web-server")

    @flask.route("/radio/api/v1.0/all", methods=["GET"])
    def api_now() -> Any:
        # TODO
        return jsonify({
            "status": "ok",
            "current": "unknown",
            "history": [],
            "next": None
        })

    @flask.route("/radio/api/v1.0/skip", methods=["PUT"])
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
