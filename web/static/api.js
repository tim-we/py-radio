const API_PATH = "http://" + window.location.host + "/api/v1.0";
console.log("API path", API_PATH);

export async function api_request(path, method = "GET") {
    let init = {
        method: method,
        cache: "no-store",
        follow: "error"
    };
    let response = await fetch(API_PATH + path, init);
    let obj = await response.json();
    return obj.status === "ok" ? Promise.resolve(obj) : Promise.reject(obj);
} 

export function now() {
    return api_request("/now");
}

export async function get_extensions() {
    let obj = await api_request("/extensions", "GET");
    return obj.extensions;
}

export function button(btn, path, method = "GET", onsuccess) {
    btn.addEventListener("click", async (e) => {
        if(btn.classList.contains("active")) {
            console.log("Ignoring button click because it is still active.");
            return;
        }
        
        btn.classList.add("active");
        let success = true;
        await api_request(path, method).catch(
            e => {
                console.error(e);
                success = false;
                alert(e.message || "operation failed");
            }
        );
        btn.classList.remove("active");

        if(success) {
            onsuccess();
        }
    });
}
