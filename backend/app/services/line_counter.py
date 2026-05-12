from dataclasses import dataclass, field


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
