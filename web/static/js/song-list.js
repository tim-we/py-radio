import * as api from "./api.js"

/** @type {HTMLDivElement} */
let container, list_output, close_button;
/** @type {HTMLInputElement} */
let filter_input;

window.addEventListener("DOMContentLoaded", async () => {
    container = document.getElementById("song-list-container");
    filter_input = document.getElementById("song-filter");
    list_output = document.getElementById("song-list");
    close_button = document.getElementById("song-list-close");

    close_button.addEventListener("click", close);
});

export function open() {
    filter_input.value = "";
    container.classList.add("show");
    filter_input.focus();
}

export function close() {
    container.classList.remove("show");
}
