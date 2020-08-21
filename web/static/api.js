const API_PATH = "http://" + window.location.host + "/api/v1.0";
console.log("API path", API_PATH);

/**
 * @typedef {"GET"|"POST"|"PUT"|"DELETE"} HTTPMethod
 */

/**
 * Makes an API requests and returns the requested data
 * as an object. If the API returns with status="error"
 * the promise will be rejected.
 * @param {string} path 
 * @param {HTTPMethod} method 
 */
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

/**
 * Makes a request to the /now API and returns results.
 * @returns {Promise<{
 *  "status":"ok",
 *  "current": string,
 *  "history": string[],
 *  "library": {"hosts": number, "music": number, "other": number}
 * }>}
 */
export function now() {
    return api_request("/now");
}

/**
 * Get a list of available extensions.
 * @returns {Promise<{
 *  "status": "ok",
 *  "extensions": {"name": string, "command": string}[]
 * }>}
 */
export async function get_extensions() {
    let obj = await api_request("/extensions", "GET");
    return obj.extensions;
}

/**
 * @callback buttonAPICallback
 * @param {"status": "ok"} response
 */

/**
 * 
 * @param {HTMLButtonElement} btn 
 * @param {string} path 
 * @param {HTTPMethod} method 
 * @param {buttonAPICallback} onsuccess 
 */
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
