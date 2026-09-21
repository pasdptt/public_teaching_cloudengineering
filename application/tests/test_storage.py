"""Storage behaviour that the rest of the application relies on.

These are not tests of ``open()``. Each one pins down a property that a different storage
backend must also have, which is what makes the backends swappable in Lab 3.
"""

from __future__ import annotations

import os

import pytest

from docapp.storage import LocalStorage, NotFound, StorageError


def test_roundtrip(tmp_path):
    store = LocalStorage(str(tmp_path / "objects"))
    store.put("a/b.txt", b"hello")
    assert store.get("a/b.txt") == b"hello"
    assert store.exists("a/b.txt")


def test_missing_object_raises_notfound(tmp_path):
    store = LocalStorage(str(tmp_path / "objects"))
    with pytest.raises(NotFound):
        store.get("nope")
    assert store.exists("nope") is False


def test_delete_is_idempotent(tmp_path):
    """Deleting twice must succeed.

    This is the property that makes a retried cleanup safe. Lab 5 depends on it, and every
    teardown script in the course depends on it.
    """
    store = LocalStorage(str(tmp_path / "objects"))
    store.put("k", b"v")
    store.delete("k")
    store.delete("k")  # must not raise
    assert store.exists("k") is False


def test_put_overwrites(tmp_path):
    store = LocalStorage(str(tmp_path / "objects"))
    store.put("k", b"first")
    store.put("k", b"second")
    assert store.get("k") == b"second"


@pytest.mark.parametrize("key", ["../escape", "/absolute", "a/../../b", "", " padded"])
def test_rejects_keys_that_could_escape_the_root(tmp_path, key):
    """Path traversal is rejected before it reaches the filesystem."""
    store = LocalStorage(str(tmp_path / "objects"))
    with pytest.raises(StorageError):
        store.put(key, b"x")


def test_put_leaves_no_temporary_files_behind(tmp_path):
    """Atomic writes must clean up after themselves.

    If temp files accumulated, a long-running service would fill its disk — and on the
    free-tier 30 GB allowance that is a real outcome, not a theoretical one.
    """
    root = tmp_path / "objects"
    store = LocalStorage(str(root))
    for i in range(20):
        store.put(f"file-{i}", b"x" * 100)
    leftovers = [p for p in os.listdir(root) if p.endswith(".tmp")]
    assert leftovers == []
