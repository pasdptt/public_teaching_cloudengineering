"""Where job records live.

This module is the heart of the course's first real lesson.

The default backend, ``MemoryJobStore``, keeps job records in a Python dictionary. It
works perfectly — until the process stops. Restart the server and every job is gone, even
though the documents those jobs referred to are still sitting safely on disk.

That is not a bug to be embarrassed about. It is the difference between *execution* and
*state*, and Lab 1 asks students to observe it, explain it, and then fix it by implementing
``FileJobStore`` against the contract below.

In Lab 3 the same contract is satisfied by Firestore, and the application again does not
notice. An interface that survived being moved from a dict, to a file, to a managed
database is an interface worth having.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
from typing import Any, Iterable, Optional, Protocol

from .models import Job


class JobStoreError(RuntimeError):
    """A job store operation failed."""


class JobNotFound(JobStoreError):
    """No job with that id."""


class JobStore(Protocol):
    """The contract every job store must satisfy.

    ``find_by_idempotency_key`` is not an optional extra. It is what lets the API return
    the *same* job when a client retries a submission — the difference between a user
    double-clicking and a user creating two jobs.
    """

    def put(self, job: Job) -> None: ...
    def get(self, job_id: str) -> Job: ...
    def find_by_idempotency_key(self, key: str) -> Optional[Job]: ...
    def list_jobs(self, limit: int = 50) -> list[Job]: ...
    def delete(self, job_id: str) -> None: ...
    def count(self) -> int: ...


class MemoryJobStore:
    """Job records in a dictionary. Fast, simple, and gone when the process ends.

    This is the default so that Lab 1's failure exercise happens by itself rather than
    having to be staged. Students start the server, create a job, restart the server, and
    watch it disappear.

    Thread-safe, because the HTTP server is threaded and two concurrent requests really can
    touch this at the same time. A race here would be a distraction from the lesson rather
    than part of it.
    """

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._by_key: dict[str, str] = {}
        self._lock = threading.Lock()

    def put(self, job: Job) -> None:
        with self._lock:
            self._jobs[job.id] = job
            if job.idempotency_key:
                self._by_key[job.idempotency_key] = job.id

    def get(self, job_id: str) -> Job:
        with self._lock:
            try:
                return self._jobs[job_id]
            except KeyError:
                raise JobNotFound(f"No job with id {job_id!r}.") from None

    def find_by_idempotency_key(self, key: str) -> Optional[Job]:
        with self._lock:
            job_id = self._by_key.get(key)
            return self._jobs.get(job_id) if job_id else None

    def list_jobs(self, limit: int = 50) -> list[Job]:
        with self._lock:
            jobs = sorted(self._jobs.values(), key=lambda j: j.created_ms, reverse=True)
            return jobs[:limit]

    def delete(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs.pop(job_id, None)
            if job and job.idempotency_key:
                self._by_key.pop(job.idempotency_key, None)

    def count(self) -> int:
        with self._lock:
            return len(self._jobs)


class FileJobStore:
    """Durable job records, written to a JSON file.

    ------------------------------------------------------------------------------
    STUDENT WORK — Lab 1.  This class is deliberately unimplemented.
    ------------------------------------------------------------------------------

    Your task is to make this satisfy the same ``JobStore`` contract as
    ``MemoryJobStore``, so that job records survive a restart of the server.

    The acceptance tests are already written. They are the specification:

        pytest -m lab01

    Read them before you start. They will tell you more precisely than this docstring
    what "works" means.

    Things worth thinking about before you write any code — these are the questions the
    lab asks you to answer, not just hurdles:

      1. When should the file be read, and when written? Reading on every call is simple
         and slow; caching in memory is fast and can go stale. Which problem would you
         rather have here, and why?
      2. The HTTP server is threaded. Two requests can call ``put`` at the same moment.
         What goes wrong if you ignore that?
      3. If the process is killed *while* you are writing the file, what does the next
         start-up read? Look at how ``LocalStorage.put`` in ``storage.py`` avoids this,
         and decide whether the same technique applies.
      4. ``MemoryJobStore`` keeps a second dictionary to look up jobs by idempotency key.
         Do you need the equivalent, or can you do without it? What does your answer cost?

    You are not expected to build a database. A few dozen lines is the right size. If you
    find yourself writing more than that, stop and re-read question 1.
    """

    def __init__(self, path: str) -> None:
        self.path = os.path.abspath(path)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._lock = threading.Lock()
        # TODO(lab01): decide what state, if any, you keep in memory alongside the file.
        raise NotImplementedError(
            "FileJobStore is your Lab 1 exercise and is not implemented yet.\n"
            "Run `pytest -m lab01` to see exactly what it needs to do, then implement it "
            "here. Until then, run the application with DOCAPP_JOBSTORE=memory."
        )

    # TODO(lab01): implement put()
    # TODO(lab01): implement get()
    # TODO(lab01): implement find_by_idempotency_key()
    # TODO(lab01): implement list_jobs()
    # TODO(lab01): implement delete()
    # TODO(lab01): implement count()

    # ---- helpers you may use, or ignore entirely ----

    @staticmethod
    def _serialise(jobs: Iterable[Job]) -> str:
        return json.dumps([j.to_dict() for j in jobs], indent=2, sort_keys=True)

    @staticmethod
    def _deserialise(text: str) -> list[Job]:
        if not text.strip():
            return []
        try:
            raw: Any = json.loads(text)
        except json.JSONDecodeError as exc:
            raise JobStoreError(
                f"The job file is not valid JSON ({exc}). If this happened after the "
                f"process was killed mid-write, that is question 3 in the docstring."
            ) from exc
        return [Job.from_dict(item) for item in raw]

    @staticmethod
    def _atomic_write(path: str, text: str) -> None:
        """Write ``text`` to ``path`` so that a crash cannot leave a half-written file."""
        directory = os.path.dirname(path) or "."
        fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(text)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, path)
        except OSError:
            try:
                os.remove(tmp)
            except OSError:
                pass
            raise


def build_jobstore(backend: str, data_dir: str) -> JobStore:
    """Factory. Lab 3 adds a Firestore branch here; nothing else changes."""
    if backend == "memory":
        return MemoryJobStore()
    if backend == "file":
        return FileJobStore(os.path.join(data_dir, "jobs", "jobs.json"))
    raise JobStoreError(
        f"Unknown job store backend {backend!r}. This build supports: memory, file."
    )
