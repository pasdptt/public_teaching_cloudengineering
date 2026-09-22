"""The application's actual behaviour, independent of HTTP.

Everything the service can do lives here as a plain method taking and returning plain data.
The HTTP layer in ``app.py`` does nothing but translate between requests and these calls.

That separation is why the same logic runs unchanged behind a web request in week 2 and
behind a queue consumer in week 10, and why the tests can exercise real behaviour without
starting a server.
"""

from __future__ import annotations

from typing import Any, Optional

from . import logs
from .config import Config
from .jobstore import JobNotFound, JobStore
from .models import (
    ALL_STATES, FAILED, OPERATIONS, PENDING, RUNNING, SUCCEEDED,
    Counters, Document, Job, now_ms,
)
from .processing import ProcessingError, process
from .queue import Queue
from .storage import NotFound as StorageNotFound
from .storage import Storage


class ValidationError(ValueError):
    """The caller asked for something that does not make sense. Becomes HTTP 400."""


class DocumentService:
    """Documents in, jobs out.

    Holds one Storage, one JobStore and one Queue. Which concrete implementations those
    are is decided at start-up and is not this class's business — that indifference is the
    property that lets Labs 3, 4 and 5 change infrastructure without changing behaviour.
    """

    def __init__(self, config: Config, storage: Storage, jobs: JobStore) -> None:
        self.config = config
        self.storage = storage
        self.jobs = jobs
        self.counters = Counters()
        self._queue: Optional[Queue] = None
        # Document metadata lives beside the bytes, in storage, so that it moves with them
        # when Lab 3 swaps the backend. Job records go to the job store instead, because
        # they change constantly and object storage is a poor place for mutable records.
        # Being able to explain that split is part of Lab 3.

    def attach_queue(self, queue: Queue) -> None:
        """Wired after construction because the queue's handler calls back into us."""
        self._queue = queue

    # ------------------------------------------------------------------ documents

    def create_document(self, name: str, data: bytes,
                        content_type: str = "text/plain") -> Document:
        if not name or len(name) > 200:
            raise ValidationError("Document name must be between 1 and 200 characters.")
        if not data:
            raise ValidationError("Document is empty. Send some content to store.")
        if len(data) > self.config.max_document_bytes:
            raise ValidationError(
                f"Document is {len(data)} bytes, over the {self.config.max_document_bytes} "
                f"byte limit. The limit exists to keep labs bounded; raise "
                f"DOCAPP_MAX_DOCUMENT_BYTES if a lab tells you to."
            )

        doc = Document.create(name=name, size_bytes=len(data), content_type=content_type)
        self.storage.put(f"{doc.id}/content", data)
        self.storage.put(f"{doc.id}/metadata.json", _json_bytes(doc.to_dict()))
        self.counters.documents_created += 1
        logs.info("document created", document_id=doc.id, name=name, size_bytes=len(data))
        return doc

    def get_document_bytes(self, document_id: str) -> bytes:
        return self.storage.get(f"{document_id}/content")

    def get_document(self, document_id: str) -> Document:
        raw = self.storage.get(f"{document_id}/metadata.json")
        return Document.from_dict(_json_loads(raw))

    def delete_document(self, document_id: str) -> None:
        """Idempotent: deleting a document that is already gone succeeds quietly."""
        self.storage.delete(f"{document_id}/content")
        self.storage.delete(f"{document_id}/metadata.json")
        logs.info("document deleted", document_id=document_id)

    # ----------------------------------------------------------------------- jobs

    def create_job(self, document_id: str, operation: str,
                   idempotency_key: Optional[str] = None) -> tuple[Job, bool]:
        """Create a job, or return the existing one for this idempotency key.

        Returns ``(job, created)``. ``created`` is False when an existing job was returned.

        This is the whole idempotency story in one method, and it is here from week 2 rather
        than being retrofitted in week 10. Retrying a submission that may already have
        succeeded is the normal case in a distributed system, not an edge case: the network
        can swallow a response after the work was done, and the client cannot tell that
        apart from the request never arriving.
        """
        if operation not in OPERATIONS:
            raise ValidationError(
                f"Unknown operation {operation!r}. Supported: {', '.join(OPERATIONS)}."
            )
        if not self.storage.exists(f"{document_id}/content"):
            raise ValidationError(f"No document with id {document_id!r}.")

        if idempotency_key:
            existing = self.jobs.find_by_idempotency_key(idempotency_key)
            if existing is not None:
                self.counters.jobs_deduplicated += 1
                logs.info("job deduplicated", job_id=existing.id,
                          idempotency_key=idempotency_key)
                return existing, False

        job = Job.create(document_id=document_id, operation=operation,
                         idempotency_key=idempotency_key)
        self.jobs.put(job)
        self.counters.jobs_created += 1
        logs.info("job created", job_id=job.id, document_id=document_id,
                  operation=operation)

        if self._queue is None:
            raise RuntimeError("No queue attached. This is a wiring bug, not a user error.")
        self._queue.submit(job.id)
        # Re-read: with the inline queue the job is already finished by now, and the caller
        # should see that rather than a stale PENDING record. With a real queue in Lab 5 it
        # will still be PENDING here -- and that difference is the point of the lab.
        return self.jobs.get(job.id), True

    def get_job(self, job_id: str) -> Job:
        return self.jobs.get(job_id)

    def list_jobs(self, limit: int = 50) -> list[Job]:
        return self.jobs.list_jobs(limit=limit)

    # ------------------------------------------------------------------- the work

    def run_job(self, job_id: str) -> Job:
        """Process one job. Safe to call more than once for the same job.

        Re-delivery safety is built in rather than bolted on: if the job has already reached
        a terminal state, this returns immediately without reprocessing. Once Lab 5
        introduces at-least-once delivery, that early return is what stands between the
        service and doing everything twice.
        """
        try:
            job = self.jobs.get(job_id)
        except JobNotFound:
            # A message for a job that does not exist. With a real queue this happens for
            # real -- a message outliving its job record -- and dropping it is correct.
            logs.warning("job not found, dropping", job_id=job_id)
            raise

        if job.is_terminal:
            self.counters.duplicate_deliveries_skipped += 1
            logs.info("duplicate delivery skipped", job_id=job.id, status=job.status,
                      attempts=job.attempts)
            return job

        job.status = RUNNING
        job.attempts += 1
        job.updated_ms = now_ms()
        job.worker_instance = self.config.instance_id
        self.jobs.put(job)

        try:
            data = self.storage.get(f"{job.document_id}/content")
        except StorageNotFound:
            return self._fail(job, f"Document {job.document_id} no longer exists.")

        try:
            result = process(job.operation, data, delay_ms=self.config.processing_delay_ms)
        except ProcessingError as exc:
            return self._fail(job, str(exc))

        job.status = SUCCEEDED
        job.result = result
        job.error = None
        job.updated_ms = now_ms()
        job.completed_ms = job.updated_ms
        self.jobs.put(job)
        self.counters.jobs_processed += 1
        logs.info("job succeeded", job_id=job.id, operation=job.operation,
                  attempts=job.attempts, duration_ms=result.get("duration_ms"))
        return job

    def _fail(self, job: Job, message: str) -> Job:
        job.status = FAILED
        job.error = message
        job.updated_ms = now_ms()
        job.completed_ms = job.updated_ms
        self.jobs.put(job)
        self.counters.jobs_failed += 1
        logs.error("job failed", job_id=job.id, operation=job.operation,
                   attempts=job.attempts, error=message)
        return job

    # ------------------------------------------------------------------ inspection

    def stats(self) -> dict[str, Any]:
        data = self.counters.to_dict()
        data["jobs_in_store"] = self.jobs.count()
        data["instance_id"] = self.config.instance_id
        data["backends"] = {
            "storage": self.config.storage_backend,
            "jobstore": self.config.jobstore_backend,
            "queue": self.config.queue_backend,
        }
        # Some queues can say something about themselves: depth, retries, how many
        # duplicates they injected. Asked for by duck typing rather than declared on the
        # Protocol, because a queue that cannot introspect itself -- which includes every
        # real broker, from inside the application -- is still a perfectly good queue.
        describe = getattr(self._queue, "describe", None)
        if callable(describe):
            data["queue"] = describe()
        return data


def _json_bytes(obj: Any) -> bytes:
    import json
    return json.dumps(obj, sort_keys=True).encode("utf-8")


def _json_loads(raw: bytes) -> Any:
    import json
    return json.loads(raw.decode("utf-8"))


__all__ = ["DocumentService", "ValidationError", "ALL_STATES", "PENDING", "RUNNING",
           "SUCCEEDED", "FAILED"]
