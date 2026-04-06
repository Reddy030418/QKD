import logging
from typing import Optional

from ..models import User

audit_logger = logging.getLogger("audit")


def log_audit_event(
    event: str,
    actor: Optional[User] = None,
    outcome: str = "success",
    target: Optional[str] = None,
    reason: Optional[str] = None,
) -> None:
    audit_logger.info(
        "audit_event",
        extra={
            "event": event,
            "actor_id": actor.id if actor else None,
            "actor_username": actor.username if actor else None,
            "actor_role": actor.role if actor else None,
            "target": target,
            "outcome": outcome,
            "reason": reason,
        },
    )
