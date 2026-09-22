"""Backend contracts, written once and run against every implementation.

A ``Storage`` is a ``Storage`` whether it writes to a directory or to Cloud Storage. If the
two behave differently, the application will behave differently after Lab 3 — and the whole
premise of the Protocol seam collapses.

So the rules live here, once, and every backend is held to them:

    LocalStorage       runs these on every test run
    GcsStorage         runs these in Lab 3, against a real bucket
    MemoryJobStore     runs these on every test run
    FileJobStore       runs these in Lab 1 (student exercise)
    FirestoreJobStore  runs these in Lab 3, against a real database

Writing the contract once is not tidiness. It is the only way to know that swapping a
backend changed *where* things are stored and nothing else.
"""

from __future__ import annotations

import pytest

from docapp.jobstore import JobNotFound
from docapp.models import Job
from docapp.storage import NotFound, StorageError


def a_job(**overrides) -> Job:
    job = Job.create(document_id="doc_1", operation="wordcount")
    for key, value in overrides.items():
        setattr(job, key, value)
    return job


class StorageContract:
    """Mix in and provide a ``storage`` fixture returning an empty backend."""

    def test_roundtrip(self, storage):
        storage.put("alpha/one.txt", b"hello")
        assert storage.get("alpha/one.txt") == b"hello"
        assert storage.exists("alpha/one.txt")

    def test_missing_object_raises_notfound(self, storage):
        with pytest.raises(NotFound):
            storage.get("absent")
        assert storage.exists("absent") is False

    def test_put_overwrites(self, storage):
        storage.put("k", b"first")
        storage.put("k", b"second")
        assert storage.get("k") == b"second"

    def test_delete_is_idempotent(self, storage):
        """Deleting twice must succeed. Every teardown and retry in this course needs it."""
        storage.put("k", b"v")
        storage.delete("k")
        storage.delete("k")
        assert storage.exists("k") is False

    def test_binary_content_survives_unchanged(self, storage):
        """Bytes in, the same bytes out. No encoding, no newline translation."""
        payload = bytes(range(256))
        storage.put("bin", payload)
        assert storage.get("bin") == payload

    def test_empty_value_is_storable(self, storage):
        """A zero-byte object exists and is distinct from an absent one."""
        storage.put("empty", b"")
        assert storage.exists("empty")
        assert storage.get("empty") == b""

    @pytest.mark.parametrize("key", ["../escape", "/absolute", "a/../../b", "", " padded"])
    def test_unsafe_keys_are_rejected(self, storage, key):
        """An object store has a flat namespace and would happily accept these.

        The application rejects them anyway, so that every backend enforces the same key
        rules. A key that is legal in one backend and dangerous in another is exactly the
        kind of difference that makes a swap unsafe.
        """
        with pytest.raises(StorageError):
            storage.put(key, b"x")


class JobStoreContract:
    """Mix in and provide a ``store`` fixture returning an empty backend."""

    def test_put_then_get(self, store):
        job = a_job()
        store.put(job)
        assert store.get(job.id).to_dict() == job.to_dict()

    def test_get_unknown_raises_jobnotfound(self, store):
        """Not None, not KeyError. Callers must not need to know the backend."""
        with pytest.raises(JobNotFound):
            store.get("job_missing")

    def test_put_replaces(self, store):
        job = a_job()
        store.put(job)
        job.status = "succeeded"
        job.result = {"words": 7}
        store.put(job)
        assert store.get(job.id).status == "succeeded"
        assert store.count() == 1

    def test_count_and_list_agree(self, store):
        for _ in range(5):
            store.put(a_job())
        assert store.count() == 5
        assert len(store.list_jobs()) == 5

    def test_list_is_newest_first_and_respects_limit(self, store):
        for i in range(5):
            store.put(a_job(created_ms=1000 + i))
        listed = store.list_jobs(limit=3)
        assert len(listed) == 3
        assert [j.created_ms for j in listed] == [1004, 1003, 1002]

    def test_delete_is_idempotent(self, store):
        job = a_job()
        store.put(job)
        store.delete(job.id)
        store.delete(job.id)
        with pytest.raises(JobNotFound):
            store.get(job.id)

    def test_find_by_idempotency_key(self, store):
        job = a_job(idempotency_key="order-42")
        store.put(job)
        found = store.find_by_idempotency_key("order-42")
        assert found is not None and found.id == job.id

    def test_find_by_unknown_key_returns_none(self, store):
        assert store.find_by_idempotency_key("never-used") is None

    def test_delete_releases_the_idempotency_key(self, store):
        """Otherwise a deleted job deduplicates submissions forever."""
        job = a_job(idempotency_key="k")
        store.put(job)
        store.delete(job.id)
        assert store.find_by_idempotency_key("k") is None

    def test_result_survives_a_roundtrip(self, store):
        """The result is a nested dict. Some backends flatten; this one must not."""
        job = a_job()
        job.status = "succeeded"
        job.result = {"words": 12, "top_words": [{"word": "a", "count": 3}], "nested": {"x": 1}}
        store.put(job)
        assert store.get(job.id).result == job.result
