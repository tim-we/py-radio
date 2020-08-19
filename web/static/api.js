const API_PATH = "http://" + window.location.host + "/api/v1.0";
console.log("API path", API_PATH);

export async function now() {
    let response = await fetch(API_PATH + "/now");
    return response.json();
}

export async function skip() {
    let response = await fetch(API_PATH + "/skip", {method: "PUT"});
    return response.json();
}
