from celeryworker import celery_app


def run_celery_worker():
    celery_app.worker_main(argv=["worker", "--loglevel=INFO", "--concurrency=2", "--events"])


if __name__ == "__main__":
    run_celery_worker()
