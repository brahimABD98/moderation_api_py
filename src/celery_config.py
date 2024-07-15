from celery import Celery
from src.app_settings import Settings

settings = Settings()
celery_app = Celery(
    "moderation_api.src.celery_config",
    broker=settings.redis_db_url,
    backend=settings.redis_db_url,
)
celery_app.autodiscover_tasks(["src.tasks"])
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],  # Ignore other content
    result_serializer="json",
    timezone="Europe/Paris",
    enable_utc=True,
)
celery_app.control.rate_limit("src.tasks.extract_frames_task", "1/m")
celery_app.control.rate_limit("src.tasks.image_moderation_task", "2/m")
celery_app.conf.update(
    worker_max_tasks_per_child=1,  # Restart worker after each task to free resources
    worker_prefetch_multiplier=1,  # Limit the number of tasks a worker can reserve
)