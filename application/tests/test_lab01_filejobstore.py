"""ACCEPTANCE TESTS — Lab 1, FileJobStore.

    Run them with:   pytest -m lab01

These are the specification for the exercise in ``docapp/jobstore.py``. They are excluded
from the default test run so that a fresh clone is green; you opt into them.

Read them before you write any code. Every test says, in its name and its docstring, one
thing your implementation has to be true of — and the order they appear in is a reasonable
order to make them pass.

They do not tell you *how*. That part is yours, and the lab asks you to explain the choice
you made.
"""

from __future__ import annotations

import os
import threading

import pytest

from conftest import SAMPLE, make_config
from docapp.jobstore import FileJobStore, JobNotFound
from docapp.models import Job
from docapp.wiring import build_application

pytestmark = pytest.mark.lab01


@pytest.fixture
def store(tmp_path):
    return FileJobStore(str(tmp_path / "jobs" / "jobs.json"))


def a_job(**overrides) -> Job:
    job = Job.create(document_id="doc_1", operation="wordcount")
    for key, value in overrides.items():
        setattr(job, key, value)
    return job


# ---------------------------------------------------------------- the basics

def test_put_then_get_returns_an_equal_job(store):
    job = a_job()
    store.put(job)
    assert store.get(job.id).to_dict() == job.to_dict()


def test_get_of_an_unknown_id_raises_jobnotfound(store):
    """Not ``None``, not ``KeyError`` — the same exception MemoryJobStore raises.

    Callers must not have to know which backend they are talking to.
    """
    with pytest.raises(JobNotFound):
        store.get("job_missing")


def test_put_of_an_existing_id_replaces_it(store):
    """A job is updated many times as it moves pending → running → succeeded."""
    job = a_job()
    store.put(job)
    job.status = "succeeded"
    job.result = {"words": 7}
    store.put(job)
    assert store.get(job.id).status == "succeeded"
    assert store.count() == 1


def test_count_and_list_agree(store):
    for _ in range(5):
        store.put(a_job())
    assert store.count() == 5
    assert len(store.list_jobs()) == 5


def test_list_is_newest_first_and_respects_limit(store):
    jobs = [a_job(created_ms=1000 + i) for i in range(5)]
    for job in jobs:
        store.put(job)
    listed = store.list_jobs(limit=3)
    assert len(listed) == 3
    assert [j.created_ms for j in listed] == [1004, 1003, 1002]


def test_delete_removes_the_job_and_is_idempotent(store):
    job = a_job()
    store.put(job)
    store.delete(job.id)
    store.delete(job.id)  # second delete must not raise
    with pytest.raises(JobNotFound):
        store.get(job.id)


# ------------------------------------------------------------- idempotency keys

def test_find_by_idempotency_key(store):
    job = a_job(idempotency_key="order-42")
    store.put(job)
    found = store.find_by_idempotency_key("order-42")
    assert found is not None and found.id == job.id


def test_find_by_unknown_key_returns_none(store):
    assert store.find_by_idempotency_key("never-used") is None


def test_deleting_a_job_also_releases_its_idempotency_key(store):
    """Otherwise a deleted job keeps deduplicating submissions forever."""
    job = a_job(idempotency_key="k")
    store.put(job)
    store.delete(job.id)
    assert store.find_by_idempotency_key("k") is None


# ----------------------------------------------------- the point of the exercise

def test_jobs_survive_a_restart(tmp_path):
    """THE test. Everything else is scaffolding around this one.

    A brand-new store object, pointed at the same file, must see what the previous one
    wrote. This is what makes the job record *state* rather than something the process
    happens to remember.
    """
    path = str(tmp_path / "jobs" / "jobs.json")
    first = FileJobStore(path)
    job = a_job(idempotency_key="survive-me")
    job.status = "succeeded"
    job.result = {"words": 99}
    first.put(job)

    second = FileJobStore(path)          # as if the process had been restarted
    restored = second.get(job.id)
    assert restored.status == "succeeded"
    assert restored.result == {"words": 99}
    assert second.find_by_idempotency_key("survive-me").id == job.id


def test_a_fresh_store_on_a_missing_file_is_simply_empty(tmp_path):
    """First ever start-up is not an error condition."""
    store = FileJobStore(str(tmp_path / "nothing" / "yet.json"))
    assert store.count() == 0
    assert store.list_jobs() == []


def test_concurrent_writes_do_not_lose_jobs(tmp_path):
    """The HTTP server is threaded, so this really happens.

    Twenty threads each write one job. All twenty must be there afterwards. If your
    implementation reads the file, modifies it, and writes it back without holding a lock,
    this test is where you find out.
    """
    store = FileJobStore(str(tmp_path / "jobs" / "jobs.json"))
    errors: list[BaseException] = []

    def write_one() -> None:
        try:
            store.put(a_job())
        except BaseException as exc:  # noqa: BLE001 - reported, not swallowed
            errors.append(exc)

    threads = [threading.Thread(target=write_one) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=20)

    assert errors == []
    assert store.count() == 20
    assert FileJobStore(str(tmp_path / "jobs" / "jobs.json")).count() == 20


def test_no_temporary_files_are_left_behind(tmp_path):
    """A store that leaks temp files fills a disk. On a 30 GB free allowance, that matters."""
    directory = tmp_path / "jobs"
    store = FileJobStore(str(directory / "jobs.json"))
    for _ in range(25):
        store.put(a_job())
    assert [p for p in os.listdir(directory) if p.endswith(".tmp")] == []


# -------------------------------------------------- it has to work in the real app

def test_the_application_works_end_to_end_with_the_file_backend(tmp_path):
    """The final check: run the whole application on your store, restart it, and find the
    job still there.

    If every earlier test passes and this one does not, the problem is in wiring rather
    than in the store — start with ``build_jobstore`` in ``jobstore.py``.
    """
    config = make_config(tmp_path, jobstore_backend="file")

    first = build_application(config).service
    doc = first.create_document("notes.txt", SAMPLE)
    job, _ = first.create_job(doc.id, "wordcount", idempotency_key="run-1")
    assert job.status == "succeeded"

    second = build_application(config).service          # restart
    restored = second.get_job(job.id)
    assert restored.status == "succeeded"
    assert restored.result["words"] == 16

    # And the idempotency key still works across the restart, so a client retrying after
    # the server bounced does not get a second job.
    again, created = second.create_job(doc.id, "wordcount", idempotency_key="run-1")
    assert created is False
    assert again.id == job.id
