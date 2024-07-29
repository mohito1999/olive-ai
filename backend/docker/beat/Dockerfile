############################
# STEP 1 install dependencies
############################
FROM python:3.10-slim as dependencies

WORKDIR /app
RUN apt-get update && apt-get install -y build-essential libssl-dev libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1 
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 
ENV PYTHONPATH=/app

# install dependencies
RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock /app/

RUN python3 -m venv venv
RUN venv/bin/pip install -U pip setuptools
RUN . /app/venv/bin/activate && poetry install

############################
# STEP 2 build a small image
############################
FROM python:3.10-slim as deployment

WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg libportaudio2 && rm -rf /var/lib/apt/lists/*
RUN pip install nltk && python -c "import nltk; nltk.download('punkt')"

COPY --from=dependencies /app/venv ./venv

# copy project
COPY . /app/

CMD ["/app/scripts/run.sh", "beat"]

