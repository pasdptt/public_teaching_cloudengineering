"""LocalStorage, held to the shared backend contract, plus its own specifics.

The contract in ``contracts.py`` is the same one Lab 3's Cloud Storage backend must satisfy.
The extra tests below are about *this* implementation — atomic writes and temp-file hygiene
are properties of a filesystem backend, not of storage in general.
"""

from __future__ import annotations

import os

import pytest

from contracts import StorageContract
from docapp.storage import LocalStorage


class TestLocalStorage(StorageContract):
    @pytest.fixture
    def storage(self, tmp_path):
        return LocalStorage(str(tmp_path / "objects"))

    # ---- filesystem-specific, not part of the shared contract ----

    def test_put_leaves_no_temporary_files_behind(self, tmp_path):
        """A backend that leaks temp files fills a disk.

        On the 30 GB free persistent-disk allowance that is a real outcome, not a
        theoretical one.
        """
        root = tmp_path / "objects"
        store = LocalStorage(str(root))
        for i in range(20):
            store.put(f"file-{i}", b"x" * 100)
        assert [p for p in os.listdir(root) if p.endswith(".tmp")] == []

    def test_nested_keys_create_directories(self, tmp_path):
        store = LocalStorage(str(tmp_path / "objects"))
        store.put("a/b/c/d.txt", b"deep")
        assert store.get("a/b/c/d.txt") == b"deep"
