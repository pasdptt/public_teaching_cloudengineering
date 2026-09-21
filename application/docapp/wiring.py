"""Assemble the application from configuration.

One function, used by the server entry point and by the tests, so that what the tests
exercise is what actually runs. A test that builds its own bespoke object graph is testing
the test.
"""

from __future__ import annotations

from .app import Application
from .config import Config
from .jobstore import build_jobstore
from .queue import build_queue
from .service import DocumentService
from .storage import build_storage


def build_application(config: Config) -> Application:
    storage = build_storage(config.storage_backend, config.data_dir)
    jobs = build_jobstore(config.jobstore_backend, config.data_dir)
    service = DocumentService(config, storage, jobs)
    # The queue calls back into the service, and the service submits to the queue. The knot
    # is tied here rather than inside either of them, so neither has to know how the other
    # was built.
    service.attach_queue(build_queue(config.queue_backend, service.run_job))
    return Application(service)
