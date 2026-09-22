"""Configuration, read once from the environment at startup.

Everything the application needs to know about its surroundings arrives through
environment variables. Nothing is read from a config file on disk, and nothing is
hard-coded to a particular machine.

That is not ceremony. In Lab 4 this same code runs in a container on managed execution,
where there is no config file to edit and no shell to edit it from — the only thing the
platform hands you is the environment. Writing it this way from week 2 means the
application does not change when it moves.

Errors here are deliberately loud and specific. A student who mistypes a value should get
a sentence telling them what to fix, not a traceback thirty frames deep.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Bounds exist so that a typo cannot turn a lab exercise into an expensive or
# hung experiment. Every one of these has been chosen to keep a student inside
# the free tier and inside the lab's time budget.
MAX_DOCUMENT_BYTES_LIMIT = 1_048_576  # 1 MiB. Bigger documents teach nothing extra.
MAX_PROCESSING_DELAY_MS = 5_000       # 5 s. Enough to see queuing, short enough to wait.


class ConfigError(RuntimeError):
    """Raised when the environment is configured in a way that cannot work.

    Carries a message written for the person who has to fix it.
    """


def _env_str(name: str, default: str) -> str:
    value = os.environ.get(name, default).strip()
    if not value:
        raise ConfigError(
            f"{name} is set but empty. Either give it a value or unset it to use the "
            f"default ({default!r})."
        )
    return value


def _env_int(name: str, default: int, *, minimum: int, maximum: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        raise ConfigError(
            f"{name} must be a whole number, but it is {raw!r}. "
            f"Example: {name}={default}"
        ) from None
    if not minimum <= value <= maximum:
        raise ConfigError(
            f"{name} must be between {minimum} and {maximum}, but it is {value}. "
            f"This bound exists so a mistyped value cannot run up a bill or hang a lab."
        )
    return value


def _env_choice(name: str, default: str, allowed: tuple[str, ...]) -> str:
    value = _env_str(name, default).lower()
    if value not in allowed:
        raise ConfigError(
            f"{name}={value!r} is not a backend this build knows about. "
            f"Choose one of: {', '.join(allowed)}."
        )
    return value


@dataclass(frozen=True)
class Config:
    """Resolved configuration. Immutable once built, so nothing can drift at runtime."""

    host: str
    port: int
    storage_backend: str
    jobstore_backend: str
    queue_backend: str
    data_dir: str
    bucket: str
    project_id: str
    max_document_bytes: int
    processing_delay_ms: int
    log_level: str
    instance_id: str

    @classmethod
    def from_env(cls) -> "Config":
        """Build a Config from os.environ, or raise ConfigError with actionable advice."""
        return cls(
            # 127.0.0.1 is the safe local default: it is not reachable from the network.
            # Lab 2 changes it to 0.0.0.0 and asks the student to explain why that is
            # both necessary and a thing to be careful about.
            host=_env_str("DOCAPP_HOST", "127.0.0.1"),
            # Managed execution platforms tell a container which port to listen on via
            # $PORT. Honouring it now means Lab 4 needs no code change.
            port=_env_int("PORT", 8080, minimum=1, maximum=65535),
            storage_backend=_env_choice("DOCAPP_STORAGE", "local", ("local", "gcs")),
            jobstore_backend=_env_choice("DOCAPP_JOBSTORE", "memory", ("memory", "file", "firestore")),
            queue_backend=_env_choice("DOCAPP_QUEUE", "inline", ("inline",)),
            data_dir=_env_str("DOCAPP_DATA_DIR", "./data"),
            # Only needed by the cloud backends. Empty is fine on the local path, and each
            # backend raises its own actionable error if it is missing when required.
            bucket=os.environ.get("DOCAPP_BUCKET", "").strip(),
            project_id=os.environ.get("DOCAPP_PROJECT_ID", "").strip(),
            max_document_bytes=_env_int(
                "DOCAPP_MAX_DOCUMENT_BYTES", 65_536,
                minimum=1, maximum=MAX_DOCUMENT_BYTES_LIMIT,
            ),
            # Real document processing is slow. Simulating that with a bounded, explicit
            # delay is honest and controllable; pretending processing is instant would
            # make Labs 4 and 5 measure nothing.
            processing_delay_ms=_env_int(
                "DOCAPP_PROCESSING_DELAY_MS", 250,
                minimum=0, maximum=MAX_PROCESSING_DELAY_MS,
            ),
            log_level=_env_choice("DOCAPP_LOG_LEVEL", "info", ("debug", "info", "warning", "error")),
            # Which process served this request. Meaningless locally, essential in Lab 4
            # when several instances exist and you need to know whether you hit a new one.
            instance_id=_env_str("DOCAPP_INSTANCE_ID", _default_instance_id()),
        )

    def describe(self) -> dict[str, object]:
        """A safe-to-log summary. No secrets live in this config, and none ever should."""
        return {
            "host": self.host,
            "port": self.port,
            "storage": self.storage_backend,
            "jobstore": self.jobstore_backend,
            "queue": self.queue_backend,
            "data_dir": self.data_dir,
            "bucket": self.bucket,
            "project_id": self.project_id,
            "max_document_bytes": self.max_document_bytes,
            "processing_delay_ms": self.processing_delay_ms,
            "instance_id": self.instance_id,
        }


def _default_instance_id() -> str:
    import socket
    import uuid

    # Hostname alone is not enough: two processes on one machine would share it.
    return f"{socket.gethostname()}-{uuid.uuid4().hex[:8]}"
