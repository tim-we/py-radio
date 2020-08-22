import radio.player
import radio.library
from radio.audio import AudioClip, Pause
from radio.extensions import Extension
from flask import Flask, jsonify, send_file, request
from typing import Any
from threading import Thread, active_count
from waitress import serve
import ifcfg
import os
import sys

api_prefix = "/api/v1.0"


def create(
    player: 'radio.player.Player',
    library: 'radio.library.ClipLibrary',
    port: int = 80
) -> None:
    flask = Flask(
        __name__.split('.')[0],
        static_url_path="/static",
        static_folder="static"
    )

    host = ifcfg.default_interface()["inet"]

    # -------------- WEBSITE --------------
    @flask.route("/", methods=["GET"])
    def web_main() -> Any:
        return send_file("static/web.html")

    # ---------------- API ----------------
    @flask.route(api_prefix + "/now", methods=["GET"])
    def api_now() -> Any:
        now = player.now()
        return jsonify({
            "status": "ok",
            "current": "-" if now is None else now.__str__(),
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

    @flask.route(api_prefix + "/schedule", methods=["POST"])
    def api_schedule() -> Any:
        file = request.values.get("file")
        if file is None:
            return jsonify({
                "status": "error",
                "message": "Invalid request: 'file' not set."
            })
        results = library.search_clips(file)
        if not len(results) == 1:
            return jsonify({
                "status": "error",
                "message": "Found {} files, expected 1.".format(len(results))
            })
        clip = AudioClip(results[0])
        player.schedule(clip)
        return jsonify({
            "status": "ok",
            "clip": clip.__str__()
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

    @flask.route(api_prefix + "/sysinfo", methods=["GET"])
    def api_sysinfo() -> Any:
        pv = sys.implementation.version
        return jsonify({
            "status": "ok",
            "cpu_count": os.cpu_count(),
            "process_id": os.getpid(),
            "os": os.uname().sysname,
            "python_version": "{}.{}".format(pv.major, pv.minor),
            "threads": active_count()
        })

    @flask.route(api_prefix + "/extensions", methods=["GET"])
    def api_extensions() -> Any:
        return jsonify({
            "status": "ok",
            "extensions": list(map(
                lambda e: {"name": e[1].name, "command": e[0]},
                player.extensions.items()
            ))
        })

    @flask.route(api_prefix + "/extensions/<string:ext>/schedule", methods=["PUT"])
    def api_schedule_extension(ext: str) -> Any:
        if ext in player.extensions:
            extension: Extension = player.extensions[ext]
            clip = extension.get_clip()
            if clip is not None:
                print("{} scheduled via API".format(extension.name))
                player.schedule(clip)
                if isinstance(clip, AudioClip):
                    clip.loaded.wait()
                if not player.now() == clip:
                    player.skip()
                return jsonify({"status": "ok"})
            else:
                return jsonify({
                    "status": "error",
                    "message": "{} did not provide a clip.".format(extension.name)
                })
        else:
            return jsonify({
                "status": "error",
                "message": "No extension for this command."
            })

    @flask.route(api_prefix + "/library/update", methods=["PUT"])
    def api_library_update() -> Any:
        thread = Thread(target=library.update, name="APILibUpdateThread")
        thread.start()
        thread.join(1.0)
        return jsonify({
            "status": "ok",
            "update_status": "updating" if thread.is_alive() else "completed"
        })

    def start() -> None:
        serve(
            flask,
            host=host,
            port=port,
            ident="py-radio web-server"
        )
        print("API will be available at http://{}:{}{}/".format(host, port, api_prefix))

    Thread(target=start, name="ServerThread", daemon=True).start()
