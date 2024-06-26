from celery import Celery
from app_settings import Settings

settings = Settings()
celery_app = Celery(
    __name__, broker=settings.redis_db_url, backend=settings.redis_db_url
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],  # Ignore other content
    result_serializer="json",
    timezone="Europe/Paris",
    enable_utc=True,
)
