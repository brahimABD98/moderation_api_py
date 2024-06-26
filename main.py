import atexit
import json
import subprocess
import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile
import redis.asyncio as redis
from app_settings import Settings
from celery_config import celery_app
from model import Moderation
from dtos import ModerationResponse

now = str(datetime.now())
settings = Settings()
app = FastAPI()
model = Moderation()
pool = redis.ConnectionPool.from_url(settings.redis_db_url)
redis_client: redis.Redis
celery_worker: subprocess.Popen
flower_worker: subprocess.Popen


def start_celery_worker():
    global celery_worker
    celery_worker = subprocess.Popen(
        ["celery", "-A", "celery_config.celery_app", "worker", "--loglevel=info", "--pool=solo"]
    )


def start_flower_worker():
    global flower_worker
    flower_worker = subprocess.Popen(
        ["celery", "-A", "celery_config.celery_app", "flower", "--persistent=True", "--state_save_interval=5"]
    )


def stop_flower_worker():
    global flower_worker
    flower_worker.terminate()
    celery_worker.wait()


def stop_celery_worker():
    global celery_worker
    celery_worker.terminate()
    celery_worker.wait()


@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = redis.Redis.from_pool(pool)
    print(f"redis client started : {await redis_client.ping()}")
    start_celery_worker()
    start_flower_worker()


@app.on_event("shutdown")
async def shutdown():
    global redis_client
    global pool
    await redis_client.aclose()
    await pool.aclose()
    stop_celery_worker()
    stop_flower_worker()


@app.get("/")
async def root():
    await redis_client.set("my-key", json.dumps({"key": "value"}))
    data = await redis_client.get("my-key")
    return {"message": "Hello World", "data": data}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post(
    "/api/v1/moderation/image", tags=["moderation"], response_model=ModerationResponse
)
async def image_moderation(image: UploadFile):
    global redis_client
    enc_image = await image.read()
    task = celery_app.send_task('tasks.image_moderation_task', args=[enc_image])
    return ModerationResponse(task_id=task.id, created_at=now)


@app.post(
    "/api/v1/moderation/text", tags=["moderation"], response_model=ModerationResponse
)
async def text_moderation(text: str):
    global redis_client
    task_id = str(uuid.uuid4())
    data = new_task_entry()
    await redis_client.set(task_id, data)
    task = celery_app.send_task('tasks.text_moderation_task', args=[text])
    return ModerationResponse(task_id=task.id, created_at=now)


@app.get("/api/v1/moderation/{task}", tags=["moderation"])
async def moderation_status(task: str):
    global redis_client
    data = await redis_client.get(task)
    data_dict = json.loads(data)
    return {**data_dict}


def new_task_entry():
    return json.dumps({"status": "pending", "updated_at": now})


atexit.register(stop_celery_worker)
atexit.register(stop_flower_worker)
