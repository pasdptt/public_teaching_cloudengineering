"""The local broker: asynchronous, at-least-once, and bounded.

These tests run by default and need no cloud account. They are not the Lab 5 exercise --
``ThreadQueue`` is supplied -- but they pin the three behaviours Lab 5 is about, so that a
student reading them can see what "at-least-once" actually means before meeting a broker
that does it to them unpredictably.
"""

from __future__ import annotations

import threading

import pytest

from conftest import SAMPLE, make_config
from docapp.threadqueue import ThreadQueue
from docapp.wiring import build_application


def test_submit_returns_before_the_work_is_done():
    """The whole point of a queue, in one assertion."""
    started = threading.Event()
    allowed = threading.Event()
    done = threading.Event()

    def slow(job_id: str) -> None:
        started.set()
        allowed.wait(timeout=5)
        done.set()

    queue = ThreadQueue(slow)
    try:
        queue.submit("job-1")
        assert started.wait(timeout=5), "the worker never picked the job up"
        # submit() returned, the handler is still running, and nothing has completed.
        assert not done.is_set()
        allowed.set()
        assert queue.drain(timeout=5)
        assert done.is_set()
    finally:
        queue.stop()


def test_every_message_is_delivered_twice_when_asked():
    """At-least-once, made reproducible. The consumer sees the same id more than once."""
    seen: list[str] = []
    lock = threading.Lock()

    def record(job_id: str) -> None:
        with lock:
            seen.append(job_id)

    queue = ThreadQueue(record, duplicate_percent=100, seed=1)
    try:
        queue.submit("job-1")
        assert queue.drain(timeout=5)
    finally:
        queue.stop()

    assert seen == ["job-1", "job-1"]
    assert queue.describe()["duplicates_injected"] == 1


def test_a_duplicate_is_not_itself_duplicated():
    """Otherwise one submission becomes an infinite supply of work."""
    seen: list[str] = []
    lock = threading.Lock()

    def record(job_id: str) -> None:
        with lock:
            seen.append(job_id)

    queue = ThreadQueue(record, duplicate_percent=100, seed=1)
    try:
        for i in range(5):
            queue.submit(f"job-{i}")
        assert queue.drain(timeout=10)
    finally:
        queue.stop()

    assert len(seen) == 10, f"expected exactly two deliveries each, got {len(seen)}"


def test_a_failing_handler_is_retried_and_then_dead_lettered():
    """Bounded retries. An unbounded one is a retry storm with a nicer name."""
    attempts: list[int] = []
    lock = threading.Lock()

    def always_fails(job_id: str) -> None:
        with lock:
            attempts.append(1)
        raise RuntimeError("nope")

    queue = ThreadQueue(always_fails, max_attempts=3, backoff_ms=1)
    try:
        queue.submit("job-1")
        assert queue.drain(timeout=10)
    finally:
        queue.stop()

    assert len(attempts) == 3
    counters = queue.describe()
    assert counters["retries"] == 2
    assert counters["dead_lettered"] == 1
    assert counters["delivered"] == 0


def test_a_failure_does_not_kill_the_worker():
    """One poisonous message must not stop everything behind it."""
    survived: list[str] = []
    lock = threading.Lock()

    def sometimes(job_id: str) -> None:
        if job_id == "poison":
            raise RuntimeError("nope")
        with lock:
            survived.append(job_id)

    queue = ThreadQueue(sometimes, max_attempts=1)
    try:
        queue.submit("poison")
        queue.submit("fine")
        assert queue.drain(timeout=10)
    finally:
        queue.stop()

    assert survived == ["fine"]


def test_the_application_processes_a_job_asynchronously(tmp_path):
    """End to end through the real object graph, on the real seam.

    The job is PENDING when the caller is answered and SUCCEEDED a moment later. Students
    meet this in Lab 5 as a client-visible change: the API stops telling you the answer and
    starts telling you where to look for it.
    """
    config = make_config(tmp_path, queue_backend="thread")
    app = build_application(config)
    service = app.service

    doc = service.create_document("notes.txt", SAMPLE)
    job, created = service.create_job(doc.id, "wordcount")
    assert created

    # We cannot assert the job is still PENDING here without a race -- the worker may be
    # fast. What we CAN assert is that it reaches a terminal state without anyone asking.
    assert service._queue.drain(timeout=10)
    assert service.get_job(job.id).status == "succeeded"
    service._queue.stop()


def test_duplicate_delivery_does_not_do_the_work_twice(tmp_path):
    """The lesson of Lab 5, pinned.

    Every message is delivered twice. The document is processed once, because ``run_job``
    returns early for a job that has already finished. Delete that early return and this
    test is what fails.
    """
    config = make_config(tmp_path, queue_backend="thread", queue_duplicate_percent=100)
    app = build_application(config)
    service = app.service

    doc = service.create_document("notes.txt", SAMPLE)
    job, _ = service.create_job(doc.id, "wordcount")
    assert service._queue.drain(timeout=10)

    finished = service.get_job(job.id)
    assert finished.status == "succeeded"
    assert finished.attempts == 1, "the work was done more than once"
    assert service.counters.jobs_processed == 1
    assert service.counters.duplicate_deliveries_skipped == 1
    service._queue.stop()


def test_stats_reports_the_queue(tmp_path):
    """Evidence a student can collect from a running service without a metrics console."""
    config = make_config(tmp_path, queue_backend="thread", queue_duplicate_percent=100)
    service = build_application(config).service
    doc = service.create_document("notes.txt", SAMPLE)
    service.create_job(doc.id, "wordcount")
    assert service._queue.drain(timeout=10)

    stats = service.stats()
    assert stats["backends"]["queue"] == "thread"
    assert stats["queue"]["duplicates_injected"] == 1
    assert stats["duplicate_deliveries_skipped"] == 1
    service._queue.stop()


def test_the_inline_queue_reports_no_counters(tmp_path):
    """describe() is optional. A queue without it must not break /stats."""
    service = build_application(make_config(tmp_path)).service
    assert "queue" not in service.stats()
