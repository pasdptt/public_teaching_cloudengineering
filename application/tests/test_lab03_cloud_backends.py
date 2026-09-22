"""ACCEPTANCE TESTS — Lab 3, the Cloud Storage and Firestore backends.

    DOCAPP_TEST_BUCKET=your-bucket   pytest -m lab03      # Cloud Storage
    DOCAPP_TEST_PROJECT=your-project pytest -m lab03      # Firestore

**These tests touch real cloud resources.** They are skipped unless you point them at
something, so nobody runs them by accident and nobody is billed by surprise.

Notice what is — and is not — in this file. The rules are **not** restated here: they are
imported from ``contracts.py``, the same ones ``LocalStorage`` and ``MemoryJobStore``
already satisfy. That is the point of Lab 3. If your Cloud Storage backend passes the
contract that a directory on your laptop passes, then swapping them changes *where* your
documents live and nothing else.

Cost: at these volumes, nothing. Each run writes a handful of small objects and documents,
far inside the 5,000 Class A operations and 20,000 Firestore writes per day. Clean-up runs
after every test — read the fixtures and satisfy yourself that it does.
"""

from __future__ import annotations

import os
import uuid

import pytest

from contracts import JobStoreContract, StorageContract

pytestmark = pytest.mark.lab03

TEST_BUCKET = os.environ.get("DOCAPP_TEST_BUCKET", "").strip()
TEST_PROJECT = os.environ.get("DOCAPP_TEST_PROJECT", "").strip()


@pytest.mark.skipif(not TEST_BUCKET, reason="set DOCAPP_TEST_BUCKET to run these")
class TestGcsStorage(StorageContract):
    """The same contract LocalStorage passes. Nothing extra, nothing relaxed."""

    @pytest.fixture
    def storage(self):
        from docapp.gcs_storage import GcsStorage

        # A unique prefix per test run, so a failed run cannot poison the next one and two
        # students can safely share a bucket.
        prefix = f"test-{uuid.uuid4().hex[:12]}"
        store = GcsStorage(TEST_BUCKET, prefix=prefix)
        yield store
        # Tidy up whatever the test wrote. Best effort: a failing implementation must not
        # leave the next run to deal with its mess.
        for key in ("alpha/one.txt", "k", "bin", "empty", "absent", "a/b/c/d.txt"):
            try:
                store.delete(key)
            except Exception:  # noqa: BLE001 - cleanup must not mask the real failure
                pass


@pytest.mark.skipif(not TEST_PROJECT, reason="set DOCAPP_TEST_PROJECT to run these")
class TestFirestoreJobStore(JobStoreContract):
    """The same contract MemoryJobStore passes."""

    @pytest.fixture
    def store(self):
        from docapp.firestore_jobstore import FirestoreJobStore

        store = FirestoreJobStore(TEST_PROJECT)
        # Start from empty, so a leftover job from a previous run cannot make
        # test_count_and_list_agree fail for a reason that is not your code.
        for job in store.list_jobs(limit=200):
            store.delete(job.id)
        yield store
        for job in store.list_jobs(limit=200):
            store.delete(job.id)


@pytest.mark.skipif(not (TEST_BUCKET and TEST_PROJECT),
                    reason="set both DOCAPP_TEST_BUCKET and DOCAPP_TEST_PROJECT")
def test_the_application_runs_end_to_end_on_cloud_backends(tmp_path):
    """The final check: the whole application, on cloud backends, restarted.

    If every contract test passes and this one does not, the problem is wiring rather than
    the backends — start with ``build_storage`` and ``build_jobstore``.
    """
    from conftest import SAMPLE, make_config
    from docapp.wiring import build_application

    config = make_config(
        tmp_path,
        storage_backend="gcs",
        jobstore_backend="firestore",
        bucket=TEST_BUCKET,
        project_id=TEST_PROJECT,
    )

    first = build_application(config).service
    doc = first.create_document("notes.txt", SAMPLE)
    job, _ = first.create_job(doc.id, "wordcount", idempotency_key="cloud-run-1")
    assert job.status == "succeeded"
    assert job.result["words"] == 16

    # A completely new object graph, as if the process had been replaced -- which, in
    # Lab 4, it will be, on a different machine.
    second = build_application(config).service
    assert second.get_document_bytes(doc.id) == SAMPLE
    restored = second.get_job(job.id)
    assert restored.status == "succeeded"

    # And the idempotency key still works across that boundary, so a client retrying after
    # an instance was replaced does not get a second job.
    again, created = second.create_job(doc.id, "wordcount", idempotency_key="cloud-run-1")
    assert created is False
    assert again.id == job.id

    second.delete_document(doc.id)
    second.jobs.delete(job.id)
