"""End-to-end over a real socket.

A real HTTP server on a real (ephemeral) port, driven with ``urllib`` from the standard
library. Slower than calling ``dispatch`` directly, and worth it: status codes, headers and
body parsing are exactly the surface students interact with in every lab, and they are
where mistakes actually happen.
"""

from __future__ import annotations

import json
import threading
from urllib import error, request

import pytest

from conftest import SAMPLE, make_config
from docapp.app import make_server
from docapp.wiring import build_application


@pytest.fixture
def server(tmp_path):
    config = make_config(tmp_path)
    app = build_application(config)
    httpd = make_server(config, app)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)


def call(base, method, path, body=None, headers=None):
    """Return (status, parsed_json, response_headers). Never raises on 4xx/5xx."""
    data = body if isinstance(body, bytes) else (json.dumps(body).encode() if body else None)
    req = request.Request(base + path, data=data, method=method)
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode()), dict(resp.headers)
    except error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode()), dict(exc.headers)


def test_health_is_reachable(server):
    status, body, _ = call(server, "GET", "/healthz")
    assert status == 200
    assert body["status"] == "ok"


def test_full_document_and_job_flow(server):
    status, doc, _ = call(server, "POST", "/documents", SAMPLE,
                          {"X-Document-Name": "notes.txt", "Content-Type": "text/plain"})
    assert status == 201

    status, job, _ = call(server, "POST", "/jobs",
                          {"document_id": doc["id"], "operation": "wordcount"})
    assert status == 201
    assert job["status"] == "succeeded"
    assert job["result"]["words"] == 16

    status, fetched, _ = call(server, "GET", f"/jobs/{job['id']}")
    assert status == 200
    assert fetched["id"] == job["id"]


def test_idempotent_submission_returns_200_not_201(server):
    """The status code is the signal that a retry did nothing. That is the contract."""
    _, doc, _ = call(server, "POST", "/documents", SAMPLE, {"X-Document-Name": "n.txt"})
    payload = {"document_id": doc["id"], "operation": "checksum"}

    first_status, first, _ = call(server, "POST", "/jobs", payload,
                                  {"Idempotency-Key": "abc-123"})
    second_status, second, _ = call(server, "POST", "/jobs", payload,
                                    {"Idempotency-Key": "abc-123"})

    assert first_status == 201 and first["deduplicated"] is False
    assert second_status == 200 and second["deduplicated"] is True
    assert first["id"] == second["id"]


def test_unknown_route_is_404_and_wrong_method_is_405(server):
    status, body, _ = call(server, "GET", "/nope")
    assert status == 404
    status, body, _ = call(server, "GET", "/documents")   # only POST is defined
    assert status == 405
    assert "not allowed" in body["error"]


def test_bad_json_gives_400_with_an_explanation(server):
    status, body, _ = call(server, "POST", "/jobs", b"{not json",
                           {"Content-Type": "application/json"})
    assert status == 400
    assert "valid JSON" in body["error"]


def test_missing_document_id_gives_400(server):
    status, body, _ = call(server, "POST", "/jobs", {"operation": "wordcount"})
    assert status == 400
    assert "document_id" in body["error"]


def test_unknown_document_gives_404(server):
    status, _, _ = call(server, "GET", "/documents/doc_nope")
    assert status == 404


def test_every_response_carries_request_and_instance_ids(server):
    """Both headers are what make Lab 1's request tracing and Lab 4's instance
    identification possible. Losing either would be silent, so it is tested."""
    _, _, headers = call(server, "GET", "/healthz")
    assert headers.get("X-Request-Id")
    assert headers.get("X-Instance-Id") == "test-instance"


def test_supplied_request_id_is_echoed_back(server):
    _, _, headers = call(server, "GET", "/healthz", None, {"X-Request-Id": "trace-me"})
    assert headers["X-Request-Id"] == "trace-me"


def test_delete_document_is_idempotent_over_http(server):
    _, doc, _ = call(server, "POST", "/documents", SAMPLE, {"X-Document-Name": "n.txt"})
    assert call(server, "DELETE", f"/documents/{doc['id']}")[0] == 200
    assert call(server, "DELETE", f"/documents/{doc['id']}")[0] == 200


def test_concurrent_requests_are_all_served(server):
    """The server is threaded; counters and the job store are touched concurrently.

    Ten simultaneous submissions must produce ten jobs — no lost updates, no crash. This is
    the property that Lab 4's load experiment depends on.
    """
    _, doc, _ = call(server, "POST", "/documents", SAMPLE, {"X-Document-Name": "n.txt"})
    results: list[int] = []
    lock = threading.Lock()

    def submit(i: int) -> None:
        status, _, _ = call(server, "POST", "/jobs",
                            {"document_id": doc["id"], "operation": "checksum"})
        with lock:
            results.append(status)

    threads = [threading.Thread(target=submit, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=15)

    assert results == [201] * 10
    _, stats, _ = call(server, "GET", "/stats")
    assert stats["jobs_created"] == 10
    assert stats["jobs_in_store"] == 10
