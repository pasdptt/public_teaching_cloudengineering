"""The two things this application knows about: documents and jobs.

Kept deliberately small. A job record is the unit of state that has to survive when
execution does not — which is the whole point of Lab 1's failure exercise and of moving
this data to Firestore in Lab 3.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

# Job lifecycle. A job is created PENDING, moves to RUNNING while a worker holds it, and
# ends in one of the two terminal states.
PENDING = "pending"
RUNNING = "running"
SUCCEEDED = "succeeded"
FAILED = "failed"

TERMINAL_STATES = frozenset({SUCCEEDED, FAILED})
ALL_STATES = frozenset({PENDING, RUNNING, SUCCEEDED, FAILED})

# Operations the processor knows how to perform. Deliberately trivial domain logic:
# the course is about the cloud, not about text analysis.
OPERATIONS = ("wordcount", "checksum", "extract")


def new_id(prefix: str) -> str:
    """A readable, sortable-enough identifier.

    A UUID would do, but prefixed ids make log output legible when a student is tracing a
    request by eye — which they do in every single lab.
    """
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def now_ms() -> int:
    """Milliseconds since the epoch, as an int.

    Wall-clock time, not monotonic: these timestamps are stored and compared across
    processes and machines, where a monotonic clock is meaningless.
    """
    return int(time.time() * 1000)


@dataclass
class Document:
    """An uploaded document. The bytes live in storage; this is the metadata."""

    id: str
    name: str
    size_bytes: int
    content_type: str
    created_ms: int

    @classmethod
    def create(cls, name: str, size_bytes: int, content_type: str = "text/plain") -> "Document":
        return cls(
            id=new_id("doc"),
            name=name,
            size_bytes=size_bytes,
            content_type=content_type,
            created_ms=now_ms(),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Document":
        return cls(**data)


@dataclass
class Job:
    """A unit of work against a document.

    ``attempts`` and ``idempotency_key`` are not decoration. Once Lab 5 introduces a queue
    with at-least-once delivery, the same job can be handed to a worker more than once, and
    these two fields are what make that safe to reason about.
    """

    id: str
    document_id: str
    operation: str
    status: str
    created_ms: int
    updated_ms: int
    attempts: int = 0
    idempotency_key: Optional[str] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    worker_instance: Optional[str] = None
    # Set when a job first reaches a terminal state, so a duplicate delivery can be
    # detected and skipped rather than reprocessed.
    completed_ms: Optional[int] = None

    @classmethod
    def create(cls, document_id: str, operation: str,
               idempotency_key: Optional[str] = None) -> "Job":
        ts = now_ms()
        return cls(
            id=new_id("job"),
            document_id=document_id,
            operation=operation,
            status=PENDING,
            created_ms=ts,
            updated_ms=ts,
            idempotency_key=idempotency_key,
        )

    @property
    def is_terminal(self) -> bool:
        return self.status in TERMINAL_STATES

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Job":
        # Tolerate records written by an older version of the application: a field that
        # does not exist any more is dropped rather than raising. Students hit this for
        # real in Lab 3, when records written before a change are read back after it.
        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class Counters:
    """In-process counters, exposed at /stats.

    Not a metrics system. Enough to make Lab 4's load experiment measurable without
    installing anything, and enough to show in Lab 11 why in-process counters stop being
    useful the moment there is more than one instance.
    """

    documents_created: int = 0
    jobs_created: int = 0
    jobs_deduplicated: int = 0
    jobs_processed: int = 0
    jobs_failed: int = 0
    duplicate_deliveries_skipped: int = 0
    request_count: int = 0
    started_ms: int = field(default_factory=now_ms)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["uptime_ms"] = now_ms() - self.started_ms
        return data
