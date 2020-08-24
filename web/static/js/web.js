import * as api from "./api.js";
import * as list from "./song-list.js";

window.addEventListener("DOMContentLoaded", async () => {
    api.button(document.getElementById("pause"), "/pause", "POST", update)
    api.button(document.getElementById("skip"), "/skip", "PUT", update);
    api.button(document.getElementById("repeat"), "/repeat", "PUT", update);
    
    document.getElementById("song-list-button").addEventListener("click", list.open);

    const current = document.getElementById("current-clip");
    const history = document.getElementById("history-clips");

    /**
     * @type {string[]}
     */
    let last_history = [];

    async function update() {
        if(document.hidden) {
            return;
        }
        
        let info = await api.now();

        // update "Now playing"
        if(current.innerText !== info.current) {
            current.innerText = info.current;
        }

        // update history section
        let history_changed = last_history.length !== info.history.length;
        if(!history_changed && last_history.length > 0) {
            let idx = last_history.length-1;
            history_changed = history_changed || last_history[idx] !== info.history[idx];
        }
        if(history_changed) {
            last_history = info.history;
            history.innerHTML = "";
            info.history.forEach(clip => {
                let elem = document.createElement("div");
                elem.classList.add("clip");
                elem.innerText = clip;
                history.prepend(elem);
            });
        }
    }

    document.addEventListener("visibilitychange", function() {
        if (document.visibilityState === "visible") {
            update();
        }
    });

    update();
    window.setInterval(update, 3141);

    const extensions = await api.get_extensions();

    for(const ext of extensions) {
        let btn = document.createElement("button");
        btn.title = ext.name;
        btn.innerText = ext.command;
        document.getElementById("controls").prepend(btn);
        api.button(btn, `/extensions/${ext.command}/schedule`, "PUT", update);
    }
});
