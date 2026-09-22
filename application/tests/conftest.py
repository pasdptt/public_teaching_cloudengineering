"""Shared fixtures.

Every test builds the application through ``build_application`` — the same function the
server uses — so the tests exercise the real object graph rather than a convenient
imitation of it.
"""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docapp import logs  # noqa: E402
from docapp.config import Config  # noqa: E402
from docapp.wiring import build_application  # noqa: E402

logs.configure("error")  # keep test output readable; raise to "debug" when investigating


def make_config(tmp_path, **overrides) -> Config:
    """A Config with test-friendly defaults. Built directly, not from os.environ."""
    base = dict(
        host="127.0.0.1",
        port=0,                  # 0 = let the OS choose a free port
        storage_backend="local",
        jobstore_backend="memory",
        queue_backend="inline",
        queue_topic="",
        queue_workers=1,
        queue_duplicate_percent=0,
        queue_max_attempts=3,
        data_dir=str(tmp_path),
        bucket="",
        project_id="",
        max_document_bytes=65_536,
        processing_delay_ms=0,   # no artificial delay: tests should be fast and honest
        log_level="error",
        instance_id="test-instance",
    )
    base.update(overrides)
    return Config(**base)


@pytest.fixture
def config(tmp_path):
    return make_config(tmp_path)


@pytest.fixture
def app(config):
    return build_application(config)


@pytest.fixture
def service(app):
    return app.service


SAMPLE = b"The quick brown fox jumps over the lazy dog. The dog sleeps.\nThe fox does not.\n"
