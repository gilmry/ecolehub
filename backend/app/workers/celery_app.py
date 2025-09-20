"""
EcoleHub Stage 3 - Celery Configuration
Background tasks for shop orders and notifications
"""

import os

from celery import Celery

# Redis URL for Celery broker
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "ecolehub_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.workers.shop_tasks", "app.workers.notification_tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Brussels",  # Belgian timezone
    enable_utc=True,
    task_routes={
        "app.workers.shop_tasks.*": {"queue": "shop"},
        "app.workers.notification_tasks.*": {"queue": "notifications"},
    },
)

# Configure task execution
celery_app.conf.update(
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
)

if __name__ == "__main__":
    celery_app.start()
