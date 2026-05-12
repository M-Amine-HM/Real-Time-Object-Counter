import React from "react";

export default function VideoPanel({ streamUrl }) {
    if (!streamUrl) {
        return (
            <div className="video-placeholder">
                <p>Stream will appear here once started.</p>
            </div>
        );
    }

    return (
        <div className="video-shell">
            <img src={streamUrl} alt="Processed stream" />
        </div>
    );
}
