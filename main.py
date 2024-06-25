import json
import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import FastAPI, UploadFile, BackgroundTasks
from PIL import Image
import redis.asyncio as redis
from tasks import image_moderation_task, text_moderation_task
from model import Moderation
from dtos import ModerationResponse

load_dotenv()


class Settings(BaseSettings):
    redis_db_url: str = os.environ.get("DATABASE_URL")


now = str(datetime.now())

settings = Settings()
app = FastAPI()
model = Moderation()
pool = redis.ConnectionPool.from_url(settings.redis_db_url)
redis_client: redis.Redis


@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = redis.Redis.from_pool(pool)
    print(f"redis client started : {await redis_client.ping()}")


@app.on_event("shutdown")
async def shutdown():
    global redis_client
    global pool
    if redis_client:
        await redis_client.aclose()
    await pool.aclose()


@app.get("/")
async def root():
    await redis_client.set('my-key', json.dumps({'key': 'value'}))
    data = await redis_client.get('my-key')
    return {"message": "Hello World", "data": data}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/api/v1/moderation/image", tags=["moderation"], response_model=ModerationResponse)
async def image_moderation(image: UploadFile, background_task: BackgroundTasks):
    global redis_client
    enc_image = Image.open(image.file)
    task_id = str(uuid.uuid4())
    data = new_task_entry()
    await redis_client.set(task_id, data)
    background_task.add_task(image_moderation_task, enc_image, redis_client, task_id)
    return ModerationResponse(task_id=task_id, created_at=now)


@app.post("/api/v1/moderation/text", tags=["moderation"], response_model=ModerationResponse)
async def text_moderation(text: str, background_task: BackgroundTasks):
    global redis_client
    task_id = str(uuid.uuid4())
    data = new_task_entry()
    await redis_client.set(task_id, data)
    background_task.add_task(text_moderation_task, text, redis_client, task_id)
    return ModerationResponse(task_id=task_id, created_at=now)


@app.get("/api/v1/moderation/{task}", tags=["moderation"])
async def moderation_status(task: str):
    global redis_client
    data = await redis_client.get(task)
    return {"data": data}


def new_task_entry():
    return json.dumps({"status": "pending", "updated_at": now})
