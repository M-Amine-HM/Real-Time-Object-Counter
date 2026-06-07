import React, { useEffect, useRef, useState } from "react";
import ControlPanel from "./components/ControlPanel.jsx";
import VideoPanel from "./components/VideoPanel.jsx";
import StatCard from "./components/StatCard.jsx";
import { buildStreamUrl, fetchClasses, fetchStats, uploadImage, uploadVideo } from "./api.js";

const DEFAULT_CLASSES = ["car", "truck", "bus", "motorcycle"];

export default function App() {
    const [streamUrl, setStreamUrl] = useState("");
    const [streamId, setStreamId] = useState("");
    const [stats, setStats] = useState({ count: 0, fps: 0 });
    const [loading, setLoading] = useState(false);
    const [isStreaming, setIsStreaming] = useState(false);
    const [uploadType, setUploadType] = useState("video");
    const [availableClasses, setAvailableClasses] = useState([]);
    const [selectedClasses, setSelectedClasses] = useState(DEFAULT_CLASSES);
    const [lineY, setLineY] = useState(65);
    const pollingRef = useRef(null);

    useEffect(() => {
        const loadClasses = async () => {
            try {
                const classList = await fetchClasses();
                setAvailableClasses(classList);
            } catch (error) {
                setAvailableClasses(DEFAULT_CLASSES);
            }
        };

        loadClasses();
    }, []);

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
        formData.append("classes", selectedClasses.join(","));
        formData.append("line_y", String(lineY));

        try {
            if (uploadType === "image") {
                const response = await uploadImage(formData, {
                    classes: selectedClasses,
                    lineY
                });
                const url = buildStreamUrl(response.image_url);
                setStreamUrl(url);
                setStreamId(response.image_id);
                setIsStreaming(false);
                setStats({ count: response.count ?? 0, fps: 0 });
            } else {
                const response = await uploadVideo(formData, {
                    classes: selectedClasses,
                    lineY
                });
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
        const url = buildStreamUrl("/webcam", {
            classes: selectedClasses,
            lineY
        });
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
                    classes={availableClasses}
                    selectedClasses={selectedClasses}
                    onSelectedClassesChange={setSelectedClasses}
                    lineY={lineY}
                    onLineYChange={setLineY}
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
                    <VideoPanel
                        streamUrl={streamUrl}
                    />
                </section>
            </main>

            <footer className="footer">
                <p>Tip: Update the YOLO class list in the backend to target other objects.</p>
            </footer>
        </div>
    );
}
