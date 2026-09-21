"""Service behaviour: the properties the whole course is built on.

Idempotency and duplicate-delivery safety are tested here, in week 2, even though the queue
that makes them matter does not arrive until week 10. That is on purpose: the behaviour is
designed in from the start, and Lab 5 demonstrates why it was needed rather than adding it
in a panic.
"""

from __future__ import annotations

import pytest

from conftest import SAMPLE
from docapp.jobstore import JobNotFound
from docapp.models import FAILED, SUCCEEDED
from docapp.service import ValidationError


def test_document_roundtrip(service):
    doc = service.create_document("notes.txt", SAMPLE)
    assert doc.size_bytes == len(SAMPLE)
    assert service.get_document_bytes(doc.id) == SAMPLE
    assert service.get_document(doc.id).name == "notes.txt"


def test_empty_document_is_rejected(service):
    with pytest.raises(ValidationError):
        service.create_document("empty.txt", b"")


def test_oversized_document_is_rejected_with_the_limit_in_the_message(tmp_path):
    from conftest import make_config
    from docapp.wiring import build_application

    app = build_application(make_config(tmp_path, max_document_bytes=10))
    with pytest.raises(ValidationError) as exc:
        app.service.create_document("big.txt", b"x" * 11)
    assert "10" in str(exc.value)


def test_inline_queue_completes_the_job_before_create_returns(service):
    """With the inline queue, submission and completion are the same event.

    Lab 5 breaks this on purpose, and the difference is the lesson. Pinning the current
    behaviour here means that change is visible rather than silent.
    """
    doc = service.create_document("notes.txt", SAMPLE)
    job, created = service.create_job(doc.id, "wordcount")
    assert created is True
    assert job.status == SUCCEEDED
    assert job.result["words"] == 16
    assert job.attempts == 1


def test_job_for_unknown_document_is_rejected(service):
    with pytest.raises(ValidationError):
        service.create_job("doc_does_not_exist", "wordcount")


def test_unknown_operation_is_rejected(service):
    doc = service.create_document("notes.txt", SAMPLE)
    with pytest.raises(ValidationError):
        service.create_job(doc.id, "transmogrify")


# ----------------------------------------------------------------- idempotency

def test_same_idempotency_key_returns_the_same_job(service):
    doc = service.create_document("notes.txt", SAMPLE)
    first, created_first = service.create_job(doc.id, "wordcount", idempotency_key="k-1")
    second, created_second = service.create_job(doc.id, "wordcount", idempotency_key="k-1")

    assert created_first is True
    assert created_second is False
    assert first.id == second.id
    assert service.jobs.count() == 1
    assert service.counters.jobs_deduplicated == 1


def test_different_idempotency_keys_create_different_jobs(service):
    doc = service.create_document("notes.txt", SAMPLE)
    first, _ = service.create_job(doc.id, "wordcount", idempotency_key="k-1")
    second, _ = service.create_job(doc.id, "wordcount", idempotency_key="k-2")
    assert first.id != second.id
    assert service.jobs.count() == 2


def test_no_idempotency_key_means_no_deduplication(service):
    """Absence of a key is not a bug — it is the caller declining the guarantee."""
    doc = service.create_document("notes.txt", SAMPLE)
    first, _ = service.create_job(doc.id, "wordcount")
    second, _ = service.create_job(doc.id, "wordcount")
    assert first.id != second.id


# -------------------------------------------------------- duplicate delivery

def test_reprocessing_a_finished_job_is_a_no_op(service):
    """At-least-once delivery means this will happen for real in Lab 5.

    The second delivery must not run the work again, must not change the result, and must
    be counted so the behaviour is observable.
    """
    doc = service.create_document("notes.txt", SAMPLE)
    job, _ = service.create_job(doc.id, "wordcount")
    first_result = dict(job.result)
    attempts_after_first = job.attempts

    again = service.run_job(job.id)

    assert again.status == SUCCEEDED
    assert again.attempts == attempts_after_first  # no second attempt was made
    assert again.result == first_result            # result unchanged
    assert service.counters.duplicate_deliveries_skipped == 1
    assert service.counters.jobs_processed == 1    # the work ran exactly once


def test_run_job_for_unknown_id_raises(service):
    with pytest.raises(JobNotFound):
        service.run_job("job_nonexistent")


def test_job_fails_cleanly_when_its_document_disappears(service):
    """A failure must be recorded as a failure, not crash the worker.

    Students induce exactly this in Lab 1 by deleting a document mid-flight.
    """
    doc = service.create_document("notes.txt", SAMPLE)
    job, _ = service.create_job(doc.id, "wordcount")

    # Force the job back to a non-terminal state, then remove the document underneath it.
    job.status = "pending"
    job.completed_ms = None
    service.jobs.put(job)
    service.delete_document(doc.id)

    failed = service.run_job(job.id)
    assert failed.status == FAILED
    assert doc.id in failed.error
    assert service.counters.jobs_failed == 1


def test_stats_report_the_configured_backends(service):
    stats = service.stats()
    assert stats["backends"] == {"storage": "local", "jobstore": "memory", "queue": "inline"}
    assert stats["instance_id"] == "test-instance"
