from dataclasses import dataclass

import cv2
import numpy as np

from app.config import MIN_ASPECT_RATIO, MIN_CONTOUR_AREA


@dataclass
class ClassicalDetector:
    history: int = 500
    var_threshold: int = 16
    detect_shadows: bool = True

    def __post_init__(self) -> None:
        self.subtractor = cv2.createBackgroundSubtractorMOG2(
            history=self.history,
            varThreshold=self.var_threshold,
            detectShadows=self.detect_shadows,
        )

    def detect(self, frame: np.ndarray) -> list[tuple[int, int, int, int]]:
        mask = self.subtractor.apply(frame)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.dilate(mask, kernel, iterations=2)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes: list[tuple[int, int, int, int]] = []

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < MIN_CONTOUR_AREA:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            if h == 0:
                continue

            aspect_ratio = w / float(h)
            if aspect_ratio < MIN_ASPECT_RATIO:
                continue

            boxes.append((x, y, x + w, y + h))

        return boxes
