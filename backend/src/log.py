from asgi_correlation_id import CorrelationIdFilter
from asgi_correlation_id.context import correlation_id
from loguru import logger
from vocode.logging import configure_json_logging, configure_pretty_logging


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


log = logger
