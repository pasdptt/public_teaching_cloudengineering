"""MemoryJobStore, held to the shared backend contract.

The same contract applies to the FileJobStore you write in Lab 1 and to the Firestore
backend in Lab 3. If your implementation passes it, swapping backends changes where job
records live and nothing else — which is the entire point of the Protocol.
"""

from __future__ import annotations

import threading

import pytest

from contracts import JobStoreContract, a_job
from docapp.jobstore import MemoryJobStore


class TestMemoryJobStore(JobStoreContract):
    @pytest.fixture
    def store(self):
        return MemoryJobStore()

    # ---- specific to an in-process store ----

    def test_concurrent_writes_do_not_lose_jobs(self, store):
        """The HTTP server is threaded, so this happens for real."""
        errors: list[BaseException] = []

        def write_one() -> None:
            try:
                store.put(a_job())
            except BaseException as exc:  # noqa: BLE001
                errors.append(exc)

        threads = [threading.Thread(target=write_one) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=20)

        assert errors == []
        assert store.count() == 20

    def test_state_does_not_outlive_the_object(self):
        """The Lab 1 lesson, stated as a property.

        A new MemoryJobStore knows nothing about the previous one. That is not a defect —
        it is what makes it a *memory* store, and what Lab 1 asks you to fix.
        """
        first = MemoryJobStore()
        first.put(a_job())
        assert MemoryJobStore().count() == 0
