from __future__ import annotations

import shutil
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Generator

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

try:
    from ultralytics import YOLO
except ImportError as exc:
    raise RuntimeError(
        "Ultralytics is not installed. Run: pip install ultralytics") from exc


APP_TITLE = "Object Detection and Counting"
MODEL_NAME = "yolov8n.pt"
FRAME_WIDTH = 960
FRAME_SKIP = 0
# DETECT_CLASSES = {"car", "truck", "bus", "motorbike"}
DETECT_CLASSES = {"car", "person"}
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class CentroidTracker:
    max_disappeared: int = 20
    max_distance: int = 70
    next_object_id: int = 0
    objects: dict[int, tuple[int, int]] = field(default_factory=dict)
    disappeared: dict[int, int] = field(default_factory=dict)

    def register(self, centroid: tuple[int, int]) -> None:
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id: int) -> None:
        self.objects.pop(object_id, None)
        self.disappeared.pop(object_id, None)

    def update(
        self, rects: list[tuple[int, int, int, int]]
    ) -> dict[int, tuple[int, int]]:
        if len(rects) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        input_centroids = np.zeros((len(rects), 2), dtype="int")
        for i, (x1, y1, x2, y2) in enumerate(rects):
            c_x = int((x1 + x2) / 2.0)
            c_y = int((y1 + y2) / 2.0)
            input_centroids[i] = (c_x, c_y)

        if len(self.objects) == 0:
            for i in range(len(input_centroids)):
                self.register(tuple(input_centroids[i]))
            return self.objects

        object_ids = list(self.objects.keys())
        object_centroids = np.array(list(self.objects.values()))

        distances = np.linalg.norm(
            object_centroids[:, None] - input_centroids[None, :], axis=2)
        rows = distances.min(axis=1).argsort()
        cols = distances.argmin(axis=1)[rows]

        used_rows = set()
        used_cols = set()

        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue

            if distances[row, col] > self.max_distance:
                continue

            object_id = object_ids[row]
            self.objects[object_id] = tuple(input_centroids[col])
            self.disappeared[object_id] = 0

            used_rows.add(row)
            used_cols.add(col)

        unused_rows = set(range(distances.shape[0])).difference(used_rows)
        unused_cols = set(range(distances.shape[1])).difference(used_cols)

        if distances.shape[0] >= distances.shape[1]:
            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
        else:
            for col in unused_cols:
                self.register(tuple(input_centroids[col]))

        return self.objects


@dataclass
class LineCounter:
    line: tuple[int, int, int, int]
    total: int = 0
    last_side: dict[int, int] = field(default_factory=dict)

    def _side(self, point: tuple[int, int]) -> int:
        x1, y1, x2, y2 = self.line
        px, py = point
        value = (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
        if value > 0:
            return 1
        if value < 0:
            return -1
        return 0

    def update(self, object_id: int, centroid: tuple[int, int]) -> bool:
        current_side = self._side(centroid)
        last_side = self.last_side.get(object_id)
        crossed = False

        if last_side is not None and current_side != 0 and last_side != current_side:
            self.total += 1
            crossed = True

        self.last_side[object_id] = current_side
        return crossed


@dataclass
class StreamStats:
    count: int = 0
    fps: float = 0.0


_stats: dict[str, StreamStats] = {}
_uploads: dict[str, str] = {}
_images: dict[str, str] = {}
_lock = Lock()


class YOLODetector:
    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self.model = YOLO(model_name)

    def detect(self, frame: np.ndarray) -> list[tuple[int, int, int, int]]:
        results = self.model(frame, verbose=False)[0]
        boxes: list[tuple[int, int, int, int]] = []

        for box in results.boxes:
            cls_index = int(box.cls[0])
            label = self.model.names.get(cls_index, "")
            if DETECT_CLASSES and label not in DETECT_CLASSES:
                continue

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            boxes.append((int(x1), int(y1), int(x2), int(y2)))

        return boxes


app = FastAPI(title=APP_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _update_stats(stream_id: str, count: int, fps: float) -> None:
    with _lock:
        _stats[stream_id] = StreamStats(count=count, fps=fps)


def _get_stats(stream_id: str) -> dict[str, float] | None:
    with _lock:
        stats = _stats.get(stream_id)
        if stats is None:
            return None
        return {"count": stats.count, "fps": stats.fps}


def _draw_overlay(frame, boxes, tracked, counter: LineCounter, fps: float) -> None:
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


def _draw_image_overlay(frame, boxes, count: int) -> None:
    for (x1, y1, x2, y2) in boxes:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 180, 255), 2)

    cv2.putText(
        frame,
        f"Count: {count}",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2,
    )


def _stream_generator(
    cap: cv2.VideoCapture,
    detector: YOLODetector,
    stream_id: str,
) -> Generator[bytes, None, None]:
    tracker = CentroidTracker()
    fps = 0.0
    last_time = time.time()

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    line = (0, int(height * 0.65), width, int(height * 0.65))
    counter = LineCounter(line=line)

    while True:
        for _ in range(FRAME_SKIP):
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

        _draw_overlay(frame, boxes, tracked, counter, fps)
        _update_stats(stream_id, counter.total, fps)

        success, buffer = cv2.imencode(".jpg", frame)
        if not success:
            continue

        payload = buffer.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + payload + b"\r\n"
        )

    cap.release()


def _stream_response(cap: cv2.VideoCapture, detector: YOLODetector, stream_id: str):
    generator = _stream_generator(cap, detector, stream_id)
    return StreamingResponse(generator, media_type="multipart/x-mixed-replace; boundary=frame")


@app.post("/upload")
def upload_video(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    input_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    with input_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    _uploads[file_id] = str(input_path)
    return {"stream_id": file_id, "stream_url": f"/stream/{file_id}"}


@app.post("/image")
def upload_image(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    input_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    with input_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    frame = cv2.imread(str(input_path))
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    if FRAME_WIDTH and frame.shape[1] != FRAME_WIDTH:
        scale = FRAME_WIDTH / frame.shape[1]
        frame = cv2.resize(frame, (FRAME_WIDTH, int(frame.shape[0] * scale)))

    detector = YOLODetector()
    boxes = detector.detect(frame)
    _draw_image_overlay(frame, boxes, len(boxes))

    output_path = OUTPUT_DIR / f"{file_id}.jpg"
    cv2.imwrite(str(output_path), frame)

    _images[file_id] = str(output_path)
    _update_stats(file_id, len(boxes), 0.0)

    return {"image_id": file_id, "image_url": f"/image/{file_id}", "count": len(boxes)}


@app.get("/stream/{stream_id}")
def stream_uploaded_video(stream_id: str):
    input_path = _uploads.get(stream_id)
    if input_path is None:
        raise HTTPException(status_code=404, detail="Upload not found")

    detector = YOLODetector()
    cap = cv2.VideoCapture(input_path)
    return _stream_response(cap, detector, stream_id)


@app.get("/image/{image_id}")
def get_image(image_id: str):
    image_path = _images.get(image_id)
    if image_path is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path, media_type="image/jpeg")


@app.get("/webcam")
def webcam_stream():
    detector = YOLODetector()
    cap = cv2.VideoCapture(0)
    return _stream_response(cap, detector, "webcam")


@app.get("/stats/{stream_id}")
def stats(stream_id: str):
    payload = _get_stats(stream_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Stream not found")
    return payload
