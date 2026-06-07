import React, { useMemo, useRef, useState } from "react";

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

export default function LinePlanner({ lineY, onLineYChange, loading }) {
    const boardRef = useRef(null);
    const [dragging, setDragging] = useState(false);

    const displayLineY = useMemo(() => clamp(lineY, 5, 95), [lineY]);

    const updateFromPointer = (event) => {
        const board = boardRef.current;
        if (!board) {
            return;
        }

        const rect = board.getBoundingClientRect();
        const next = ((event.clientY - rect.top) / rect.height) * 100;
        onLineYChange(clamp(Math.round(next), 5, 95));
    };

    const handlePointerDown = (event) => {
        if (loading) {
            return;
        }

        event.preventDefault();
        setDragging(true);
        updateFromPointer(event);
        event.currentTarget.setPointerCapture?.(event.pointerId);
    };

    const handlePointerMove = (event) => {
        if (!dragging) {
            return;
        }

        updateFromPointer(event);
    };

    const stopDragging = () => {
        setDragging(false);
    };

    return (
        <section className="panel-row line-planner">
            <div className="selector-header">
                <label className="label">Choose Counting Line</label>
                <span className="selector-count">{displayLineY}% from top</span>
            </div>
            <div
                ref={boardRef}
                className={`line-board ${dragging ? "dragging" : ""} ${loading ? "disabled" : ""}`}
                onPointerDown={handlePointerDown}
                onPointerMove={handlePointerMove}
                onPointerUp={stopDragging}
                onPointerCancel={stopDragging}
                onLostPointerCapture={stopDragging}
                role="slider"
                aria-label="Counting line placement board"
                aria-valuemin={5}
                aria-valuemax={95}
                aria-valuenow={displayLineY}
                tabIndex={0}
            >
                <div className="line-board-grid" />
                <div className="line-board-line" style={{ top: `${displayLineY}%` }}>
                    <span className="line-board-handle" />
                    <span className="line-board-label">Line</span>
                </div>
            </div>
            <p className="helper-text">Place the line here before uploading the video or starting the webcam.</p>
        </section>
    );
}
