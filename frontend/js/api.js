
const BASE_URL = "";

async function handleResponse(response) {
    const text = await response.text();
    try {
        return JSON.parse(text);
    } catch {
        return { raw: text, status: response.status };
    }
}

export async function apiGet(path) {
    const response = await fetch(`${BASE_URL}${path}`, {
        method: "GET",
        headers: { "Accept": "application/json" }
    });
    return handleResponse(response);
}

export async function apiPost(path, body) {
    const response = await fetch(`${BASE_URL}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(body || {})
    });
    return handleResponse(response);
}

export async function sendCommand(query) {
    const response = await fetch("/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
    });
    return handleResponse(response);
}