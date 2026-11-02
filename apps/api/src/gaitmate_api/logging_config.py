import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("gaitmate.api")


def configure_logging() -> None:
    if logger.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def log_event(level: int, event: str, **fields: Any) -> None:
    logger.log(
        level,
        json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "level": logging.getLevelName(level),
                "event": event,
                **fields,
            },
            separators=(",", ":"),
        ),
    )
