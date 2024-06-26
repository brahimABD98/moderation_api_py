from celery import Celery
from app_settings import Settings

settings = Settings()
celery_app = Celery(
    "moderation_api.celery_config", broker=settings.redis_db_url, backend=settings.redis_db_url
)
celery_app.autodiscover_tasks(['tasks'])
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],  # Ignore other content
    result_serializer="json",
    timezone="Europe/Paris",
    enable_utc=True,
)
