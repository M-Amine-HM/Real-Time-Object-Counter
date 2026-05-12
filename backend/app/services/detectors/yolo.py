from dataclasses import dataclass

import numpy as np

from app.config import VEHICLE_CLASSES, YOLO_MODEL_NAME


@dataclass
class YOLODetector:
    model_name: str = YOLO_MODEL_NAME

    def __post_init__(self) -> None:
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError(
                "Ultralytics is not installed. Run: pip install ultralytics"
            ) from exc

        self.model = YOLO(self.model_name)

    def detect(self, frame: np.ndarray) -> list[tuple[int, int, int, int]]:
        results = self.model(frame, verbose=False)[0]
        boxes: list[tuple[int, int, int, int]] = []

        for box in results.boxes:
            cls_index = int(box.cls[0])
            label = self.model.names.get(cls_index, "")
            if label not in VEHICLE_CLASSES:
                continue

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            boxes.append((int(x1), int(y1), int(x2), int(y2)))

        return boxes
