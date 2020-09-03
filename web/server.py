from util import JSONFile
import radio.player
import radio.library
from radio.audio import AudioClip, Pause
from radio.extensions import Extension
from flask import Flask, jsonify, send_file, request, abort
from threading import Thread, active_count
from waitress import serve
import ifcfg
import os
import sys
from typing import Any, Optional

api_prefix = "/api/v1.0"
MAX_SEARCH_RESULTS = 50


def create(
    player: 'radio.player.Player',
    library: 'radio.library.ClipLibrary',
    config: JSONFile
) -> None:
    flask = Flask(
        __name__.split('.')[0],
        static_url_path="/static",
        static_folder="static"
    )

    # -------------- CONFIG ---------------
    host: str = config.get("web.host", "inet", expected_type=str)
    dif = ifcfg.default_interface()
    if "." not in host and host in dif:
        host = dif[host]
    port: int = config.get("web.port", 6969, expected_type=int)
    if port < 1024:
        print("Warning: Ports below 1024 require root access.")

    # -------------- ERRORS ---------------
    @flask.errorhandler(404)
    def resource_not_found(e):
        if request.path.startswith("/api/"):
            response = jsonify({
                "status": "error",
                "message": str(e),
                "version": "1.0"
            })
        else:
            response = send_file("static/error.html")
        return response, 404

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

    @flask.route(api_prefix + "/library/search", methods=["GET"])
    def api_search() -> Any:
        query: str = request.args.get("query", "", type=str).strip()[0:42]
        if len(query) == 0:
            return jsonify({
                "status": "error",
                "message": "Invalid query."
            })
        else:
            results = library.search_clips(query, short_path=True)
            return jsonify({
                "status": "ok",
                "query": query,
                "results": results[0:MAX_SEARCH_RESULTS],
                "num_all_results": len(results)
            })

    @flask.route(api_prefix + "/library/download", methods=["GET"])
    def api_download() -> Any:
        file: Optional[str] = request.args.get("file", type=str)
        if file is None:
            abort(400, description="Required argument 'file' is missing.")
        results = library.search_clips(file, short_path=True)
        if len(results) == 1 and results[0] == file:
            path = os.path.join(library.abs_path, results[0])
            return send_file(
                path,
                as_attachment=True,
                attachment_filename=os.path.basename(path)
            )
        else:
            abort(404, description="Resource not found.")

    @flask.route(api_prefix + "/library/update", methods=["PUT"])
    def api_library_update() -> Any:
        thread = Thread(target=library.update, name="APILibUpdateThread")
        thread.start()
        thread.join(1.0)
        return jsonify({
            "status": "ok",
            "update_status": "updating" if thread.is_alive() else "completed"
        })

    @flask.route(api_prefix + "/schedule", methods=["POST"])
    def api_schedule() -> Any:
        file: Optional[str] = request.values.get("file", type=str)
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

    @flask.route(api_prefix + "/repeat", methods=["PUT"])
    def api_repeat() -> Any:
        player.repeat()
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

    def start() -> None:
        serve(
            flask,
            host=host,
            port=port,
            ident="py-radio web-server"
        )
        print("API will be available at http://{}:{}{}/".format(host, port, api_prefix))

    Thread(target=start, name="ServerThread", daemon=True).start()
