#!/usr/bin/env bash

cd /app
source venv/bin/activate

case $1 in
    worker ) python src/run_celery_worker.py; exit; ;;
    beat ) python src/run_celery_beat.py; exit; ;;
    * ) python src/run_gunicorn.py; exit 1; ;;
esac
