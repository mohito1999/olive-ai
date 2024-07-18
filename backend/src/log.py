import logging

from asgi_correlation_id import CorrelationIdFilter
from asgi_correlation_id.context import correlation_id
from ecs_logging import StdlibFormatter
from loguru import logger
from vocode.logging import configure_json_logging, configure_pretty_logging

import config


def configure_logging() -> None:  # pragma: no cover
    configure_pretty_logging()

configure_logging()

###################
# Context filters
###################
class TraceIDLogFilter(CorrelationIdFilter):
    """
    Log filter to inject the current request id of the request under `log_record.trace_id`
    """

    def filter(self, log_record):
        cid = correlation_id.get()
        if self.uuid_length is not None and cid:
            log_record.trace_id = cid[: self.uuid_length]  # type: ignore[attr-defined]
        else:
            log_record.trace_id = cid  # type: ignore[attr-defined]
        return log_record


def clear_uvicorn_logger_handlers():
    logging.getLogger("watchfiles.main").setLevel(logging.INFO)
    logging.getLogger("uvicorn").handlers.clear()


def setup(logger: logging.Logger):
    # if logger.hasHandlers():
    #     logger.handlers.clear()
    # clear_uvicorn_logger_handlers()

    if config.STRUCTURED_LOGGING:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            StdlibFormatter(
                exclude_fields=[
                    "log.original",
                    "log.origin",
                    "log.logger",
                    "process",
                    "ecs",
                ],
                extra=config.DEFAULT_LOG_FIELDS,
            )
        )
        logger.addHandler(stream_handler)

    logger.addFilter(TraceIDLogFilter())
    logger.setLevel(config.LOG_LEVEL)

    return logger


log = logger
