import json
from datetime import datetime

from PIL import Image
import redis.asyncio as redis
from model import Moderation

model = Moderation()


def new_response(answer):
    now = str(datetime.now())
    return json.dumps({"status": "completed", "answer": str(answer), "updated_at": now})


async def image_moderation_task(image: Image, redis_client: redis.Redis, task_id: str):
    task = await redis_client.get(task_id)
    if task is None:
        return
    answer = model.evaluate_image(image)
    data = new_response(answer)
    await redis_client.set(task_id, data)
    return


async def text_moderation_task(text: str, redis_client: redis.Redis, task_id: str):
    task = await redis_client.get(task_id)
    if task is None:
        return
    answer = model.evaluate_text(text)
    data = new_response(answer)
    await redis_client.set(task_id, data)
    return
