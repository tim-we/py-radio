from radio.player import Player
from radio.library import ClipLibrary
from flask import Flask, jsonify, render_template, send_from_directory
from typing import Any
from threading import Thread
from waitress import serve

api_prefix = "/radio/api/v1.0"


def create(player: Player, library: ClipLibrary, port: int = 5000) -> None:
    flask = Flask(__name__.split('.')[0])

    # -------------- WEBSITE --------------
    @flask.route("/radio", methods=["GET"])
    def web_main() -> Any:
        return render_template("web.html")

    @flask.route("/radio/static/<path:path>")
    def web_static(path: Any) -> Any:
        return send_from_directory("static", path)

    # ---------------- API ----------------
    @flask.route(api_prefix + "/all", methods=["GET"])
    def api_now() -> Any:
        return jsonify({
            "status": "ok",
            "current": player.now(),
            "history": player.get_history(),
            "library": {
                "music": library.music.size() + library.night.size(),
                "hosts": library.hosts.size(),
                "other": library.other.size()
            }
        })

    @flask.route(api_prefix + "/search/<string:search>", methods=["GET"])
    def api_search(search: str) -> Any:
        search = search.strip()[0:42]
        if len(search) == 0:
            return jsonify({
                "status": "error",
                "message": "Invalid search term."
            })
        else:
            results = library.search_clips(search)
            return jsonify({
                "status": "ok",
                "search": search,
                "results": results[0:100],
                "clipped": len(results) > 100
            })

    @flask.route(api_prefix + "/skip", methods=["PUT"])
    def api_skip() -> Any:
        player.skip()
        return jsonify({"status": "ok"})

    def start() -> None:
        print("API will be available at http://localhost:{}{}/".format(port, api_prefix))
        serve(
            flask,
            host="127.0.0.1",
            port=port,
            ident="py-radio web-server"
        )

    Thread(target=start, daemon=True).start()