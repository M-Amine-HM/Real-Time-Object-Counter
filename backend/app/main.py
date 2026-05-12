from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.upload import router as upload_router
from app.routes.webcam import router as webcam_router
from app.routes.stats import router as stats_router

app = FastAPI(title="Vehicle Detection and Counting")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(webcam_router)
app.include_router(stats_router)
