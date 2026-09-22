"""Job records in Firestore.

------------------------------------------------------------------------------------------
STUDENT WORK — Lab 3, Part 3. This class is deliberately unimplemented.
------------------------------------------------------------------------------------------

In Lab 1 you moved job records from a dictionary to a file, so they survived a restart. That
was enough for one process on one machine. It stops being enough the moment there is more
than one instance — which is exactly what happens in Lab 4.

A file on an instance's disk is state that belongs to *that instance*. Two instances, two
files, two different answers to "what is the status of job X". Firestore is where the
records go so that every instance sees the same ones.

The acceptance tests are the same contract every other job store satisfies:

    DOCAPP_TEST_PROJECT=your-project pytest -m lab03

Decide these before you write code — they carry more marks than the implementation:

  1. Which Firestore collection, and what is the document id? You have a natural key
     already. Using it is not the only option; say why you chose what you chose.
  2. ``find_by_idempotency_key`` is a lookup by a field that is not the document id. That is
     a *query*, and queries may need an index. What did you do, and what does it cost?
  3. ``list_jobs`` returns newest first with a limit. How do you order in Firestore, and
     what happens to the free-tier read quota if you get this wrong? (50,000 reads per day,
     and a query that scans reads every document it examines.)
  4. ``count()``. There is a cheap way and an expensive way. Which did you use, and what
     would the expensive one cost you on a collection with 10,000 jobs?
  5. ``get`` on a missing id must raise ``JobNotFound``. Firestore returns a snapshot that
     simply does not exist. Where do you convert one into the other, and why does the
     contract insist on this?

**Free-tier constraint you must respect:** one free Firestore database per project, and it
must be the ``(default)`` one. A *named* database qualifies for no free quota at all and
bills from its first operation (course/references.md R-11). Do not create a named database.

As with the Cloud Storage backend, the client library is imported inside the constructor so
that the local path needs nothing installed.
"""

from __future__ import annotations

from typing import Any, Optional

from .jobstore import JobStoreError
from .models import Job

# The collection name is supplied. Naming it is not the exercise; deciding what goes in it is.
COLLECTION = "jobs"


class FirestoreJobStore:
    """Job records in the project's free ``(default)`` Firestore database."""

    def __init__(self, project_id: str) -> None:
        if not project_id:
            raise JobStoreError(
                "DOCAPP_PROJECT_ID is not set. The Firestore backend needs a project. "
                "Either set it, or run with DOCAPP_JOBSTORE=memory."
            )
        self.project_id = project_id

        try:
            from google.cloud import firestore  # type: ignore
        except ImportError as exc:
            raise JobStoreError(
                "google-cloud-firestore is not installed, but DOCAPP_JOBSTORE=firestore.\n"
                "  pip3 install -r application/requirements.txt\n"
                "Or run with DOCAPP_JOBSTORE=memory."
            ) from exc

        # No database= argument: that selects the (default) database, which is the only one
        # covered by the free quota. Passing a name here would start billing immediately.
        self._db: Any = firestore.Client(project=project_id)

        raise NotImplementedError(
            "FirestoreJobStore is your Lab 3 exercise and is not implemented yet.\n"
            "Run `DOCAPP_TEST_PROJECT=<project> pytest -m lab03` to see what it must do. "
            "Until then, run with DOCAPP_JOBSTORE=memory."
        )

    @staticmethod
    def _to_document(job: Job) -> dict:
        """Supplied. A Job is already a flat dataclass with a nested result dict."""
        return job.to_dict()

    @staticmethod
    def _from_document(data: dict) -> Job:
        """Supplied. Job.from_dict already tolerates fields it does not recognise."""
        return Job.from_dict(data)

    # TODO(lab03): implement put(self, job: Job) -> None
    # TODO(lab03): implement get(self, job_id: str) -> Job            # raise JobNotFound
    # TODO(lab03): implement find_by_idempotency_key(self, key) -> Optional[Job]
    # TODO(lab03): implement list_jobs(self, limit: int = 50) -> list[Job]
    # TODO(lab03): implement delete(self, job_id: str) -> None        # idempotent
    # TODO(lab03): implement count(self) -> int
