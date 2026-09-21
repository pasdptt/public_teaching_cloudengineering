"""How work gets from the request handler to the processor.

Today there is one implementation, ``InlineQueue``, which is not really a queue at all: it
runs the work immediately, on the request thread, before the response is sent. That is the
simplest thing that can possibly work, and it is genuinely what the application should do
until there is a reason for anything more.

The reason arrives in Lab 4, when students watch this design saturate under load, and is
answered in Lab 5, when a real queue is put behind the same interface.

Keeping the seam here from week 2 means Lab 5 adds a class; it does not restructure the
application. Students should notice that the interface below says nothing about *when* the
work happens — which is exactly why it can be satisfied both by "now, right here" and by
"later, on another machine, possibly twice".
"""

from __future__ import annotations

from typing import Callable, Protocol


class QueueError(RuntimeError):
    """A queue operation failed."""


class Queue(Protocol):
    """Hand a job id off for processing.

    Note what this contract does **not** promise: not that the work has finished when
    ``submit`` returns, not that it happens once, and not that it happens at all without a
    consumer. Every one of those absences becomes a lesson later.
    """

    def submit(self, job_id: str) -> None: ...


class InlineQueue:
    """Runs the handler immediately, synchronously, on the calling thread.

    Honest about what it is: a queue-shaped hole with the work done in place. It gives the
    caller the strongest possible guarantee — when ``submit`` returns, the work is done —
    and pays for it with a request that takes as long as the work does.
    """

    def __init__(self, handler: Callable[[str], None]) -> None:
        self._handler = handler

    def submit(self, job_id: str) -> None:
        self._handler(job_id)


def build_queue(backend: str, handler: Callable[[str], None]) -> Queue:
    """Factory. Lab 5 adds a Pub/Sub branch here."""
    if backend == "inline":
        return InlineQueue(handler)
    raise QueueError(
        f"Unknown queue backend {backend!r}. This build supports: inline. "
        f"(Lab 5 adds a Pub/Sub backend.)"
    )
