import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile

from app.config import FRAME_SKIP, USE_YOLO_DEFAULT
from app.services.video_stream import stream_from_video
from app.state import register_upload

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
def upload_video(
    file: UploadFile = File(...),
    mode: str | None = Form(None),
    stream_id: str | None = None,
    frame_skip: int = FRAME_SKIP,
    line_x1: int | None = None,
    line_y1: int | None = None,
    line_x2: int | None = None,
    line_y2: int | None = None,
):
    file_id = stream_id or str(uuid.uuid4())
    input_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    with input_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    register_upload(file_id, str(input_path))

    chosen_mode = mode or ("yolo" if USE_YOLO_DEFAULT else "classical")
    stream_url = f"/stream/{file_id}?mode={chosen_mode}&frame_skip={frame_skip}"

    if all(v is not None for v in [line_x1, line_y1, line_x2, line_y2]):
        stream_url += (
            f"&line_x1={line_x1}&line_y1={line_y1}&line_x2={line_x2}&line_y2={line_y2}"
        )

    return {"stream_id": file_id, "stream_url": stream_url}


@router.get("/stream/{stream_id}")
def stream_uploaded_video(
    stream_id: str,
    mode: str | None = None,
    frame_skip: int = FRAME_SKIP,
    line_x1: int | None = None,
    line_y1: int | None = None,
    line_x2: int | None = None,
    line_y2: int | None = None,
):
    return stream_from_video(
        stream_id=stream_id,
        mode=mode,
        frame_skip=frame_skip,
        line=(line_x1, line_y1, line_x2, line_y2),
    )
