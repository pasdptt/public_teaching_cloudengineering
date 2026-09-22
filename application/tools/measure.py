#!/usr/bin/env python3
"""A deliberately small load measurement tool.

    python3 tools/measure.py --url http://127.0.0.1:8080 --requests 30 --concurrency 5

Used unchanged in Lab 1 against your laptop, and in Lab 4 against a managed cloud service.
Using the same instrument for both is the point: when the numbers differ, the difference is
the system, not the tool.

It is not a benchmarking suite, and it does not pretend to be. It sends N requests with C
in flight at a time, records how long each took, and reports percentiles. Read the
"Honest limitations" section at the bottom of `--help` before you draw a conclusion from
its output — the limitations are part of what you are being taught.

Standard library only. Bounded by default, because an unbounded load generator pointed at a
cloud service is how a free tier becomes a bill.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from typing import Any

# Hard caps. A typo in --requests should not be able to run up a bill or hang a lab.
MAX_REQUESTS = 5_000
MAX_CONCURRENCY = 100
MAX_DURATION_S = 300


class Result:
    __slots__ = ("latency_ms", "status", "error")

    def __init__(self, latency_ms: float, status: int, error: str | None) -> None:
        self.latency_ms = latency_ms
        self.status = status
        self.error = error


def one_request(base: str, document_id: str, operation: str, timeout: float,
                extra_headers: dict[str, str] | None = None) -> Result:
    payload = json.dumps({"document_id": document_id, "operation": operation}).encode()
    req = urllib.request.Request(base + "/jobs", data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    for name, value in (extra_headers or {}).items():
        req.add_header(name, value)
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()
            status = resp.status
        return Result((time.perf_counter() - started) * 1000, status, None)
    except urllib.error.HTTPError as exc:
        exc.read()
        return Result((time.perf_counter() - started) * 1000, exc.code, f"HTTP {exc.code}")
    except Exception as exc:  # noqa: BLE001 - a failed request is data, not a crash
        return Result((time.perf_counter() - started) * 1000, 0, type(exc).__name__)


def upload_document(base: str, path: str | None,
                    extra_headers: dict[str, str] | None = None) -> str:
    if path:
        with open(path, "rb") as fh:
            data = fh.read()
    else:
        data = b"Measurement document. " * 40
    req = urllib.request.Request(base + "/documents", data=data, method="POST")
    req.add_header("Content-Type", "text/plain")
    req.add_header("X-Document-Name", "measure.txt")
    for name, value in (extra_headers or {}).items():
        req.add_header(name, value)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())["id"]


def run(base: str, document_id: str, operation: str, total: int, concurrency: int,
        timeout: float, deadline: float,
        extra_headers: dict[str, str] | None = None) -> list[Result]:
    results: list[Result] = []
    lock = threading.Lock()
    counter = {"sent": 0}

    def worker() -> None:
        while True:
            with lock:
                if counter["sent"] >= total or time.monotonic() > deadline:
                    return
                counter["sent"] += 1
            result = one_request(base, document_id, operation, timeout, extra_headers)
            with lock:
                results.append(result)

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(concurrency)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=MAX_DURATION_S + 10)
    return results


def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile. Simple, and honest about being simple.

    With 30 samples, p95 is the 29th value. Saying "p95" about 30 samples is a much weaker
    claim than it sounds, which is exactly why the report prints the sample count next to it.
    """
    if not values:
        return float("nan")
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round(p / 100 * len(ordered) + 0.5)) - 1))
    return ordered[index]


def parse_headers(raw: list[str]) -> dict[str, str]:
    """Turn ``["Name: value", ...]`` into a dict, or say precisely what was wrong.

    Values are never printed back by this tool. One of them is usually a bearer token, and
    a load generator that echoes credentials into a terminal — or into a lab submission —
    has created a problem bigger than the measurement it was taking.
    """
    headers: dict[str, str] = {}
    for item in raw:
        name, sep, value = item.partition(":")
        if not sep or not name.strip() or not value.strip():
            raise ValueError(
                f"--header must look like 'Name: value', but got {item!r}. "
                f"Example: --header 'Authorization: Bearer <token>'"
            )
        headers[name.strip()] = value.strip()
    return headers


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Honest limitations — read these before concluding anything
----------------------------------------------------------
  * The client and the server may be on the same machine. If they are, they compete for
    the same CPU, and what you measure includes your own load generator.
  * One run is one sample of a noisy system. Run it three times. If the three disagree,
    that disagreement is your result.
  * Network latency is included and not separated out. Measuring a service in Iowa from
    Bangkok includes roughly the round-trip time on every single request.
  * Percentiles from small samples are weak. p95 of 30 requests is "the second-slowest
    one". The report prints n for this reason.
  * This tool measures job *creation*. Whether the work is finished when the response
    arrives depends on the queue backend — and noticing that difference is the whole point
    of Lab 5.

