import subprocess

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


def start_celery_worker():
    return subprocess.Popen(
        [
            "celery",
            "-A",
            "src.celery_config.celery_app",
            "worker",
            "--loglevel=info",
            "--pool=solo",
            "--concurrency=1",
        ]
    )


def start_flower_worker():
    return subprocess.Popen(
        [
            "celery",
            "-A",
            "src.celery_config.celery_app",
            "flower",
            "--persistent=True",
            "--state_save_interval=5",
        ]
    )


def stop_flower_worker(flower_worker):
    flower_worker.terminate()


def stop_celery_worker(celery_worker):
    celery_worker.terminate()
