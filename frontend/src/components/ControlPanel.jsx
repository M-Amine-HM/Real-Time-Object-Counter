import React from "react";

export default function ControlPanel({
    uploadType,
    onUploadTypeChange,
    onUpload,
    onStartWebcam,
    onStopWebcam,
    isStreaming,
    loading
}) {
    return (
        <section className="panel">
            <div className="panel-row">
                <label className="label">Upload Type</label>
                <select
                    className="select"
                    value={uploadType}
                    onChange={(event) => onUploadTypeChange(event.target.value)}
                    disabled={loading}
                >
                    <option value="video">Video</option>
                    <option value="image">Image</option>
                </select>
            </div>

            <div className="panel-row">
                <label className="label">Upload File</label>
                <input
                    className="file"
                    type="file"
                    accept={uploadType === "image" ? "image/*" : "video/*"}
                    onChange={onUpload}
                    disabled={loading}
                />
            </div>

            <div className="panel-row">
                <label className="label">Webcam</label>
                <div className="button-row">
                    <button className="button" onClick={onStartWebcam} disabled={loading || isStreaming}>
                        Start
                    </button>
                    <button className="button ghost" onClick={onStopWebcam} disabled={loading || !isStreaming}>
                        Stop
                    </button>
                </div>
            </div>
        </section>
    );
}
