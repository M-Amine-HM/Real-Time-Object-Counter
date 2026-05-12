from fastapi import APIRouter, HTTPException

from app.state import get_stats

router = APIRouter()


@router.get("/stats/{stream_id}")
def stats(stream_id: str):
    payload = get_stats(stream_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Stream not found")
    return payload
