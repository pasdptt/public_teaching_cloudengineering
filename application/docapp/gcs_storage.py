"""Document bytes in Cloud Storage.

------------------------------------------------------------------------------------------
STUDENT WORK — Lab 3, Part 2. This class is deliberately unimplemented.
------------------------------------------------------------------------------------------

Your task is to satisfy the same ``Storage`` contract as ``LocalStorage``, so that changing
one environment variable moves every document from a directory on a disk to an object store
— and nothing else about the application changes.

The acceptance tests are already written, and they are the same contract ``LocalStorage``
passes:

    DOCAPP_TEST_BUCKET=your-bucket pytest -m lab03

Read ``tests/contracts.py`` first. It tells you exactly what "works" means.

Things worth deciding before you write code — the lab asks you to answer these, and they
are worth more marks than the implementation:

  1. ``LocalStorage.put`` writes to a temp file and renames, because a process killed
     mid-write would otherwise leave a truncated file. Does an object store need the
     equivalent? What happens to a reader if an upload is interrupted?
  2. ``delete`` must be idempotent. Is deleting an absent object an error in this API? If
     it is, what do you do about it, and why does it matter for a retried teardown?
  3. ``exists`` could be a metadata lookup or a download you throw away. One of those is a
     Class A operation and one is Class B, and they have different free-tier allowances
     (5,000 vs 50,000 per month). Which did you choose?
  4. ``LocalStorage`` rejects keys containing ``..``. An object store has a flat namespace
     and would accept them happily. Should this backend still reject them? The contract
     says yes — say why that is the right call rather than pointless strictness.

The import of the client library is deliberately INSIDE the constructor, not at the top of
this file. Work out why before you move it — ``application/README.md`` and the comment on
``_client`` will tell you if you get stuck.
"""

from __future__ import annotations

from typing import Any

from .storage import NotFound, StorageError, _validate_key


class GcsStorage:
    """Stores objects in a Cloud Storage bucket under an optional prefix."""

    def __init__(self, bucket_name: str, prefix: str = "") -> None:
        if not bucket_name:
            raise StorageError(
                "DOCAPP_BUCKET is not set. The Cloud Storage backend needs a bucket name. "
                "Either set it, or run with DOCAPP_STORAGE=local."
            )
        self.bucket_name = bucket_name
        self.prefix = prefix.strip("/")

        # Imported here, not at module top level, so that a student on the local or
        # fallback path never needs google-cloud-storage installed at all. The application
        # keeps its zero-dependency start-up; only this backend pays for the library.
        try:
            from google.cloud import storage  # type: ignore
        except ImportError as exc:
            raise StorageError(
                "google-cloud-storage is not installed, but DOCAPP_STORAGE=gcs.\n"
                "  pip3 install -r application/requirements.txt\n"
                "Or run with DOCAPP_STORAGE=local."
            ) from exc

        self._client: Any = storage.Client()
        self._bucket = self._client.bucket(bucket_name)

        raise NotImplementedError(
            "GcsStorage is your Lab 3 exercise and is not implemented yet.\n"
            "Run `DOCAPP_TEST_BUCKET=<bucket> pytest -m lab03` to see what it must do, then "
            "implement it here. Until then, run with DOCAPP_STORAGE=local."
        )

    def _blob(self, key: str):
        """Resolve a contract key to a blob. Supplied — the naming is not the exercise."""
        safe = _validate_key(key)
        name = f"{self.prefix}/{safe}" if self.prefix else safe
        return self._bucket.blob(name)

    # TODO(lab03): implement put(self, key: str, data: bytes) -> None
    # TODO(lab03): implement get(self, key: str) -> bytes        # raise NotFound if absent
    # TODO(lab03): implement delete(self, key: str) -> None      # must be idempotent
    # TODO(lab03): implement exists(self, key: str) -> bool
