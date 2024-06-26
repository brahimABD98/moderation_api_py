from datetime import datetime
from io import BytesIO

from PIL import Image

from celery_config import celery_app
from model import Moderation, generate_text_summary, generate_image_summary

model = Moderation()
now = str(datetime.now())


def new_text_response(answer, summary):
    answer = {key: float(value) for key, value in answer.items()}
    return {
        "status": "completed",
        "data": {key: round(value, 4) for key, value in answer.items()},
        "summary": summary,
        "updated_at": now,
    }


def new_image_response(answer, summary):
    for item in answer:
        item["score"] = round(item["score"], 4)
    return {"status": "completed", "data": answer, "summary": summary, "updated_at": now}
    

@celery_app.task
def image_moderation_task(image_buffer: bytes):
    image = Image.open(BytesIO(image_buffer))
    answer = model.evaluate_image(image)
    summary = generate_image_summary(answer)
    data = new_image_response(answer=answer, summary=summary)
    return data


@celery_app.task
def text_moderation_task(text: str):
    answer = model.evaluate_text(text)
    summary = generate_text_summary(answer)
    data = new_text_response(summary=summary, answer=answer)
    return data
