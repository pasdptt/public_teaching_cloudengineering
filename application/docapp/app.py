"""The HTTP layer: routing, parsing, status codes. Nothing else.

Built on ``http.server`` from the standard library rather than a web framework. That is a
considered choice with three reasons behind it:

  * **Nothing to install.** With one instructor and no teaching assistant, every dependency
    is a support ticket waiting to happen in week 1.
  * **The mechanism is visible.** Week 2 teaches HTTP just-in-time. A student can read this
    file and see the method, the path, the headers and the status code, rather than a
    decorator that makes them disappear.
  * **A smaller container image.** In Lab 4 the image goes to Artifact Registry, whose free
    allowance is 0.5 GiB. An image with no pip install stays small, builds fast, and keeps
    the lab free.

It is not a production web server and the code says so where it matters. Knowing *why* it
is not is worth more than using one that hides the question.
"""

from __future__ import annotations

import json
import re
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Optional, Pattern
from urllib.parse import parse_qs, urlparse

from . import logs
from .config import Config
from .jobstore import JobNotFound
from .models import new_id
from .queue import QueueError
from .service import DocumentService, ValidationError
from .storage import NotFound as StorageNotFound
from .storage import StorageError

Route = tuple[str, Pattern[str], Callable[..., Any]]

# Requests larger than this are refused before being read into memory. Without a limit,
# a single large POST is a denial-of-service against a 1 GB free-tier VM.
ABSOLUTE_MAX_BODY = 2_097_152  # 2 MiB


