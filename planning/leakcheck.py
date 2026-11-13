#!/usr/bin/env python3
"""Refuse anything that belongs in the private instructor repository.

    python3 planning/leakcheck.py          # exit 1 and name the file if anything leaks

This repository is PUBLIC (D-01). Quiz and exam papers, quiz keys, lab solutions, teaching notes and
grading guidance live in ../cloudengineering-instructor and must never appear here, because
a leaked key stays readable in every clone and fork for good.

Three independent checks, run over every file git would publish (tracked, plus untracked
files that are not ignored):

1. Paths.    No file may sit where private material lives (exam-papers/, quizzes/, quiz-keys/, ...) or
             carry a private-looking name (midterm*.md, *-key.*, *solution*).
2. Content.  No answer-key, expected-answer or solution heading, and no credential.
3. Fingerprint. When the private repository is present beside this one, no line of its prose
             (keys, papers, notes; 40+ characters) may appear here, and no public file may
             hold most of a reference solution's code. Scaffolding a stub shares with its
             solution (signatures, error messages) is expected; a copied solution is not.
             Skipped, and said so, when the private repository is not on this machine.

It runs from the pre-commit and pre-push hooks in .githooks/ and as check 10 of audit.py.
Standard library only.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = Path(os.environ.get("CLOUDENG_PRIVATE", ROOT.parent / "cloudengineering-instructor"))

PRIVATE_DIRS = ("exam-papers", "quiz-keys", "lab-solutions", "pilot-evidence", "teaching-notes",
                "instructor", "solution", "solutions", "quizzes")     # quiz papers too (D-71)
PRIVATE_NAMES = [
    re.compile(r"(^|/)midterm[^/]*\.(md|pdf|docx?)$", re.I),
    re.compile(r"(^|/)final(-paper)?\.(md|pdf|docx?)$", re.I),    # the final paper, anywhere
    re.compile(r"(^|/)(final-)?practice[^/]*\.(md|pdf|docx?)$", re.I),   # the practice set (D-71)
    re.compile(r"(^|/)quiz-\d+\.(md|pdf|docx?)$", re.I),            # a quiz paper (D-71)
    re.compile(r"-key\.[a-z]+$", re.I),
    re.compile(r"answer[-_ ]?key", re.I),
    re.compile(r"solution", re.I),
    re.compile(r"(^|/)(project-guidance|delivery-guide)\.md$", re.I),
]
FORBIDDEN = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r'"private_key"\s*:'), "service-account key"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}"), "Google API key"),
    (re.compile(r"\bya29\.[0-9A-Za-z_\-]{20,}"), "OAuth access token"),
    (re.compile(r"^#+\s*Answer key", re.I | re.M), "answer key heading"),
    (re.compile(r"^#+\s*(Model|Expected)\s+answers?", re.I | re.M), "expected-answers heading"),
    (re.compile(r"^#+\s*(Reference\s+)?Solution\b", re.I | re.M), "solution heading"),
    (re.compile(r"^#+\s*(Marking|Grading)\s+(key|scheme|guide)", re.I | re.M), "marking-key heading"),
]
BINARY = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".ico", ".woff", ".woff2"}
CODE = {".py", ".sh", ".tf", ".yml", ".yaml"}
MIN_LINE = 40          # shorter lines are too generic to fingerprint
CODE_SHARE = 0.6       # a stub shares up to ~50% of its solution's long lines today


def publishable() -> list[str]:
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [f for f in out.splitlines() if (ROOT / f).is_file()]


def norm(line: str) -> str:
    """Compare lines as text, not layout: no indentation, list or heading marks, or case."""
    line = re.sub(r"^[\s>#*|+\-]*(\d+[.)]\s*)?", "", line)
    return re.sub(r"\s+", " ", line).strip().lower()


def read(path: Path) -> str | None:
    if path.suffix.lower() in BINARY:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def check(files: list[str]) -> tuple[list[str], list[str]]:
    problems, notes = [], []
    me = Path(__file__).resolve()

    # 1. paths
    for f in files:
        parts = f.split("/")
        if any(p in PRIVATE_DIRS for p in parts[:-1]) or any(p.search(f) for p in PRIVATE_NAMES):
            problems.append(f"{f}: a private-looking path (this repository is PUBLIC)")

    # 2. content
    texts = {}
    for f in files:
        body = read(ROOT / f)
        if body is None:
            continue
        texts[f] = body
        if (ROOT / f).resolve() in (me, (ROOT / "planning/audit.py").resolve()):
            continue   # these hold the patterns by definition
        for pat, label in FORBIDDEN:
            if pat.search(body):
                problems.append(f"{f}: {label} (this repository is PUBLIC)")

    # 3. fingerprint against the private repository
    if not PRIVATE.is_dir():
        notes.append(f"fingerprint: skipped, no private repository at {PRIVATE}")
        return problems, notes
    prose, code = {}, {}
    for p in sorted(PRIVATE.rglob("*")):
        # .githooks is the private repository's tooling, not course content; its comments
        # legitimately share lines with this repository's own hooks.
        if (not p.is_file() or ".git" in p.parts or ".githooks" in p.parts
                or p.name in ("README.md", ".gitignore")):
            continue
        body = read(p)
        if body is None:
            continue
        rel = str(p.relative_to(PRIVATE))
        lines = {n for n in map(norm, body.splitlines()) if len(n) >= MIN_LINE}
        if p.suffix.lower() in CODE:
            code[rel] = lines
        else:
            for n in lines:
                prose.setdefault(n, rel)
    public_lines = {f: {norm(l) for l in body.splitlines()} for f, body in texts.items()}
    for f, lines in public_lines.items():
        leaked = sorted({prose[n] for n in lines if n in prose})
        for src in leaked:
            problems.append(f"{f}: contains text from the private {src}")
        for src, sol in code.items():
            if sol and len(sol & lines) / len(sol) > CODE_SHARE:
                problems.append(f"{f}: holds {len(sol & lines)} of {len(sol)} lines of the private "
                                f"{src} — a solution, not a stub")
    notes.append(f"fingerprint: {len(prose)} private prose lines and {len(code)} solution files "
                 f"checked against {len(public_lines)} public files")
    return problems, notes


def main() -> int:
    problems, notes = check(publishable())
    for n in notes:
        print(f"  · {n}")
    if problems:
        print("\nPRIVATE MATERIAL IN THE PUBLIC REPOSITORY — nothing was committed or pushed:")
        for p in problems:
            print(f"  ✗ {p}")
        print("\nMove it to ../cloudengineering-instructor. See operations/publishing-checklist.md.")
        return 1
    print("  ✓ nothing private found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
