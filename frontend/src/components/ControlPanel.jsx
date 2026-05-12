import React from "react";

const MODES = [
    { value: "classical", label: "Classical (MOG2)" },
    { value: "yolo", label: "YOLO (Vehicle classes)" }
];

export default function ControlPanel({
    mode,
    onModeChange,
    onUpload,
    onStartWebcam,
    onStopWebcam,
    line,
    onLineChange,
    isStreaming,
    loading
}) {
    return (
        <section className="panel">
            <div className="panel-row">
                <label className="label">Detection Mode</label>
                <select
                    className="select"
                    value={mode}
                    onChange={(event) => onModeChange(event.target.value)}
                    disabled={loading}
                >
                    {MODES.map((item) => (
                        <option key={item.value} value={item.value}>
                            {item.label}
                        </option>
                    ))}
                </select>
            </div>

            <div className="panel-row">
                <label className="label">Upload Video</label>
                <input
                    className="file"
                    type="file"
                    accept="video/*"
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

            <div className="panel-row">
                <label className="label">Counting Line (x1,y1,x2,y2)</label>
                <div className="line-grid">
                    {line.map((value, index) => (
                        <input
                            key={index}
                            type="number"
                            className="input"
                            value={value}
                            onChange={(event) => onLineChange(index, event.target.value)}
                            disabled={loading}
                        />
                    ))}
                </div>
            </div>
        </section>
    );
}
