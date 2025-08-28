from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ai_creat",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL if hasattr(settings, "REDIS_URL") else None,
)

celery_app.conf.task_routes = {
    "workers.tasks_generation.*": {"queue": settings.CELERY_QUEUE_PRIMARY},
    "workers.tasks_moderation.*": {"queue": settings.CELERY_QUEUE_PRIMARY},
}

celery_app.conf.task_queues = {
    settings.CELERY_QUEUE_PRIMARY: {"exchange": "ai_creat", "routing_key": "primary"},
    settings.CELERY_QUEUE_PRIORITY: {"exchange": "ai_creat", "routing_key": "priority"},
    settings.CELERY_QUEUE_DLQ: {"exchange": "ai_creat", "routing_key": "dlq"},
}
