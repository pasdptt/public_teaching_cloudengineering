"""A real queue that runs on your laptop.

``InlineQueue`` does the work before the response is sent. This one does not: ``submit``
puts a job id on a list and returns immediately, and a background worker picks it up some
time later. That one change is the whole subject of week 10, and it brings every problem in
week 11 with it.

**This class is supplied, not an exercise.** It exists for three reasons:

  * It is the fallback path. A student who cannot get a cloud account does Lab 5's
    exercises here, and the honest gap is named in the lab: this broker is in one process,
    so it survives nothing. Kill the process and the queue is gone. A real broker's whole
    value is that it is not your process.
  * It is faster to iterate against than a cloud service, and it costs nothing.
  * It makes at-least-once delivery *reproducible*. A real queue delivers a message twice
    when it feels like it, which is a terrible way to learn what that means. Here you turn
    it on:

        DOCAPP_QUEUE=thread DOCAPP_QUEUE_DUPLICATE_PERCENT=100 python3 -m docapp

    and then every message arrives twice, on purpose, every time.

The behaviour below is deliberately naive in one respect, and Lab 5 asks you to find it:
**every failure is retried the same way**. A document that does not exist will never exist,
and retrying three times with backoff wastes time on an answer that cannot change. Real
brokers make you decide which errors are worth retrying, and so should you.
"""

from __future__ import annotations

import random
import threading
import time
from queue import Empty, Queue as _Fifo
from typing import Callable, Optional

from . import logs


class ThreadQueue:
    """At-least-once delivery, in one process, with the duplicates under your control.

    Not durable and not distributed, and it does not pretend to be either. What it does
    reproduce exactly is the property that matters for the exercise: the consumer may see
    the same job more than once, and must be safe when it does.
    """

    # A sentinel, so stop() can wake a worker that is blocked waiting for work rather than
    # leaving it to time out. Using a unique object means no job id can ever collide with it.
    _STOP = object()

    def __init__(self, handler: Callable[[str], None], *, workers: int = 1,
                 duplicate_percent: int = 0, max_attempts: int = 3,
                 backoff_ms: int = 50, seed: Optional[int] = None) -> None:
        self._handler = handler
        self._fifo: _Fifo = _Fifo()
        self._max_attempts = max(1, max_attempts)
        self._backoff_ms = max(0, backoff_ms)
        self._duplicate_percent = min(100, max(0, duplicate_percent))
        # Seeded, so that "it duplicated on my machine and not on yours" is never something
        # you have to debug during a lab.
        self._rng = random.Random(seed)
        self._rng_lock = threading.Lock()

        self.delivered = 0
        self.duplicates_injected = 0
        self.retries = 0
        self.dead_lettered = 0
        self._counter_lock = threading.Lock()

        self._stopping = threading.Event()
        self._workers = [
            threading.Thread(target=self._run, name=f"docapp-worker-{i}", daemon=True)
            for i in range(max(1, workers))
        ]
        for worker in self._workers:
            worker.start()

    # ------------------------------------------------------------------ producer side

    def submit(self, job_id: str) -> None:
        """Hand the job off and return. The work has NOT happened when this returns."""
        if self._stopping.is_set():
            # Accepting work you will never do is worse than refusing it.
            raise RuntimeError("Queue is shutting down; refusing new work.")
        self._fifo.put((job_id, 1, False))

    # ------------------------------------------------------------------ consumer side

    def _run(self) -> None:
        while True:
            try:
                item = self._fifo.get(timeout=0.1)
            except Empty:
                if self._stopping.is_set():
                    return
                continue
            if item is self._STOP:
                self._fifo.task_done()
                return
            job_id, attempt, is_duplicate = item
            try:
                self._deliver(job_id, attempt, is_duplicate)
            finally:
                self._fifo.task_done()

    def _deliver(self, job_id: str, attempt: int, is_duplicate: bool) -> None:
        try:
            self._handler(job_id)
        except Exception as exc:  # noqa: BLE001 - a failed job must not kill the worker
            if attempt < self._max_attempts:
                with self._counter_lock:
                    self.retries += 1
                logs.warning("delivery failed, retrying", job_id=job_id, attempt=attempt,
                             error=str(exc), type=type(exc).__name__)
                # Backoff before the redelivery. Linear, and small, because this is a
                # teaching broker -- but the shape is the point: a retry that is instant is
                # a retry storm with extra steps.
                time.sleep(self._backoff_ms * attempt / 1000.0)
                self._fifo.put((job_id, attempt + 1, is_duplicate))
            else:
                with self._counter_lock:
                    self.dead_lettered += 1
                # Nowhere else to put it. A real broker would move it to a dead-letter
                # topic, where a human can look at it; logging loudly is this broker's
                # equivalent, and Lab 5 asks what is lost by not having the real thing.
                logs.error("delivery failed permanently, dead-lettering", job_id=job_id,
                           attempts=attempt, error=str(exc), type=type(exc).__name__)
            return

        with self._counter_lock:
            self.delivered += 1

        # A successful delivery may be delivered again. That is what at-least-once means:
        # the broker knows it handed the message over, and does not always know you
        # finished with it. Only originals are duplicated, so one message cannot multiply.
        if not is_duplicate and self._duplicate_percent:
            with self._rng_lock:
                roll = self._rng.randint(1, 100)
            if roll <= self._duplicate_percent:
                with self._counter_lock:
                    self.duplicates_injected += 1
                logs.info("injecting duplicate delivery", job_id=job_id)
                self._fifo.put((job_id, 1, True))

    # ------------------------------------------------------------------ lifecycle

    def drain(self, timeout: float = 10.0) -> bool:
        """Block until the queue is empty, or ``timeout`` expires. Returns True if empty.

        Tests need this, and so does anything that wants to shut down without throwing
        away accepted work. A queue you cannot wait for is a queue you cannot test.
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._fifo.unfinished_tasks == 0:
                return True
            time.sleep(0.01)
        return self._fifo.unfinished_tasks == 0

    def stop(self, timeout: float = 5.0) -> None:
        """Finish what has been accepted, then stop the workers."""
        self.drain(timeout=timeout)
        self._stopping.set()
        for _ in self._workers:
            self._fifo.put(self._STOP)
        for worker in self._workers:
            worker.join(timeout=timeout)

    def describe(self) -> dict[str, int]:
        """Counters, for /stats and for your Lab 5 evidence."""
        with self._counter_lock:
            return {
                "delivered": self.delivered,
                "duplicates_injected": self.duplicates_injected,
                "retries": self.retries,
                "dead_lettered": self.dead_lettered,
                "depth": self._fifo.qsize(),
            }
