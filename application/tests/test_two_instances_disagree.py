"""The Lab 4 lesson, pinned as a test.

``test_state_is_not_in_the_process`` shows state dying when one process restarts. That is
Lab 1, and students fix it by writing to somewhere durable.

This file shows the *other* half, which is the one that motivates Lab 4. Two instances
running at the same time, both perfectly healthy, neither having crashed — and they give
different answers to "what is the status of job X", because each holds its own copy of the
job records. No restart is involved. Nothing failed. The design is simply wrong the moment
there is more than one of it.

The local stand-in for "an external store both instances share" is literally sharing the
store object. That analogy has limits and they are worth saying out loud: a shared object
in one process has no network between the instances, no independent failure, and no
concurrent-write semantics to get wrong. What it does reproduce exactly is the property the
lab is about — whether the record lives inside an instance or outside every instance.

Students meet the real version in Lab 4, where the two instances are on different machines
in Iowa and the shared store is Firestore.
"""

from __future__ import annotations

import pytest

from conftest import SAMPLE, make_config
from docapp.jobstore import JobNotFound, MemoryJobStore
from docapp.queue import build_queue
from docapp.service import DocumentService
from docapp.storage import build_storage


def _instance(config, storage, jobs) -> DocumentService:
    """One instance of the service, assembled from parts we choose to share or not."""
    service = DocumentService(config, storage, jobs)
    service.attach_queue(build_queue(config.queue_backend, service.run_job))
    return service


def test_two_instances_with_private_job_stores_disagree(tmp_path):
    """Both instances are healthy. They still give different answers."""
    config = make_config(tmp_path, instance_id="instance-a")
    # Shared storage -- the documents are already external, as of Lab 3.
    storage = build_storage(config.storage_backend, config.data_dir, config.bucket)

    # ...but each instance keeps its own job records, which is the default the application
    # has shipped with since week 2.
    alpha = _instance(config, storage, MemoryJobStore())
    beta = _instance(make_config(tmp_path, instance_id="instance-b"), storage,
                     MemoryJobStore())

    doc = alpha.create_document("notes.txt", SAMPLE)
    job, created = alpha.create_job(doc.id, "wordcount")
    assert created and job.status == "succeeded"

    # The document is visible from both. It lives outside either of them.
    assert beta.get_document_bytes(doc.id) == SAMPLE

    # The job is not. A client whose next request lands on beta is told the job does not
    # exist -- and in Lab 4 the client has no way to ask for alpha again.
    with pytest.raises(JobNotFound):
        beta.get_job(job.id)


def test_idempotency_key_stops_working_across_instances(tmp_path):
    """The subtler failure, and the one that actually costs money.

    A client retries a submission it is not sure arrived. With one instance the retry is
    deduplicated. With two, the retry lands on the other one, finds no matching key, and
    the work is done twice -- silently, with two job ids, and with nothing in any log
    saying anything went wrong.
    """
    config = make_config(tmp_path, instance_id="instance-a")
    storage = build_storage(config.storage_backend, config.data_dir, config.bucket)
    alpha = _instance(config, storage, MemoryJobStore())
    beta = _instance(make_config(tmp_path, instance_id="instance-b"), storage,
                     MemoryJobStore())

    doc = alpha.create_document("notes.txt", SAMPLE)
    first, created_first = alpha.create_job(doc.id, "wordcount", idempotency_key="retry-me")
    assert created_first

    # Same key, same client intent, different instance.
    second, created_second = beta.create_job(doc.id, "wordcount", idempotency_key="retry-me")

    assert created_second, "beta cannot see alpha's key, so it creates a second job"
    assert second.id != first.id
    assert alpha.counters.jobs_processed == 1
    assert beta.counters.jobs_processed == 1  # the same work, done a second time


def test_one_shared_store_makes_both_instances_agree(tmp_path):
    """The fix, and it is not a code change -- it is a wiring change.

    Neither ``DocumentService`` nor any handler differs between this test and the two
    above. The only difference is where the job records live. That is why Lab 4 needs no
    application changes at all, and why Lab 3 had to come first.
    """
    config = make_config(tmp_path, instance_id="instance-a")
    storage = build_storage(config.storage_backend, config.data_dir, config.bucket)
    shared = MemoryJobStore()  # stands in for Firestore: one store, outside both instances

    alpha = _instance(config, storage, shared)
    beta = _instance(make_config(tmp_path, instance_id="instance-b"), storage, shared)

    doc = alpha.create_document("notes.txt", SAMPLE)
    job, _ = alpha.create_job(doc.id, "wordcount", idempotency_key="retry-me")

    assert beta.get_job(job.id).status == "succeeded"

    # The retry is deduplicated even though it landed on the other instance.
    same, created = beta.create_job(doc.id, "wordcount", idempotency_key="retry-me")
    assert not created and same.id == job.id

    # And the record says which instance did the work, which is how you answer "why is this
    # one slow" once there are twenty of them.
    assert beta.get_job(job.id).worker_instance == "instance-a"
