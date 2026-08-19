from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=settings.REDIS_URL or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Zombie Task Locking Mitigations
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # OOM Mitigation limits
    worker_concurrency=2,
    worker_max_tasks_per_child=50
)
