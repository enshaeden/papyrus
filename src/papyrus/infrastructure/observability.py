from __future__ import annotations

import json
import logging
from typing import Any


LOGGER_NAME = "papyrus"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage(),
        }
        event = getattr(record, "event", None)
        if event:
            payload["event"] = event
        context = getattr(record, "context", None)
        if isinstance(context, dict):
            payload.update(context)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, sort_keys=True)


def get_logger(name: str = LOGGER_NAME) -> logging.Logger:
    root_logger = logging.getLogger(LOGGER_NAME)
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
        root_logger.propagate = False
    return logging.getLogger(name)


def log_event(logger: logging.Logger, level: int, event: str, **context: Any) -> None:
    logger.log(level, event.replace("_", " "), extra={"event": event, "context": context})
