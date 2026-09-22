"""How work gets from the request handler to the processor.

Today there is one implementation, ``InlineQueue``, which is not really a queue at all: it
runs the work immediately, on the request thread, before the response is sent. That is the
simplest thing that can possibly work, and it is genuinely what the application should do
until there is a reason for anything more.

The reason arrives in Lab 4, when students watch this design saturate under load, and is
answered in Lab 5, when a real queue is put behind the same interface. Three implementations
now satisfy it -- work done here and now, work done later in this process, and work done
later somewhere else entirely -- and the application cannot tell them apart.

Keeping the seam here from week 2 means Lab 5 adds a class; it does not restructure the
application. Students should notice that the interface below says nothing about *when* the
work happens — which is exactly why it can be satisfied both by "now, right here" and by
"later, on another machine, possibly twice".
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Protocol

if TYPE_CHECKING:  # import only for type checkers: no runtime cycle with config.py
    from .config import Config


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


def build_queue(config: "Config", handler: Callable[[str], None]) -> Queue:
    """Factory. Takes the whole config, because the queue backends need different parts.

    ``InlineQueue`` needs nothing, ``ThreadQueue`` needs its duplication and retry
    settings, and ``PubSubQueue`` needs a project and a topic. Passing the config rather
    than a growing list of arguments keeps the call site in ``wiring.py`` unchanged as
    backends are added -- which is the same reason the seam exists at all.
    """
    backend = config.queue_backend
    if backend == "inline":
        return InlineQueue(handler)
    if backend == "thread":
        from .threadqueue import ThreadQueue

        return ThreadQueue(
            handler,
            workers=config.queue_workers,
            duplicate_percent=config.queue_duplicate_percent,
            max_attempts=config.queue_max_attempts,
        )
    if backend == "pubsub":
        from .pubsub_queue import PubSubQueue

        return PubSubQueue(config.project_id, config.queue_topic)
    raise QueueError(
        f"Unknown queue backend {backend!r}. This build supports: "
        f"inline, thread, pubsub."
    )
