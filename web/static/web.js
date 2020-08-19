import * as api from "./api.js"

window.addEventListener("DOMContentLoaded", () => {
    document.getElementById("skip").addEventListener("click", async (e) => {
        await api.skip();
        update();
    });

    const current = document.getElementById("current-clip");

    async function update() {
        let info = await api.now();
        current.innerText = info.current;
    }

    update();
    window.setInterval(update, 3000);
});
