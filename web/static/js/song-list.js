import * as api from "./api.js"

export function open() {
    filter_input.value = "";
    clear();
    container.classList.add("show");
    filter_input.focus();
}

export function close() {
    container.classList.remove("show");
}

/** @type {HTMLDivElement} */
let container, list_output;
/** @type {HTMLInputElement} */
let filter_input;

window.addEventListener("DOMContentLoaded", async () => {
    container = document.getElementById("song-list-container");
    filter_input = document.getElementById("song-filter");
    list_output = document.getElementById("song-list");

    document.getElementById("song-list-close").addEventListener("click", close);

    filter_input.addEventListener("input", async () => {
        let filter = filter_input.value.trim();
        if(filter === "") {
            clear();
        } else if(filter.length > 1) {
            let results = await api.search(filter);
            clear();
            results.forEach(song => list_output.appendChild(song_to_div(song)));
        }
    });

    container.addEventListener("click", e => {
        e.stopPropagation();
        close();
    });

    document.getElementById("song-list-modal").addEventListener("click", e => {
        e.stopPropagation();
    });
});

function clear() {
    list_output.innerHTML = "";
}

/**
 * @param {string} song 
 * @returns {HTMLDivElement}
 */
function song_to_div(song) {
    let compontents = song.split("/");
    let folder = compontents.slice(0, compontents.length-1).join("/");
    let filename = compontents[compontents.length - 1];

    let div = document.createElement("div");
    div.classList.add("song");
    div.addEventListener("click", e => {
        e.stopPropagation();
        if(window.getSelection().type !== "Range") {
            if(!div.classList.contains("expanded")) {
                let other = list_output.querySelector("div.song.expanded");
                if(other) {
                    other.classList.remove("expanded");
                }
            }
            div.classList.toggle("expanded");
        }
    });

    let main = document.createElement("div");
    main.classList.add("main");
    div.appendChild(main);
    {
        if(folder.length > 0) {
            let folder_span = document.createElement("span");
            folder_span.innerText = folder + "/";
            folder_span.classList.add("folder");
            main.appendChild(folder_span);
        }
        
        let file_span = document.createElement("span");
        file_span.innerText = filename
        file_span.classList.add("file");
        main.appendChild(file_span);
    }
    
    let buttons = document.createElement("div");
    buttons.classList.add("buttons");
    div.appendChild(buttons);
    {
        let add_button = document.createElement("a");
        add_button.classList.add("add");
        add_button.addEventListener("click", async (e) => {
            e.preventDefault();
            e.stopPropagation();
            await api.schedule(song);
            alert(filename + " added to queue.");
        });
        add_button.href = "#";
        add_button.textContent = "add to queue";
        buttons.appendChild(add_button);

        let download_button = document.createElement("a");
        download_button.classList.add("download");
        download_button.textContent = "download";
        download_button.href = api.get_download_url(song);
        download_button.download = download_button.href;
        download_button.addEventListener("click", e => e.stopPropagation());
        buttons.appendChild(download_button);
    }

    return div;
}
