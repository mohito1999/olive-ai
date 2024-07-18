from celeryworker import celery_app


def run_celery_beat():
    celery_app.Beat(loglevel="info", schedule="/tmp/celerybeat-schedule").run()


if __name__ == "__main__":
    run_celery_beat()
