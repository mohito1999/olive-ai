from celery import Celery
from celery.signals import setup_logging
from kombu import Queue

from config import DEBUG, SQS_QUEUE_NAME, SQS_QUEUE_URL

celery_config = {
    "broker_url": f"sqs://@{SQS_QUEUE_URL.split('://')[1]}",
    "broker_transport_options": {"visibility_timeout": 36000, "region": "ap-south-1"},
    "broker_connection_retry_on_startup": True,
    "task_default_queue": SQS_QUEUE_NAME,
    "task_queues": [
        Queue(SQS_QUEUE_NAME, broker=SQS_QUEUE_URL),
    ],
}

if not DEBUG:
    celery_config["broker_transport_options"]["predefined_queues"] = {
        SQS_QUEUE_NAME: {
            "url": SQS_QUEUE_URL,
        }
    }
    celery_config["broker_transport_options"]["is_secure"] = True

celery_app = Celery(__name__, include=["jobs.tasks", "jobs.call"])
celery_app.config_from_object(celery_config)

@setup_logging.connect
def void(*args, **kwargs):
    """Override celery's logging setup to prevent it from altering our settings.
    github.com/celery/celery/issues/1867

    :return void:
    """
    pass
