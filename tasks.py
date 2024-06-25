import json
from datetime import datetime
from PIL import Image
import redis.asyncio as redis
from model import Moderation, generate_text_summary, generate_image_summary

model = Moderation()
now = str(datetime.now())


def new_text_response(answer, summary):
    answer = {key: float(value) for key, value in answer.items()}
    return json.dumps(
        {"status": "completed", "data": {key: round(value, 4) for key, value in answer.items()}, "summary": summary,
         "updated_at": now})


def new_image_response(answer, summary):
    for item in answer:
        item['score'] = round(item['score'], 4)
    return json.dumps(
        {"status": "completed", "data": answer, "summary": summary, "updated_at": now})


async def image_moderation_task(image: Image, redis_client: redis.Redis, task_id: str):
    task = await redis_client.get(task_id)
    if task is None:
        return
    answer = model.evaluate_image(image)
    summary = generate_image_summary(answer)
    data = new_image_response(answer=answer, summary=summary)
    await redis_client.set(task_id, data)
    return


async def text_moderation_task(text: str, redis_client: redis.Redis, task_id: str):
    task = await redis_client.get(task_id)
    if task is None:
        return
    answer = model.evaluate_text(text)
    summary = generate_text_summary(answer)
    data = new_text_response(answer, summary)
    print(f"data inside task {data}")
    await redis_client.set(task_id, data)
    return
