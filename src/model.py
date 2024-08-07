import base64
import tempfile
from typing import List, Dict

import cv2
from PIL import Image
from detoxify import Detoxify
from transformers import pipeline


class AIPipeLine:
    def __init__(self, model: str, model_revision, task: str):
        self.evaluate = pipeline(task=task, model=model, revision=model_revision)


def generate_text_summary(moderation_results: dict[str, float]) -> str:
    thresholds = {
        "toxicity": 0.5,
        "severe_toxicity": 0.5,
        "obscene": 0.5,
        "identity_attack": 0.5,
        "insult": 0.5,
        "threat": 0.5,
        "sexual_explicit": 0.5,
    }
    harmful_content = [
        label
        for label, score in moderation_results.items()
        if score >= thresholds[label]
    ]
    if harmful_content:
        summary = "The text contains harmful content: " + ", ".join(harmful_content)
    else:
        summary = (
            "The text content is safe and does not contain toxic or harmful elements."
        )

    return summary


def generate_image_summary(moderation_result: List[Dict[str, float]]) -> str:
    thresholds = {"nsfw": 0.5, "normal": 0.5}
    harmful_content = []

    for result in moderation_result:
        label = result.get("label", "")
        score = result.get("score", 0.0)

        # Determine if the score exceeds the threshold for each label
        if label in thresholds and score > thresholds[label]:
            harmful_content.append(label)

    summary = (
        f"The image contains harmful content: {', '.join(harmful_content)}"
        if harmful_content
        else "The image " "is safe."
    )
    return summary


class Moderation:
    def __init__(self, image_pipline: AIPipeLine = None, text_pipeline=None):
        self.ImagePipeline = image_pipline or AIPipeLine(
            model="Falconsai/nsfw_image_detection",
            model_revision=None,
            task="image-classification",
        )
        self.TextPipeline = text_pipeline or Detoxify("unbiased")

    def evaluate_image(self, image: Image):
        return self.ImagePipeline.evaluate(image)

    def evaluate_text(self, text: str):
        return self.TextPipeline.predict(text)

    def evaluate_video(
        self,
        file: bytes,
        skip_frames_percentage=30,
        fast_mode=False,
        labels: List[str] = ["nsfw"],
        return_on_first_matching_label=False,
        score=0.7,
    ):
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temporary_file:
                temporary_file.write(file)

            results = []
            # Read the video file using OpenCV
            video_capture = cv2.VideoCapture(temporary_file.name)

            total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

            skip_percentage = int(total_frames * (skip_frames_percentage / 100))

            # Extract frames from the video
            while True:
                success, frame = video_capture.read()
                if not success:
                    break
                index = int(video_capture.get(cv2.CAP_PROP_POS_FRAMES))

                if fast_mode and index % skip_percentage != 0:
                    continue

                _, img = cv2.imencode(".jpg", frame)

                base64_image = base64.b64encode(img).decode("utf-8")
                moderation_result = self.ImagePipeline.evaluate(base64_image)
                evaluated_labels = set()
                label_scores = {
                    moderation["label"]: moderation["score"]
                    for moderation in moderation_result
                }
                print(label_scores)
                for label in labels[:]:
                    if label in label_scores and label_scores[label] >= score:
                        results.append(
                            {
                                "frame": index,
                                "label": label,
                                "score": label_scores[label],
                            }
                        )
                        evaluated_labels.add(label)
                        labels.remove(label)

                if return_on_first_matching_label or set(labels) == evaluated_labels:
                    break

            # Return the results
            return results
        except Exception as e:
            print(f"Error while processing video:{e}")
        finally:
            video_capture.release()
            del temporary_file
            del moderation_result
