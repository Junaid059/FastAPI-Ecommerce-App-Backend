from celery import Celery
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

celery_app = Celery(
    "ecomm_tasks",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),  # Default fallback
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["app.tasks"]  # Where tasks are defined
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)