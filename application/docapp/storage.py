"""Where document bytes live.

The ``Storage`` Protocol is the seam. Today there is one implementation, ``LocalStorage``,
which writes to a directory. In Lab 3 students add a Cloud Storage implementation and
change one environment variable — the rest of the application does not know the difference.

That is the lesson, not the code: an application that names an *abstraction* can move; one
that calls ``open()`` in its request handler cannot.
"""

from __future__ import annotations

import os
import tempfile
from typing import Protocol


class StorageError(RuntimeError):
    """A storage operation failed for a reason the caller may be able to act on."""


class NotFound(StorageError):
    """The requested object does not exist."""


class Storage(Protocol):
    """The contract every storage backend must satisfy.

    Four operations. Anything a backend cannot do in four operations is something this
    application should not be asking a storage system to do.
    """

    def put(self, key: str, data: bytes) -> None: ...
    def get(self, key: str) -> bytes: ...
    def delete(self, key: str) -> None: ...
    def exists(self, key: str) -> bool: ...


def _validate_key(key: str) -> str:
    """Reject anything that could escape the storage root.

    ``../`` in a key is the oldest bug in file-backed storage. Object stores have a flat
    namespace and do not care; a directory does. Validating here rather than in
    LocalStorage keeps every backend honest about the same key rules, which is what makes
    the backends interchangeable.
    """
    if not key or key.strip() != key:
        raise StorageError(f"Invalid storage key {key!r}: must be non-empty and unpadded.")
    if key.startswith("/") or ".." in key.split("/"):
        raise StorageError(
            f"Invalid storage key {key!r}: keys are relative and may not contain '..'."
        )
    if any(c in key for c in "\\\0"):
        raise StorageError(f"Invalid storage key {key!r}: contains a forbidden character.")
    return key


class LocalStorage:
    """Stores objects as files under a directory.

    Writes are atomic: content goes to a temporary file in the same directory and is then
    renamed into place. Without that, a process killed mid-write leaves a truncated file
    that reads back as a valid-but-wrong document — a failure mode students meet
    deliberately in Lab 1 and would otherwise meet accidentally forever.
    """

    def __init__(self, root: str) -> None:
        self.root = os.path.abspath(root)
        try:
            os.makedirs(self.root, exist_ok=True)
        except OSError as exc:
            raise StorageError(
                f"Cannot create the storage directory {self.root!r}: {exc}. "
                f"Check DOCAPP_DATA_DIR and that you can write there."
            ) from exc

    def _path(self, key: str) -> str:
        safe = _validate_key(key)
        path = os.path.join(self.root, safe)
        # Belt and braces: even after key validation, confirm the resolved path is inside
        # the root. Cheap, and the failure it prevents is severe.
        if os.path.commonpath([os.path.abspath(path), self.root]) != self.root:
            raise StorageError(f"Storage key {key!r} resolves outside the storage root.")
        return path

    def put(self, key: str, data: bytes) -> None:
        path = self._path(key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, path)  # atomic on POSIX and on Windows for same-volume renames
        except OSError as exc:
            _quietly_remove(tmp)
            raise StorageError(f"Could not write {key!r}: {exc}") from exc

    def get(self, key: str) -> bytes:
        path = self._path(key)
        try:
            with open(path, "rb") as fh:
                return fh.read()
        except FileNotFoundError:
            raise NotFound(f"No stored object with key {key!r}.") from None
        except OSError as exc:
            raise StorageError(f"Could not read {key!r}: {exc}") from exc

    def delete(self, key: str) -> None:
        """Deleting something that is not there is not an error.

        Making delete idempotent means a retried cleanup succeeds instead of failing on
        its second attempt — which matters a great deal once Lab 5 introduces retries.
        """
        path = self._path(key)
        try:
            os.remove(path)
        except FileNotFoundError:
            return
        except OSError as exc:
            raise StorageError(f"Could not delete {key!r}: {exc}") from exc

    def exists(self, key: str) -> bool:
        return os.path.isfile(self._path(key))


def _quietly_remove(path: str) -> None:
    try:
        os.remove(path)
    except OSError:
        pass


def build_storage(backend: str, data_dir: str) -> Storage:
    """Factory. Lab 3 adds a branch here; nothing else in the application changes."""
    if backend == "local":
        return LocalStorage(os.path.join(data_dir, "documents"))
    raise StorageError(
        f"Unknown storage backend {backend!r}. This build supports: local. "
        f"(Lab 3 adds a Cloud Storage backend.)"
    )
