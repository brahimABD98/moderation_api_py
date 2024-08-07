import atexit
import subprocess
from datetime import datetime
from uuid import UUID

from celery.result import AsyncResult
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.app_settings import Settings
from src.celery_config import (
    celery_app,
    stop_celery_worker,
    stop_flower_worker,
    start_celery_worker,
    start_flower_worker,
)
from src.model import Moderation
from src.schemas import (
    ModerationRequestResponse,
    is_valid_uuid,
    ModerationResultResponse,
)
from src.tasks import vid_moderation_task

now = str(datetime.now())
settings = Settings()
app = FastAPI(
    title="moderation_api_py",
    description="text and image moderation with pretrained AI models with celery-redis queue system",
    version="0.1",
    contact={"github": "github.com/brahimabd98", "twitter/x": "@crabgpt"},
    license_info={
        "name": "GPL v3.0",
        "url": "https://www.gnu.org/licenses/gpl-3.0.en.html",
    },
)
model = Moderation()
celery_worker: subprocess.Popen
flower_worker: subprocess.Popen
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    global celery_worker, flower_worker
    celery_worker = start_celery_worker()
    flower_worker = start_flower_worker()


@app.on_event("shutdown")
async def shutdown():
    global celery_worker, flower_worker
    stop_celery_worker(celery_worker)
    stop_flower_worker(flower_worker)


@app.get("/")
async def root():
    return {
        "message": "Hello World",
    }


@app.post(
    "/api/v1/moderation/image",
    tags=["moderation", "image"],
    response_model=ModerationRequestResponse,
)
async def image_moderation(image: UploadFile):
    enc_image = await image.read()
    task = celery_app.send_task("src.tasks.image_moderation_task", args=[enc_image])
    return ModerationRequestResponse(task_id=task.id, created_at=now)


@app.post(
    "/api/v1/moderation/text",
    tags=["moderation", "text"],
    response_model=ModerationRequestResponse,
)
async def text_moderation(text: str):
    task = celery_app.send_task("src.tasks.text_moderation_task", args=[text])
    return ModerationRequestResponse(task_id=task.id, created_at=now)


@app.post(
    "/api/v1/moderation/video",
    tags=["moderation", "video"],
    response_model=ModerationRequestResponse,
)
async def video_moderation(file: UploadFile):
    video_buffer = await file.read()
    task = vid_moderation_task.apply_async(args=[video_buffer])
    return ModerationRequestResponse(task_id=task.id, created_at=now)


@app.get(
    "/api/v1/moderation/{task_id}",
    tags=["moderation"],
    response_model=ModerationResultResponse,
)
async def moderation_status(task_id: UUID):
    task_result = AsyncResult(str(task_id))
    if is_valid_uuid(task_result.result):
        task_result = AsyncResult(task_result.result)
    return ModerationResultResponse(
        task_id=task_result.id,
        task_status=task_result.status,
        task_result=task_result.result,
    )


atexit.register(stop_celery_worker)
atexit.register(stop_flower_worker)
