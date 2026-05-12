from __future__ import annotations

from dataclasses import dataclass
from threading import Lock


@dataclass
class StreamStats:
    count: int = 0
    fps: float = 0.0


_uploads: dict[str, str] = {}
_stats: dict[str, StreamStats] = {}
_lock = Lock()


def register_upload(stream_id: str, path: str) -> None:
    _uploads[stream_id] = path


def get_upload_path(stream_id: str) -> str | None:
    return _uploads.get(stream_id)


def update_stats(stream_id: str, count: int, fps: float) -> None:
    with _lock:
        _stats[stream_id] = StreamStats(count=count, fps=fps)


def get_stats(stream_id: str) -> dict[str, float] | None:
    with _lock:
        stats = _stats.get(stream_id)
        if stats is None:
            return None
        return {"count": stats.count, "fps": stats.fps}
