from transformers import pipeline
from PIL import Image

from detoxify import Detoxify


class AIPipeLine:
    def __init__(self, model: str, model_revision, task: str):
        self.evaluate = pipeline(task=task, model=model, revision=model_revision)


class Moderation:
    def __init__(self, image_pipline: AIPipeLine = None, text_pipeline=None):
        self.ImagePipeline = image_pipline or AIPipeLine(model="Falconsai/nsfw_image_detection", model_revision=None,
                                                         task="image-classification")
        self.TextPipeline = text_pipeline or Detoxify("unbiased")

    def evaluate_image(self, image: Image):
        return self.ImagePipeline.evaluate(image)

    def evaluate_text(self, text: str):
        return self.TextPipeline.predict(text)
