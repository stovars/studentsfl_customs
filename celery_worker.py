from celery import Celery

celery = Celery("tasks", broker="redis://localhost:6379",backend="redis://localhost:6379")

celery.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone="UTC",
    enable_utc=True
)

