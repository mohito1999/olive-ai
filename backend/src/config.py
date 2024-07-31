import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(verbose=True, dotenv_path=env_path)


# os.getenv but also raises error for required variables
def getenv(name, default=None, required=True):
    try:
        return os.environ[name] if required and default is None else os.environ.get(name, default)
    except KeyError as e:
        print(f"Required environment variable {e} not defined")
        raise


ENVIRONMENT = getenv("ENVIRONMENT")
BASE_URL = getenv("BASE_URL")
VERSION = getenv("VERSION", "")
DEBUG = ENVIRONMENT.casefold() == "development".casefold()

HOST = getenv("APPLICATION_HOST", "0.0.0.0")
PORT = int(getenv("APPLICATION_PORT", "3000"))

STRUCTURED_LOGGING = getenv("STRUCTURED_LOGGING", "false").lower() == "true"
LOG_LEVEL = getenv("LOG_LEVEL", "DEBUG")
DEFAULT_LOG_FIELDS = {"server": "olive-ai", "env": ENVIRONMENT, "version": VERSION}

AWS_REGION = getenv("AWS_DEFAULT_REGION", "ap-south-1")

DB_CONTAINER = getenv("APPLICATION_DB_CONTAINER", "db")
POSTGRES = {
    "user": getenv("POSTGRES_USER", "postgres"),
    "pw": getenv("POSTGRES_PASSWORD", ""),
    "host": getenv("POSTGRES_HOST", DB_CONTAINER),
    "port": int(getenv("POSTGRES_PORT", "5432")),
    "db": getenv("POSTGRES_DB", "postgres"),
    "min_size": getenv("APPLICATION_POSTGRES_MIN_CONNECTIONS", 5),
    "max_size": getenv("APPLICATION_POSTGRES_MAX_CONNECTIONS", 20),
}
BASE_DB_URI = "%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s" % POSTGRES
ASYNC_DB_URI = f"postgresql+asyncpg://{BASE_DB_URI}"
SYNC_DB_URI = f"postgresql://{BASE_DB_URI}"

SUPABASE_URL = getenv("SUPABASE_URL")
SUPABASE_KEY = getenv("SUPABASE_KEY")
SUPABASE_JWT_SECRET = getenv("SUPABASE_JWT_SECRET")

SUPABASE_CUSTOMER_SET_BUCKET_NAME = getenv("SUPABASE_CUSTOMER_SET_BUCKET_NAME")

SQS_QUEUE_URL = getenv("SQS_QUEUE_URL")
SQS_QUEUE_NAME = getenv("SQS_QUEUE_NAME")

CHANNELS_AVAILABLE_COUNT = int(getenv("CHANNELS_AVAILABLE_COUNT", "1"))
CALL_RETRY_INTERVAL = int(getenv("CALL_RETRY_INTERVAL", "30"))
CALL_TIMEOUT_DURATION = int(getenv("CALL_TIMEOUT_DURATION", "30"))
CALL_TIMEOUT_TASK_INTERVAL = int(getenv("CALL_TIMEOUT_TASK_INTERVAL", "15"))

EXOTEL_ACCOUNT_SID = getenv("EXOTEL_ACCOUNT_SID")
EXOTEL_API_KEY = getenv("EXOTEL_API_KEY")
EXOTEL_API_TOKEN = getenv("EXOTEL_API_TOKEN")
EXOTEL_APP_ID = getenv("EXOTEL_APP_ID")
EXOTEL_SUBDOMAIN = getenv("EXOTEL_SUBDOMAIN")
EXOTEL_OUTBOUND_CALLER_NUMBER = getenv("EXOTEL_OUTBOUND_CALLER_NUMBER")

TWILIO_ACCOUNT_SID = getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = getenv("TWILIO_AUTH_TOKEN")
TWILIO_OUTBOUND_CALLER_NUMBER = getenv("TWILIO_OUTBOUND_CALLER_NUMBER")

SENTRY_DSN = getenv("SENTRY_DSN")