class Application:
    """Routing table plus handlers. Holds no request state of its own.

    Statelessness is not an accident here. In Lab 4 several instances of this run at once
    and any of them may serve any request; anything cached in this object would be wrong on
    the other instances. Lab 1 asks students to find the one place state *does* live, and
    explain why it is not here.
    """

    def __init__(self, service: DocumentService) -> None:
        self.service = service
        self.routes: list[Route] = [
            ("GET",    re.compile(r"^/healthz$"),                    self.health),
            ("GET",    re.compile(r"^/stats$"),                      self.stats),
            ("POST",   re.compile(r"^/documents$"),                  self.create_document),
            ("GET",    re.compile(r"^/documents/(?P<doc_id>[\w\-]+)$"), self.get_document),
            ("DELETE", re.compile(r"^/documents/(?P<doc_id>[\w\-]+)$"), self.delete_document),
            ("POST",   re.compile(r"^/jobs$"),                       self.create_job),
            ("GET",    re.compile(r"^/jobs$"),                       self.list_jobs),
            ("GET",    re.compile(r"^/jobs/(?P<job_id>[\w\-]+)$"),   self.get_job),
            ("POST",   re.compile(r"^/tasks/process$"),              self.process_push),
        ]

    def dispatch(self, method: str, path: str, query: dict[str, list[str]],
                 body: bytes, headers: dict[str, str]) -> tuple[int, dict[str, Any]]:
        """Find a route for (method, path), or explain which part was wrong.

        Every route whose *path* matches is considered before giving up, not just the
        first. Checking the first one only would mean that ``DELETE /documents/x`` got a
        405 purely because a ``GET`` route for the same path was declared earlier -- a bug
        that depends on the order of a list, which is the worst kind.
        """
        allowed: set[str] = set()
        for route_method, pattern, handler in self.routes:
            match = pattern.match(path)
            if not match:
                continue
            if route_method == method:
                return handler(query=query, body=body, headers=headers, **match.groupdict())
            allowed.add(route_method)

        if allowed:
            # The path exists but the method does not. 405 rather than 404 -- a small
            # courtesy that saves a student ten minutes of wondering why their URL is
            # wrong when it is their verb that is.
            return 405, {
                "error": f"{method} is not allowed on {path}.",
                "allowed": sorted(allowed),
            }
        return 404, {"error": f"No route for {method} {path}."}

    # ------------------------------------------------------------------ handlers

    def health(self, **_: Any) -> tuple[int, dict[str, Any]]:
        """Liveness only. Deliberately does not touch storage or the job store.

        A health check that depends on every downstream service will report the whole
        application dead when one dependency is briefly slow, and a platform that believes
        it will then restart a perfectly healthy instance. Week 11 revisits this.
        """
        return 200, {"status": "ok", "instance_id": self.service.config.instance_id}

    def stats(self, **_: Any) -> tuple[int, dict[str, Any]]:
        return 200, self.service.stats()

    def create_document(self, body: bytes, headers: dict[str, str],
                        **_: Any) -> tuple[int, dict[str, Any]]:
        name = headers.get("x-document-name") or "untitled.txt"
        content_type = headers.get("content-type", "text/plain").split(";")[0].strip()
        doc = self.service.create_document(name=name, data=body, content_type=content_type)
        return 201, doc.to_dict()

    def get_document(self, doc_id: str, **_: Any) -> tuple[int, dict[str, Any]]:
        try:
            return 200, self.service.get_document(doc_id).to_dict()
        except StorageNotFound:
            return 404, {"error": f"No document with id {doc_id!r}."}

    def delete_document(self, doc_id: str, **_: Any) -> tuple[int, dict[str, Any]]:
        self.service.delete_document(doc_id)
        # 200 with a body rather than 204, so that a student using curl without -v sees
        # that something happened. Deliberate teaching trade-off against strict REST.
        return 200, {"deleted": doc_id}

    def create_job(self, body: bytes, headers: dict[str, str],
                   **_: Any) -> tuple[int, dict[str, Any]]:
        payload = _parse_json_object(body)
        document_id = payload.get("document_id")
        operation = payload.get("operation", "wordcount")
        if not isinstance(document_id, str) or not document_id:
            raise ValidationError("Body must be a JSON object with a 'document_id' string.")
        if not isinstance(operation, str):
            raise ValidationError("'operation' must be a string.")

        # The header is the conventional place for this. Accepting it in the body too is a
        # convenience for students driving the API from a shell.
        key = headers.get("idempotency-key") or payload.get("idempotency_key")
        if key is not None and not isinstance(key, str):
            raise ValidationError("'idempotency_key' must be a string.")

        job, created = self.service.create_job(document_id, operation, idempotency_key=key)
        body_out = job.to_dict()
        body_out["deduplicated"] = not created
        # 201 for a new job, 200 for one that already existed. The status code alone tells a
        # client whether its retry did anything -- which is the point of idempotency.
        return (201 if created else 200), body_out

    def get_job(self, job_id: str, **_: Any) -> tuple[int, dict[str, Any]]:
        try:
            return 200, self.service.get_job(job_id).to_dict()
        except JobNotFound:
            return 404, {"error": f"No job with id {job_id!r}."}

    def process_push(self, body: bytes, **_: Any) -> tuple[int, dict[str, Any]]:
        """The consumer end of an external queue: the broker POSTs work to us.

        Supplied rather than set as an exercise, because the interesting decisions here are
        not about HTTP -- they are about status codes, and they are worth stating plainly:

        **200 means "do not send this again".** A broker that gets anything else will
        redeliver, which is exactly right for a failure it should retry and exactly wrong
        for one it should not. So:

          * a message we cannot decode gets **400**, and is not retried, because a
            malformed message will be just as malformed in thirty seconds;
          * a job that does not exist gets **200**, because the message has outlived its
            job record and redelivering it forever helps nobody;
          * a job that fails *processing* is recorded as failed and still gets **200** --
            the failure is durable in the job record, and the broker retrying would only
            fail it again;
          * anything unexpected gets **500**, and the broker retries. That is the one case
            where a retry might genuinely help.

        Lab 5 Part 4 asks you to argue with two of these.
        """
        from .pubsub_queue import decode_push_envelope

        try:
            job_id = decode_push_envelope(body)
        except QueueError as exc:
            logs.warning("undecodable push message, acknowledging", error=str(exc))
            return 400, {"error": str(exc)}

        try:
            job = self.service.run_job(job_id)
        except JobNotFound:
            # Already logged by the service. Acknowledge: there is nothing to retry toward.
            return 200, {"status": "dropped", "job_id": job_id,
                         "reason": "no such job"}
        return 200, {"status": job.status, "job_id": job.id,
                     "attempts": job.attempts,
                     "instance_id": self.service.config.instance_id}

    def list_jobs(self, query: dict[str, list[str]], **_: Any) -> tuple[int, dict[str, Any]]:
        raw = query.get("limit", ["50"])[0]
        try:
            limit = max(1, min(200, int(raw)))
        except ValueError:
            raise ValidationError(f"'limit' must be a whole number, not {raw!r}.")
        jobs = self.service.list_jobs(limit=limit)
        return 200, {"jobs": [j.to_dict() for j in jobs], "count": len(jobs)}


