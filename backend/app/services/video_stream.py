from __future__ import annotations

import time
from typing import Generator

import cv2

from app.config import FRAME_WIDTH
from app.services.detectors.classical import ClassicalDetector
from app.services.detectors.yolo import YOLODetector
from app.services.line_counter import LineCounter
from app.services.tracking.centroid import CentroidTracker
from app.state import get_upload_path, update_stats


def build_detector(mode: str):
    if mode == "yolo":
        return YOLODetector()
    return ClassicalDetector()


def draw_overlay(
    frame,
    boxes,
    tracked,
    counter: LineCounter,
    fps: float,
) -> None:
    for (x1, y1, x2, y2) in boxes:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 180, 255), 2)

    for object_id, centroid in tracked.items():
        cv2.circle(frame, centroid, 4, (0, 255, 0), -1)
        cv2.putText(
            frame,
            f"ID {object_id}",
            (centroid[0] - 10, centroid[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
        )

    x1, y1, x2, y2 = counter.line
    cv2.line(frame, (x1, y1), (x2, y2), (255, 70, 70), 2)

    cv2.putText(
        frame,
        f"Count: {counter.total}",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (20, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )


def stream_generator(
    cap: cv2.VideoCapture,
    detector,
    line: tuple[int, int, int, int] | None,
    frame_skip: int,
    stream_id: str,
) -> Generator[bytes, None, None]:
    tracker = CentroidTracker()
    fps = 0.0
    last_time = time.time()

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if line is None or any(v is None for v in line):
        line = (0, int(height * 0.65), width, int(height * 0.65))

    counter = LineCounter(line=line)

    while True:
        for _ in range(frame_skip):
            cap.grab()

        success, frame = cap.read()
        if not success:
            break

        if FRAME_WIDTH and frame.shape[1] != FRAME_WIDTH:
            scale = FRAME_WIDTH / frame.shape[1]
            frame = cv2.resize(
                frame, (FRAME_WIDTH, int(frame.shape[0] * scale)))

        boxes = detector.detect(frame)
        tracked = tracker.update(boxes)

        for object_id, centroid in tracked.items():
            counter.update(object_id, centroid)

        now = time.time()
        fps = 1.0 / max(now - last_time, 1e-6)
        last_time = now

        draw_overlay(frame, boxes, tracked, counter, fps)

        update_stats(stream_id, counter.total, fps)

        success, buffer = cv2.imencode(".jpg", frame)
        if not success:
            continue

        payload = buffer.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + payload + b"\r\n"
        )

    cap.release()


def stream_from_video(
    stream_id: str,
    mode: str | None,
    frame_skip: int,
    line: tuple[int, int, int, int] | None,
):
    input_path = get_upload_path(stream_id)
    if input_path is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Upload not found")

    detector = build_detector(mode or "classical")
    cap = cv2.VideoCapture(input_path)

    return _stream_response(cap, detector, stream_id, line, frame_skip)


def stream_from_webcam(
    stream_id: str,
    mode: str,
    frame_skip: int,
    line: tuple[int, int, int, int] | None,
):
    detector = build_detector(mode)
    cap = cv2.VideoCapture(0)

    return _stream_response(cap, detector, stream_id, line, frame_skip)


def _stream_response(cap, detector, stream_id, line, frame_skip):
    from fastapi.responses import StreamingResponse

    generator = stream_generator(cap, detector, line, frame_skip, stream_id)
    return StreamingResponse(generator, media_type="multipart/x-mixed-replace; boundary=frame")
