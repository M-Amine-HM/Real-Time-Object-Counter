const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function appendQueryParams(url, options = {}) {
    const params = new URLSearchParams();

    if (Array.isArray(options.classes) && options.classes.length > 0) {
        params.set("classes", options.classes.join(","));
    }

    if (typeof options.lineY === "number") {
        params.set("line_y", String(options.lineY));
    }

    const query = params.toString();
    return query ? `${url}?${query}` : url;
}

export function buildStreamUrl(path, options = {}) {
    return appendQueryParams(`${API_BASE}${path}`, options);
}

export async function uploadVideo(formData, options = {}) {
    const response = await fetch(appendQueryParams(`${API_BASE}/upload`, options), {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        throw new Error("Upload failed");
    }

    return response.json();
}

export async function uploadImage(formData, options = {}) {
    const response = await fetch(appendQueryParams(`${API_BASE}/image`, options), {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        throw new Error("Image upload failed");
    }

    return response.json();
}

export async function fetchClasses() {
    const response = await fetch(`${API_BASE}/classes`);
    if (!response.ok) {
        throw new Error("Classes not available");
    }

    const payload = await response.json();
    return payload.classes ?? [];
}

export async function fetchStats(streamId) {
    const response = await fetch(`${API_BASE}/stats/${streamId}`);
    if (!response.ok) {
        throw new Error("Stats not available");
    }
    return response.json();
}