Measuring a service that requires an identity
---------------------------------------------
  Lab 4 deploys a service that refuses unauthenticated callers. Pass the credential as a
  header, and keep it out of your shell history and out of your submission:

    python3 tools/measure.py --url "$SERVICE_URL" \
      --header "Authorization: Bearer $(gcloud auth print-identity-token)"

  The header is sent on every request, so a token that expires mid-run shows up as a wall
  of HTTP 401s rather than as slow requests. That is a real failure mode, and reading it
  correctly off this report is part of the exercise.
""")
    parser.add_argument("--url", default="http://127.0.0.1:8080", help="base URL of the service")
    parser.add_argument("--requests", type=int, default=30, help=f"total requests (max {MAX_REQUESTS})")
    parser.add_argument("--concurrency", type=int, default=1, help=f"requests in flight (max {MAX_CONCURRENCY})")
    parser.add_argument("--operation", default="wordcount", choices=("wordcount", "checksum", "extract"))
    parser.add_argument("--document", help="path to a document to upload first (default: built-in)")
    parser.add_argument("--timeout", type=float, default=30.0, help="per-request timeout in seconds")
    parser.add_argument("--header", action="append", default=[], metavar="NAME: VALUE",
                        help="extra request header; repeatable. Used in Lab 4 to carry an "
                             "identity token to a service that requires one.")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = parser.parse_args(argv)

    if not 1 <= args.requests <= MAX_REQUESTS:
        parser.error(f"--requests must be between 1 and {MAX_REQUESTS}. "
                     f"The cap exists so a typo cannot run up a bill.")
    if not 1 <= args.concurrency <= MAX_CONCURRENCY:
        parser.error(f"--concurrency must be between 1 and {MAX_CONCURRENCY}.")

    try:
        extra_headers = parse_headers(args.header)
    except ValueError as exc:
        parser.error(str(exc))

    base = args.url.rstrip("/")
    try:
        document_id = upload_document(base, args.document, extra_headers)
    except Exception as exc:  # noqa: BLE001
        print(f"Could not upload the test document to {base}: {exc}\n"
              f"Is the service running, and is --url right?", file=sys.stderr)
        return 2

    wall_start = time.perf_counter()
    deadline = time.monotonic() + MAX_DURATION_S
    results = run(base, document_id, args.operation, args.requests,
                  args.concurrency, args.timeout, deadline, extra_headers)
    wall_s = time.perf_counter() - wall_start

    ok = [r for r in results if 200 <= r.status < 300]
    latencies = [r.latency_ms for r in ok]
    errors: dict[str, int] = {}
    for r in results:
        if r.error:
            errors[r.error] = errors.get(r.error, 0) + 1

    report: dict[str, Any] = {
        "url": base,
        "operation": args.operation,
        "requested": args.requests,
        "completed": len(results),
        "successful": len(ok),
        "concurrency": args.concurrency,
        "wall_seconds": round(wall_s, 3),
        "throughput_rps": round(len(ok) / wall_s, 2) if wall_s > 0 else None,
        "latency_ms": {
            "n": len(latencies),
            "min": round(min(latencies), 1) if latencies else None,
            "mean": round(statistics.fmean(latencies), 1) if latencies else None,
            "p50": round(percentile(latencies, 50), 1) if latencies else None,
            "p95": round(percentile(latencies, 95), 1) if latencies else None,
            "max": round(max(latencies), 1) if latencies else None,
        },
        "errors": errors,
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0 if ok else 1

    lat = report["latency_ms"]
    print(f"\n  {base}  operation={args.operation}  concurrency={args.concurrency}")
    print(f"  {'-' * 56}")
    print(f"  successful     {report['successful']} / {report['requested']}")
    print(f"  wall time      {report['wall_seconds']} s")
    print(f"  throughput     {report['throughput_rps']} req/s")
    print(f"  latency (ms)   min {lat['min']}   p50 {lat['p50']}   "
          f"p95 {lat['p95']}   max {lat['max']}   (n={lat['n']})")
    if errors:
        print(f"  errors         {errors}")
    print(f"  measured at    {report['measured_at']}")
    print(f"\n  Remember: one run is one sample. Run it three times before believing it.\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
