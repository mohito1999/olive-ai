import uvicorn

from config import HOST, PORT


def run_uvicorn_worker(reload: bool = True):
    uvicorn.run(
        "server:app",
        host=HOST,
        port=PORT,
        server_header=False,
        date_header=False,
        reload=reload,
    )


if __name__ == "__main__":
    run_uvicorn_worker()
