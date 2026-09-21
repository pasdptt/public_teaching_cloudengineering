"""Structured logging, from day one.

Logs are printed as one JSON object per line to stdout. Two reasons, and both are course
content rather than style preference:

  * **stdout, not a file.** A container has nowhere useful to write a log file, and
    anything it does write disappears with the container. Every managed platform collects
    stdout. Writing to a file now would mean rewriting this in Lab 4.
  * **JSON, not prose.** In week 11 students query logs by field. A log line that reads
    nicely to a human and cannot be filtered by job id is a log line that is useless at
    exactly the moment it is needed.

``request_id`` threads through every line produced while handling one request, which is
what makes "trace this request" in Lab 1 a matter of grepping rather than guessing.
"""

from __future__ import annotations

import json
import sys
import threading
import time
from typing import Any

_LEVELS = {"debug": 10, "info": 20, "warning": 30, "error": 40}
_state = threading.local()
_lock = threading.Lock()
_min_level = 20


def configure(level: str = "info") -> None:
    global _min_level
    _min_level = _LEVELS.get(level.lower(), 20)


def set_request_id(request_id: str | None) -> None:
    """Attach a request id to every log line emitted by this thread until cleared."""
    _state.request_id = request_id


def get_request_id() -> str | None:
    return getattr(_state, "request_id", None)


def log(level: str, message: str, **fields: Any) -> None:
    if _LEVELS.get(level, 20) < _min_level:
        return
    entry: dict[str, Any] = {
        # RFC 3339 in UTC. Sortable as text, unambiguous across timezones -- which matters
        # when the laptop is in Bangkok and the service is in Iowa.
        "time": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + f".{int(time.time() * 1000) % 1000:03d}Z",
        # "severity" is the field name Cloud Logging reads to colour and filter by level.
        # Using it now costs nothing and means Lab 4's logs are legible immediately.
        "severity": level.upper(),
        "message": message,
    }
    rid = get_request_id()
    if rid:
        entry["request_id"] = rid
    entry.update(fields)
    line = json.dumps(entry, default=str)
    # One lock around the write: without it, concurrent threads interleave partial lines
    # and the output stops being parseable exactly when load makes it interesting.
    with _lock:
        sys.stdout.write(line + "\n")
        sys.stdout.flush()


def debug(message: str, **fields: Any) -> None: log("debug", message, **fields)
def info(message: str, **fields: Any) -> None: log("info", message, **fields)
def warning(message: str, **fields: Any) -> None: log("warning", message, **fields)
def error(message: str, **fields: Any) -> None: log("error", message, **fields)
