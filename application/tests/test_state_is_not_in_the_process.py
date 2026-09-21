"""The Lab 1 lesson, pinned as a test.

Documents survive a restart because they are written to storage. Job records do not,
because the default job store keeps them in a dictionary inside the process.

Students observe this by hand in Lab 1 with two terminal windows. Capturing it here means
that when they implement ``FileJobStore``, they can see precisely which of these two
statements their work changes — and that nothing else changed with it.
"""

from __future__ import annotations

import pytest

from conftest import SAMPLE, make_config
from docapp.jobstore import JobNotFound
from docapp.wiring import build_application


def test_documents_survive_a_restart_but_jobs_do_not(tmp_path):
    config = make_config(tmp_path)

    # --- first "process" ---
    first = build_application(config).service
    doc = first.create_document("notes.txt", SAMPLE)
    job, _ = first.create_job(doc.id, "wordcount")
    assert job.status == "succeeded"

    # --- the process restarts: a completely new object graph, same data_dir ---
    second = build_application(config).service

    # The document is still there. It was written to storage, which outlives the process.
    assert second.get_document_bytes(doc.id) == SAMPLE

    # The job is gone. It lived in a dictionary, and the dictionary went with the process.
    with pytest.raises(JobNotFound):
        second.get_job(job.id)

    # This asymmetry is the entire point: execution is disposable, state is not — and
    # something is only "state" if it lives somewhere that outlives the execution.
    assert second.jobs.count() == 0
