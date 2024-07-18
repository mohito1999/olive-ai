from celeryworker import celery_app


def run_celery_worker():
    celery_app.worker_main(argv=["worker", "--loglevel=INFO", "--concurrency=1", "--events"])


if __name__ == "__main__":
    run_celery_worker()
