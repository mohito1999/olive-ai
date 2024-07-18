python3 -m venv venv
venv/bin/pip install -U pip setuptools
venv/bin/pip install poetry
source ./venv/bin/activate
poetry install

docker volume create --name=olive_db

