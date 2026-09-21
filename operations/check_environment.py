#!/usr/bin/env python3
"""Week 1 environment check.

Run this from the repository root:

    python3 operations/check_environment.py

It answers one question: can this machine do the work this course asks of it? It changes
nothing, installs nothing, and contacts no cloud service.

Every check prints PASS, WARN or FAIL, and every FAIL comes with the next thing to try.
Bring the output to the week 1 session if anything fails — a setup problem found in week 1
is a five-minute fix, and the same problem found in week 4 costs a lab.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

MIN_PYTHON = (3, 10)
results: list[tuple[str, str, str]] = []   # (status, check, detail)


def record(status: str, check: str, detail: str = "") -> None:
    results.append((status, check, detail))
    colour = {"PASS": "\033[32m", "WARN": "\033[33m", "FAIL": "\033[31m"}.get(status, "")
    reset = "\033[0m" if colour and sys.stdout.isatty() else ""
    if not sys.stdout.isatty():
        colour = ""
    print(f"  {colour}{status:<4}{reset}  {check}")
    if detail:
        for line in detail.splitlines():
            print(f"          {line}")


def section(title: str) -> None:
    print(f"\n{title}\n{'-' * len(title)}")


# --------------------------------------------------------------------- checks

def check_python() -> None:
    version = sys.version_info
    text = f"{version.major}.{version.minor}.{version.micro}"
    if version[:2] >= MIN_PYTHON:
        record("PASS", f"Python {text}")
    else:
        record("FAIL", f"Python {text} is too old",
               f"This course needs Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer.\n"
               f"macOS: install from python.org or `brew install python@3.12`.\n"
               f"Windows: install from python.org and tick 'Add python.exe to PATH'.")


def check_platform() -> None:
    record("PASS", f"{platform.system()} {platform.release()} on {platform.machine()}")
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        record("PASS", "Apple Silicon detected",
               "Lab 4 builds a container image. You will be told which architecture to\n"
               "target — building for the wrong one is the single most common Lab 4 error.")
    elif platform.system() == "Windows":
        record("WARN", "Windows detected",
               "Some lab commands assume a Unix-style shell. The setup guide gives you a\n"
               "WSL2 path; see operations/student-setup.md.")


def check_application_runs() -> None:
    """Start the real application on a spare port and talk to it. The decisive check."""
    app_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "application")
    if not os.path.isdir(app_dir):
        record("FAIL", "Cannot find the application directory",
               f"Expected it at {app_dir}.\n"
               f"Run this script from inside the course repository.")
        return

    port = _free_port()
    env = dict(os.environ, PORT=str(port), DOCAPP_DATA_DIR=os.path.join(app_dir, ".check-data"),
               DOCAPP_LOG_LEVEL="error", DOCAPP_PROCESSING_DELAY_MS="0")
    try:
        proc = subprocess.Popen([sys.executable, "-m", "docapp"], cwd=app_dir, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as exc:
        record("FAIL", "Could not start the application", str(exc))
        return

    try:
        base = f"http://127.0.0.1:{port}"
        if not _wait_for(base + "/healthz", timeout=15):
            out, err = proc.communicate(timeout=5)
            record("FAIL", "The application did not become healthy",
                   (err.decode(errors="replace").strip() or
                    out.decode(errors="replace").strip() or
                    "No output. Try `cd application && python3 -m docapp` to see the error.")[:800])
            return
        record("PASS", "Application starts and answers /healthz")

        doc_id = _post(base + "/documents", b"Two words here. And a few more words.",
                       {"X-Document-Name": "check.txt", "Content-Type": "text/plain"})["id"]
        record("PASS", "Can store a document")

        job = _post(base + "/jobs",
                    json.dumps({"document_id": doc_id, "operation": "wordcount"}).encode(),
                    {"Content-Type": "application/json"})
        if job.get("status") == "succeeded" and job.get("result", {}).get("words") == 8:
            record("PASS", "Can create and complete a job")
        else:
            record("FAIL", "A job did not complete as expected", json.dumps(job)[:400])
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(os.path.join(app_dir, ".check-data"), ignore_errors=True)


def check_tests() -> None:
    app_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "application")
    try:
        import pytest  # noqa: F401
    except ImportError:
        record("WARN", "pytest is not installed",
               "Not needed to run the application, but you will need it for Lab 1:\n"
               "  pip3 install -r application/requirements-dev.txt")
        return
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=app_dir,
                          capture_output=True, text=True)
    if proc.returncode == 0:
        record("PASS", "The application test suite passes",
               proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "")
    else:
        record("FAIL", "The application test suite does not pass",
               (proc.stdout or proc.stderr).strip()[-800:])


def check_container_runtime() -> None:
    """A container runtime is needed from Lab 1 onwards, but its absence is not fatal today."""
    for tool in ("docker", "podman", "nerdctl"):
        path = shutil.which(tool)
        if not path:
            continue
        try:
            proc = subprocess.run([tool, "info"], capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            record("WARN", f"{tool} is installed but did not respond", "Is the engine running?")
            return
        if proc.returncode == 0:
            record("PASS", f"Container runtime available: {tool}")
        else:
            record("WARN", f"{tool} is installed but not running",
                   "Start Docker Desktop / Podman Desktop and run this check again.")
        return
    record("WARN", "No container runtime found",
           "Needed from Lab 1. See operations/student-setup.md for which to install.\n"
           "This is a WARN rather than a FAIL: the application itself runs without one.")


def check_network() -> None:
    """Can this machine reach the internet at all? Nothing cloud-specific is contacted."""
    try:
        with socket.create_connection(("pypi.org", 443), timeout=8):
            record("PASS", "Outbound HTTPS works")
    except OSError as exc:
        record("WARN", "Could not open an outbound HTTPS connection", f"{exc}\n"
               "A restrictive network or VPN can cause this. Retry off the campus network.")


def check_disk_space() -> None:
    usage = shutil.disk_usage(os.path.abspath("."))
    free_gb = usage.free / (1024 ** 3)
    if free_gb >= 10:
        record("PASS", f"Free disk space: {free_gb:.1f} GB")
    elif free_gb >= 4:
        record("WARN", f"Free disk space: {free_gb:.1f} GB",
               "Container images in Lab 4 will want a few GB. Tight but workable.")
    else:
        record("FAIL", f"Free disk space: {free_gb:.1f} GB",
               "Free up space before Lab 4; container images need several GB.")


# -------------------------------------------------------------------- helpers

def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for(url: str, timeout: float) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            time.sleep(0.25)
    return False


def _post(url: str, body: bytes, headers: dict[str, str]) -> dict:
    req = urllib.request.Request(url, data=body, method="POST")
    for key, value in headers.items():
        req.add_header(key, value)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


# ----------------------------------------------------------------------- main

def main() -> int:
    print("Cloud Computing: Principles and Practice — environment check")
    print("Nothing is installed or changed, and no cloud service is contacted.")

    section("This machine")
    check_python()
    check_platform()
    check_disk_space()
    check_network()

    section("The course application")
    check_application_runs()
    check_tests()

    section("Container tooling (needed from Lab 1)")
    check_container_runtime()

    fails = [r for r in results if r[0] == "FAIL"]
    warns = [r for r in results if r[0] == "WARN"]

    section("Summary")
    print(f"  {len(results) - len(fails) - len(warns)} passed, "
          f"{len(warns)} warnings, {len(fails)} failures")
    if fails:
        print("\n  Bring this output to the week 1 session. Failing checks:")
        for _, check, _ in fails:
            print(f"    - {check}")
        print("\n  Do not try to work around these alone — that is what the session is for.")
        return 1
    if warns:
        print("\n  Nothing is blocking you. Read the warnings before Lab 1.")
    else:
        print("\n  Everything the course needs is working on this machine.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
