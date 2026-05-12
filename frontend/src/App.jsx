import React, { useEffect, useMemo, useRef, useState } from "react";
import ControlPanel from "./components/ControlPanel.jsx";
import VideoPanel from "./components/VideoPanel.jsx";
import StatCard from "./components/StatCard.jsx";
import { buildStreamUrl, fetchStats, uploadVideo } from "./api.js";

const DEFAULT_LINE = [0, 420, 960, 420];

export default function App() {
    const [mode, setMode] = useState("yolo");
    const [streamUrl, setStreamUrl] = useState("");
    const [streamId, setStreamId] = useState("");
    const [stats, setStats] = useState({ count: 0, fps: 0 });
    const [loading, setLoading] = useState(false);
    const [line, setLine] = useState(DEFAULT_LINE);
    const [isStreaming, setIsStreaming] = useState(false);
    const pollingRef = useRef(null);

    const lineParams = useMemo(() => {
        const [x1, y1, x2, y2] = line.map((value) => Number(value) || 0);
        return `line_x1=${x1}&line_y1=${y1}&line_x2=${x2}&line_y2=${y2}`;
    }, [line]);

    const startPolling = (id) => {
        if (pollingRef.current) {
            clearInterval(pollingRef.current);
        }

        pollingRef.current = setInterval(async () => {
            try {
                const payload = await fetchStats(id);
                setStats({
                    count: payload.count ?? 0,
                    fps: payload.fps ?? 0
                });
            } catch (error) {
                setStats({ count: 0, fps: 0 });
            }
        }, 1000);
    };

    const stopPolling = () => {
        if (pollingRef.current) {
            clearInterval(pollingRef.current);
            pollingRef.current = null;
        }
    };

    const handleUpload = async (event) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setLoading(true);
        stopPolling();

        const formData = new FormData();
        formData.append("file", file);
        formData.append("mode", mode);

        try {
            const response = await uploadVideo(formData);
            const url = buildStreamUrl(`${response.stream_url}&${lineParams}`);
            setStreamUrl(url);
            setStreamId(response.stream_id);
            setIsStreaming(true);
            startPolling(response.stream_id);
        } catch (error) {
            setIsStreaming(false);
        } finally {
            setLoading(false);
        }
    };

    const handleStartWebcam = () => {
        stopPolling();
        const url = buildStreamUrl(`/webcam?mode=${mode}&${lineParams}`);
        setStreamUrl(url);
        setStreamId("webcam");
        setIsStreaming(true);
        startPolling("webcam");
    };

    const handleStopWebcam = () => {
        setStreamUrl("");
        setIsStreaming(false);
        stopPolling();
    };

    const handleLineChange = (index, value) => {
        const updated = [...line];
        updated[index] = value;
        setLine(updated);
    };

    useEffect(() => {
        return () => stopPolling();
    }, []);

    return (
        <div className="page">
            <header className="hero">
                <div>
                    <p className="eyebrow">Vehicle Detection Suite</p>
                    <h1>Vehicle Detection and Counting</h1>
                    <p className="subtitle">
                        Switch between classical motion detection and YOLO vehicle recognition.
                    </p>
                </div>
                <div className="stat-grid">
                    <StatCard label="Vehicles" value={stats.count} />
                    <StatCard label="FPS" value={stats.fps.toFixed(1)} />
                </div>
            </header>

            <main className="layout">
                <ControlPanel
                    mode={mode}
                    onModeChange={setMode}
                    onUpload={handleUpload}
                    onStartWebcam={handleStartWebcam}
                    onStopWebcam={handleStopWebcam}
                    line={line}
                    onLineChange={handleLineChange}
                    isStreaming={isStreaming}
                    loading={loading}
                />

                <section className="panel video-panel">
                    <div className="panel-header">
                        <p>Processed Stream</p>
                        {loading && <span className="badge">Loading...</span>}
                    </div>
                    <VideoPanel streamUrl={streamUrl} />
                </section>
            </main>

            <footer className="footer">
                <p>
                    Tip: Adjust the line coordinates to match the roadway in your scene.
                </p>
            </footer>
        </div>
    );
}
