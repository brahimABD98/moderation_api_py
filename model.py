from typing import List, Dict

from transformers import pipeline
from PIL import Image

from detoxify import Detoxify


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
