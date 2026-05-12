import React, { useEffect, useRef, useState } from "react";
import ControlPanel from "./components/ControlPanel.jsx";
import VideoPanel from "./components/VideoPanel.jsx";
import StatCard from "./components/StatCard.jsx";
import { buildStreamUrl, fetchStats, uploadImage, uploadVideo } from "./api.js";

export default function App() {
    const [streamUrl, setStreamUrl] = useState("");
    const [streamId, setStreamId] = useState("");
    const [stats, setStats] = useState({ count: 0, fps: 0 });
    const [loading, setLoading] = useState(false);
    const [isStreaming, setIsStreaming] = useState(false);
    const [uploadType, setUploadType] = useState("video");
    const pollingRef = useRef(null);

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

        try {
            if (uploadType === "image") {
                const response = await uploadImage(formData);
                const url = buildStreamUrl(response.image_url);
                setStreamUrl(url);
                setStreamId(response.image_id);
                setIsStreaming(false);
                setStats({ count: response.count ?? 0, fps: 0 });
            } else {
                const response = await uploadVideo(formData);
                const url = buildStreamUrl(response.stream_url);
                setStreamUrl(url);
                setStreamId(response.stream_id);
                setIsStreaming(true);
                startPolling(response.stream_id);
            }
        } catch (error) {
            setIsStreaming(false);
        } finally {
            setLoading(false);
        }
    };

    const handleStartWebcam = () => {
        stopPolling();
        const url = buildStreamUrl("/webcam");
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

    useEffect(() => {
        return () => stopPolling();
    }, []);

    return (
        <div className="page">
            <header className="hero">
                <div>
                    <p className="eyebrow">YOLO Detection Suite</p>
                    <h1>Object Detection and Counting</h1>
                    <p className="subtitle">
                        YOLO-powered detection with live counts and FPS.
                    </p>
                </div>
                <div className="stat-grid">
                    <StatCard label="Objects" value={stats.count} />
                    <StatCard label="FPS" value={stats.fps.toFixed(1)} />
                </div>
            </header>

            <main className="layout">
                <ControlPanel
                    uploadType={uploadType}
                    onUploadTypeChange={setUploadType}
                    onUpload={handleUpload}
                    onStartWebcam={handleStartWebcam}
                    onStopWebcam={handleStopWebcam}
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
                <p>Tip: Update the YOLO class list in the backend to target other objects.</p>
            </footer>
        </div>
    );
}
