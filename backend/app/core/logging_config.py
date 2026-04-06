import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from .config import settings


class JsonFormatter(logging.Formatter):
    """Simple JSON formatter for structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = getattr(record, "request_id", None)
        path = getattr(record, "path", None)
        method = getattr(record, "method", None)
        status_code = getattr(record, "status_code", None)
        duration_ms = getattr(record, "duration_ms", None)
        event = getattr(record, "event", None)
        actor_id = getattr(record, "actor_id", None)
        actor_username = getattr(record, "actor_username", None)
        actor_role = getattr(record, "actor_role", None)
        target = getattr(record, "target", None)
        outcome = getattr(record, "outcome", None)
        reason = getattr(record, "reason", None)

        if request_id:
            payload["request_id"] = request_id
        if method:
            payload["method"] = method
        if path:
            payload["path"] = path
        if status_code is not None:
            payload["status_code"] = status_code
        if duration_ms is not None:
            payload["duration_ms"] = duration_ms
        if event:
            payload["event"] = event
        if actor_id is not None:
            payload["actor_id"] = actor_id
        if actor_username:
            payload["actor_username"] = actor_username
        if actor_role:
            payload["actor_role"] = actor_role
        if target:
            payload["target"] = target
        if outcome:
            payload["outcome"] = outcome
        if reason:
            payload["reason"] = reason

        return json.dumps(payload, ensure_ascii=True)


def configure_logging() -> None:
    root = logging.getLogger()
    root.handlers.clear()

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    root.setLevel(level)

    handler = logging.StreamHandler()
    if settings.log_format.lower() == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(settings.log_format))

    root.addHandler(handler)