def _parse_json_object(body: bytes) -> dict[str, Any]:
    if not body:
        raise ValidationError("Request body is empty; a JSON object was expected.")
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Request body is not valid JSON: {exc}") from None
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object, not a list or scalar.")
    return payload


class Handler(BaseHTTPRequestHandler):
    """Adapts ``http.server`` to :class:`Application`. One instance per request."""

    protocol_version = "HTTP/1.1"  # required for keep-alive; needs Content-Length on every reply
    application: Application      # injected by serve()

    def log_message(self, fmt: str, *args: Any) -> None:
        """Silence the default stderr access log; we emit structured logs instead."""

    def _handle(self, method: str) -> None:
        # A request id is generated if the client did not supply one, and echoed back. This
        # is what makes "follow one request through the logs" possible, and it is the same
        # mechanism a real distributed trace uses, minus the tooling.
        request_id = self.headers.get("X-Request-Id") or new_id("req")
        logs.set_request_id(request_id)
        parsed = urlparse(self.path)
        started = _monotonic_ms()
        status = 500
        try:
            body = self._read_body()
            headers = {k.lower(): v for k, v in self.headers.items()}
            self.application.service.counters.request_count += 1
            status, payload = self.application.dispatch(
                method, parsed.path, parse_qs(parsed.query), body, headers
            )
        except ValidationError as exc:
            status, payload = 400, {"error": str(exc)}
        except _BodyTooLarge as exc:
            status, payload = 413, {"error": str(exc)}
        except (StorageError,) as exc:
            status, payload = 500, {"error": f"Storage failure: {exc}"}
        except Exception as exc:  # noqa: BLE001 - last resort; must not leak a traceback
            logs.error("unhandled error", error=str(exc), type=type(exc).__name__)
            status, payload = 500, {"error": "Internal error. Check the server logs."}
        finally:
            logs.info("request", method=method, path=parsed.path, status=status,
                      duration_ms=_monotonic_ms() - started)

        self._respond(status, payload, request_id)
        logs.set_request_id(None)

    def _read_body(self) -> bytes:
        length_raw = self.headers.get("Content-Length")
        if not length_raw:
            return b""
        try:
            length = int(length_raw)
        except ValueError:
            raise _BodyTooLarge("Content-Length is not a number.") from None
        if length > ABSOLUTE_MAX_BODY:
            # Refuse before reading. Reading it first to then reject it would be doing the
            # attacker's work for them.
            raise _BodyTooLarge(
                f"Request body of {length} bytes exceeds the {ABSOLUTE_MAX_BODY} byte limit."
            )
        return self.rfile.read(length) if length > 0 else b""

    def _respond(self, status: int, payload: dict[str, Any], request_id: str) -> None:
        data = json.dumps(payload, indent=2, default=str).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Request-Id", request_id)
            self.send_header("X-Instance-Id", self.application.service.config.instance_id)
            self.end_headers()
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            # The client gave up before we answered. Normal under load testing; not an error.
            logs.debug("client disconnected before response", status=status)

    def do_GET(self) -> None: self._handle("GET")
    def do_POST(self) -> None: self._handle("POST")
    def do_DELETE(self) -> None: self._handle("DELETE")


class _BodyTooLarge(Exception):
    pass


def _monotonic_ms() -> int:
    import time
    return int(time.monotonic() * 1000)


class _Server(ThreadingHTTPServer):
    """The stdlib server with one default corrected.

    ``socketserver`` listens with a backlog of 5: at most five connections may sit waiting
    to be accepted, and the sixth arrival is refused by the operating system before any
    Python code sees it. That is invisible at concurrency 4 and very visible at concurrency
    20, where it shows up as a scatter of connection errors that look like the application
    failing and are nothing of the sort.

    It matters here because Lab 4 compares this server under load against a managed
    platform, and a comparison is worthless if one side is capped by an accidental default
    nobody chose. 128 is not a tuned number; it is "larger than any concurrency this
    course's tools can generate", which is the honest justification for it.
    """

    request_queue_size = 128


def make_server(config: Config, application: Application) -> ThreadingHTTPServer:
    """Build the server without starting it, so tests can drive it on a random port."""
    handler = type("BoundHandler", (Handler,), {"application": application})
    server = _Server((config.host, config.port), handler)
    # Threads do not outlive the process. Under Ctrl-C a request in flight is abandoned
    # rather than blocking shutdown -- acceptable here, and a topic revisited in week 11
    # when graceful shutdown starts to matter.
    server.daemon_threads = True
    return server
