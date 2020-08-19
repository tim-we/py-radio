from radio.player import Player
from radio.library import ClipLibrary
from flask import Flask, jsonify, render_template, send_from_directory
from typing import Any
from threading import Thread
from waitress import serve
import ifcfg
from radio.audio.clips import Pause, describe

api_prefix = "/api/v1.0"


def create(player: Player, library: ClipLibrary, host: str = "", port: int = 80) -> None:
    flask = Flask(__name__.split('.')[0])

    if host == "":
        host = ifcfg.default_interface()["inet"]

    # -------------- WEBSITE --------------
    @flask.route("/", methods=["GET"])
    def web_main() -> Any:
        return render_template("web.html")

    @flask.route("/static/<path:path>")
    def web_static(path: Any) -> Any:
        return send_from_directory("static", path)

    # ---------------- API ----------------
    @flask.route(api_prefix + "/now", methods=["GET"])
    def api_now() -> Any:
        return jsonify({
            "status": "ok",
            "current": describe(player.now()),
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
            results = library.search_clips(search, short_path=True)
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

    @flask.route(api_prefix + "/pause", methods=["POST", "PUT"])
    def api_pause() -> Any:
        if not isinstance(player.now(), Pause):
            player.schedule(Pause())
        player.skip()
        return jsonify({"status": "ok"})

    def start() -> None:
        serve(
            flask,
            host=host,
            port=port,
            ident="py-radio web-server"
        )
        print("API will be available at http://{}:{}{}/".format(host, port, api_prefix))

    Thread(target=start, daemon=True).start()
