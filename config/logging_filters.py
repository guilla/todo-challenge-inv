# config/logging_filters.py
import logging
from typing import Any

class RequestIdFilter(logging.Filter):

    def filter(self, record: logging.LogRecord) -> bool:
        rid = getattr(record, "request_id", None)
        if rid is None:
            setattr(record, "request_id", "-")
        return True