#!/usr/bin/env python3
"""Count how many instances of the service answered a burst of requests.

    python3 tools/instances.py --url "$SERVICE_URL" --requests 40 --concurrency 20

Every response from ``/healthz`` carries the ``instance_id`` of the process that produced
it. Locally that is one process and the answer is boring. On managed execution it is not:
send twenty requests at once to a service configured to handle one request per instance and
the platform has to produce instances to absorb them.

This tool makes that visible without a metrics console, which matters for two reasons. The
console is a product; the reasoning is not. And a number you obtained yourself, with a tool
whose whole implementation you can read, is evidence you can defend.

Standard library only, and bounded, for the same reason as ``measure.py``: an unbounded
request generator pointed at a metered service is how a free tier becomes a bill.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter

# Deliberately smaller caps than measure.py. This tool answers "how many", not "how fast",
# and "how many" is answered by tens of requests, not thousands.
MAX_REQUESTS = 500
MAX_CONCURRENCY = 50
MAX_DURATION_S = 120

# One header parser for both tools, so a credential is handled identically by each and
# neither ever prints one back. See measure.parse_headers.
from measure import parse_headers  # noqa: E402  (same directory, deliberate)


def probe(base: str, path: str, timeout: float,
          extra_headers: dict[str, str]) -> tuple[str, int]:
    """Return ``(instance_id_or_error_label, status)`` for one request.

    The id is taken from the ``X-Instance-Id`` response header, which every reply carries,
    and only falls back to the JSON body. That is why ``--path`` may point at any endpoint
    rather than only at the two that happen to name the instance in their payload.
    """
    req = urllib.request.Request(base + path, method="GET")
    for name, value in extra_headers.items():
        req.add_header(name, value)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            status = resp.status
            instance = resp.headers.get("X-Instance-Id")
        if not instance:
            try:
                instance = json.loads(raw.decode()).get("instance_id")
            except (ValueError, UnicodeDecodeError):
                instance = None
        if not isinstance(instance, str) or not instance:
            return "<no instance id in response>", status
        return instance, status
    except urllib.error.HTTPError as exc:
        exc.read()
        return f"<HTTP {exc.code}>", exc.code
    except Exception as exc:  # noqa: BLE001 - a failed probe is data, not a crash
        return f"<{type(exc).__name__}>", 0


def burst(base: str, path: str, total: int, concurrency: int, timeout: float,
          extra_headers: dict[str, str]) -> list[tuple[str, int]]:
    results: list[tuple[str, int]] = []
    lock = threading.Lock()
    sent = {"n": 0}
    deadline = time.monotonic() + MAX_DURATION_S

    def worker() -> None:
        while True:
            with lock:
                if sent["n"] >= total or time.monotonic() > deadline:
                    return
                sent["n"] += 1
            outcome = probe(base, path, timeout, extra_headers)
            with lock:
                results.append(outcome)

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(concurrency)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=MAX_DURATION_S + 10)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
How to read the result, and what it does not tell you
-----------------------------------------------------
  * The count is a LOWER BOUND on the instances that existed. An instance that served no
    request in this burst is invisible here, and so is one that started after it.
  * Distinct ids are not the same as "instances running now". Some may already be shutting
    down by the time you read the table.
  * Concurrency on the client is not concurrency at the server. If your own machine cannot
    keep 20 requests genuinely in flight, the service never sees 20 at once and has no
    reason to scale. When the numbers surprise you, suspect the client first.
  * Running this against a scaled-to-zero service measures a cold start as well as a fan
    out, and the two are tangled together in the first few responses.
""")
    parser.add_argument("--url", default="http://127.0.0.1:8080", help="base URL of the service")
    parser.add_argument("--path", default="/healthz",
                        help="endpoint to probe; must return instance_id (default /healthz)")
    parser.add_argument("--requests", type=int, default=40, help=f"total probes (max {MAX_REQUESTS})")
    parser.add_argument("--concurrency", type=int, default=20,
                        help=f"probes in flight (max {MAX_CONCURRENCY})")
    parser.add_argument("--timeout", type=float, default=30.0, help="per-request timeout in seconds")
    parser.add_argument("--header", action="append", default=[], metavar="NAME: VALUE",
                        help="extra request header; repeatable, same as measure.py")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = parser.parse_args(argv)

    if not 1 <= args.requests <= MAX_REQUESTS:
        parser.error(f"--requests must be between 1 and {MAX_REQUESTS}.")
    if not 1 <= args.concurrency <= MAX_CONCURRENCY:
        parser.error(f"--concurrency must be between 1 and {MAX_CONCURRENCY}.")

    try:
        extra_headers = parse_headers(args.header)
    except ValueError as exc:
        parser.error(str(exc))

    base = args.url.rstrip("/")
    started = time.perf_counter()
    outcomes = burst(base, args.path, args.requests, args.concurrency,
                     args.timeout, extra_headers)
    wall_s = time.perf_counter() - started

    counts = Counter(instance for instance, _ in outcomes)
    real = {k: v for k, v in counts.items() if not k.startswith("<")}
    failed = {k: v for k, v in counts.items() if k.startswith("<")}

    report = {
        "url": base,
        "path": args.path,
        "requests": args.requests,
        "concurrency": args.concurrency,
        "wall_seconds": round(wall_s, 3),
        "distinct_instances": len(real),
        "responses_per_instance": dict(sorted(real.items(), key=lambda kv: -kv[1])),
        "failures": failed,
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0 if real else 1

    print(f"\n  {base}{args.path}  requests={args.requests}  concurrency={args.concurrency}")
    print(f"  {'-' * 56}")
    print(f"  wall time            {report['wall_seconds']} s")
    print(f"  distinct instances   {report['distinct_instances']}")
    for instance, count in report["responses_per_instance"].items():
        print(f"    {instance:<40} {count}")
    if failed:
        print(f"  failures             {failed}")
    print(f"  measured at          {report['measured_at']}")
    print("\n  A lower bound, not a census. Read --help before concluding anything.\n")
    return 0 if real else 1


if __name__ == "__main__":
    raise SystemExit(main())
