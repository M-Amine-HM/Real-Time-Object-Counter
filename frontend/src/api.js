const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export function buildStreamUrl(path) {
    return `${API_BASE}${path}`;
}

export async function uploadVideo(formData) {
    const response = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        throw new Error("Upload failed");
    }

    return response.json();
}

export async function fetchStats(streamId) {
    const response = await fetch(`${API_BASE}/stats/${streamId}`);
    if (!response.ok) {
        throw new Error("Stats not available");
    }
    return response.json();
}
