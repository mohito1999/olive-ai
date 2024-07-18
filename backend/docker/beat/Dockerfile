############################
# STEP 1 install dependencies
############################
FROM python:3.10-slim as dependencies

WORKDIR /app
RUN apt-get update && apt-get install -y build-essential libssl-dev libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app/src

# install dependencies
RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock /app/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

RUN python3 -m venv venv
RUN venv/bin/pip install -U pip setuptools
RUN . /app/venv/bin/activate && pip install --no-cache-dir -r requirements.txt

############################
# STEP 2 build a small image
############################
FROM python:3.10-slim as deployment

WORKDIR /app
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=dependencies /app/venv ./venv

# copy project
COPY . /app/

RUN groupadd -r appgroup && useradd -r -g appgroup appuser
RUN mkdir -p /var/log/olive/osquery && \
    chown -R appuser /var/log/olive && \
    chown -R appuser /var/log/olive/osquery && \
    mkdir -p /home/appuser && \
    chown -R appuser /home/appuser && \
    rm -rf /var/log/osquery && \
    ln -sf /var/log/olive/osquery /var/log/osquery

VOLUME /var/log/olive

USER appuser
EXPOSE 3000

ARG COMMIT_SHA
LABEL COMMIT_SHA=$COMMIT_SHA
ENV ENV_COMMIT_SHA=$COMMIT_SHA

CMD ["/app/scripts/run.sh", "beat"]
