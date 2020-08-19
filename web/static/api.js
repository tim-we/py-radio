const API_PATH = "http://" + window.location.host + "/api/v1.0";
console.log("API path", API_PATH);

async function simple_req(path, method = "GET") {
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
    return simple_req("/now");
}

export function skip() {
    return simple_req("/skip", "PUT");
}

export function pause() {
    return simple_req("/pause", "POST");
}
