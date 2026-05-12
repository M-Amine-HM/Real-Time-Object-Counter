from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from app.config import MAX_ASSOCIATION_DISTANCE, MAX_DISAPPEARED


@dataclass
class CentroidTracker:
    max_disappeared: int = MAX_DISAPPEARED
    max_distance: int = MAX_ASSOCIATION_DISTANCE
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
