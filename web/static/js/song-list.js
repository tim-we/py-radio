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
    let div = document.createElement("div");
    div.classList.add("song");

    let compontents = song.split("/");
    let folder = compontents.slice(0, compontents.length-1).join("/");
    if(folder.length > 0) {
        let folder_span = document.createElement("span");
        folder_span.innerText = folder + "/";
        folder_span.classList.add("folder");
        div.appendChild(folder_span);
    }
    
    let file_span = document.createElement("span");
    file_span.innerText = compontents[compontents.length - 1];
    file_span.classList.add("file");
    div.appendChild(file_span);

    return div;
}
