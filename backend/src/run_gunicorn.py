import multiprocessing

import gunicorn.app.base
from fastapi import FastAPI
from uvicorn.workers import UvicornWorker

from config import HOST, PORT
from log import log
from server import app


# Gunicorn custom app: https://docs.gunicorn.org/en/stable/custom.html
class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict(
            [
                (key, value)
                for key, value in self.options.items()
                if key in self.cfg.settings and value is not None
            ]
        )
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def number_of_workers():
    # return (multiprocessing.cpu_count() * 2) + 1
    return 1


# Extended Uvicorn worker to disbale server and date deahers
class HeadlessUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "loop": "auto",
        "http": "auto",
        "date_header": False,
        "server_header": False,
    }


# Gunicorn conf inspired from https://github.com/tiangolo/uvicorn-gunicorn-docker
def run_gunicorn_workers(app: FastAPI):
    log.info("Starting Gunicorn workers...")
    options = {
        "bind": "%s:%s" % (HOST, int(PORT)),
        "worker_class": "run_gunicorn.HeadlessUvicornWorker",
        "workers": number_of_workers(),
        "timeout": 120,
        "graceful_timeout": 120,
        "keepalive": 5,
    }
    StandaloneApplication(app, options).run()


if __name__ == "__main__":
    run_gunicorn_workers(app)
