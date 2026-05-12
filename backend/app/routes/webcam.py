from fastapi import APIRouter

from app.config import FRAME_SKIP, USE_YOLO_DEFAULT
from app.services.video_stream import stream_from_webcam

router = APIRouter()


@router.get("/webcam")
def webcam_stream(
    mode: str | None = None,
    stream_id: str = "webcam",
    frame_skip: int = FRAME_SKIP,
    line_x1: int | None = None,
    line_y1: int | None = None,
    line_x2: int | None = None,
    line_y2: int | None = None,
):
    chosen_mode = mode or ("yolo" if USE_YOLO_DEFAULT else "classical")
    return stream_from_webcam(
        stream_id=stream_id,
        mode=chosen_mode,
        frame_skip=frame_skip,
        line=(line_x1, line_y1, line_x2, line_y2),
    )
