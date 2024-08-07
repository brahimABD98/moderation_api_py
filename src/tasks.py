import os
import tempfile
from datetime import datetime
from io import BytesIO

import cv2
from PIL import Image
from celery import chord

from src.celery_config import celery_app
from src.model import Moderation, generate_text_summary, generate_image_summary

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
    return {
        "status": "completed",
        "data": answer,
        "summary": summary,
        "updated_at": now,
    }


@celery_app.task
def text_moderation_task(text: str):
    answer = model.evaluate_text(text)
    summary = generate_text_summary(answer)
    data = new_text_response(summary=summary, answer=answer)
    return data


@celery_app.task
def video_moderation_task(file: bytes):
    return model.evaluate_video(file=file)


@celery_app.task
def image_moderation_task(image_buffer: bytes):
    image = Image.open(BytesIO(image_buffer))
    answer = model.evaluate_image(image)
    summary = generate_image_summary(answer)
    data = new_image_response(answer=answer, summary=summary)
    return data


@celery_app.task
def vid_moderation_task(video_buffer: bytes, frame_skip: int = 30):
    # Create a temporary file to save the video buffer
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_file.write(video_buffer)
        temp_video_path = temp_video_file.name

    try:
        # Load the video from the temporary file
        video = cv2.VideoCapture(temp_video_path)
        frames = []
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        for frame_idx in range(frame_count):
            ret, frame = video.read()
            if not ret:
                break

            # Skip frames according to the frame_skip parameter
            if frame_idx % frame_skip == 0:
                # Convert the frame to bytes
                is_success, buffer = cv2.imencode(".jpg", frame)
                if is_success:
                    frames.append(buffer.tobytes())

        video.release()

        task_group = [image_moderation_task.s(frame) for frame in frames]
        callback = aggregate_summaries.s()
        result = chord(task_group)(callback)
        return result.id
    finally:
        # Clean up the temporary file
        os.remove(temp_video_path)


@celery_app.task
def aggregate_summaries(results_data):
    nsfw_threshold = 0.5  # Define your NSFW score threshold here
    for result in results_data:
        for item in result["data"]:
            if item["label"] == "nsfw" and item["score"] >= nsfw_threshold:
                return "video nsfw"

    return "The video does not contain NSFW content"
