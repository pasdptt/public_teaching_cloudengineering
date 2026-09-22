#!/usr/bin/env python3
"""Consistency audit for the course repository.

Checks that can be made mechanically, so they are not re-argued every session:

  1. Every relative Markdown link points at a file that exists.
  2. Every row of the weekly workload table sums to exactly 180 minutes.
  3. Assessment weights sum to 100%.
  4. No answer-key, solution or credential-shaped content in this public repo.
  5. Every course learning outcome (CLO-1..9) is referenced in the assessment plan.
  6. Every teaching guide's session plan sums to exactly 180 contact minutes, and every
     week has an authored guide and authored student notes.

Run from anywhere:  python3 planning/audit.py
Exit code 0 = clean, 1 = problems found.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
problems: list[str] = []
notes: list[str] = []


def md_files():
    for p in sorted(ROOT.rglob("*.md")):
        if ".git" in p.parts:
            continue
        yield p


# ---------------------------------------------------------------- 1. links
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
checked = 0
for p in md_files():
    for target in LINK.findall(p.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = target.split("#", 1)[0]
        if not target:
            continue
        checked += 1
        if not (p.parent / target).resolve().exists():
            problems.append(f"broken link in {p.relative_to(ROOT)} -> {target}")
notes.append(f"relative links checked: {checked}")

# ------------------------------------------------- 2. weekly workload = 180
budget = ROOT / "course" / "workload-budget.md"
rows = 0
if budget.exists():
    for line in budget.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*(\d{1,2})\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", line)
        if not m:
            continue
        wk, reading, lab, other, total = (int(g) for g in m.groups())
        rows += 1
        if reading + lab + other != total:
            problems.append(f"workload week {wk}: {reading}+{lab}+{other} != stated total {total}")
        if total != 180:
            problems.append(f"workload week {wk}: total {total} != 180")
    if rows != 15:
        problems.append(f"workload table has {rows} week rows, expected 15")
    notes.append(f"workload week rows checked: {rows}")
else:
    problems.append("course/workload-budget.md missing")

# --------------------------------------------------- 3. weights sum to 100
plan = ROOT / "course" / "assessment-plan.md"
if plan.exists():
    text = plan.read_text(encoding="utf-8")
    weights = {}
    for name, pat in (("quizzes", r"Quizzes\s*\|\s*\*\*(\d+)%\*\*"),
                      ("labs", r"Labs\s*\|\s*\*\*(\d+)%\*\*"),
                      ("project", r"Project\s*\|\s*\*\*(\d+)%\*\*")):
        m = re.search(pat, text)
        if m:
            weights[name] = int(m.group(1))
        else:
            problems.append(f"could not find {name} weight in assessment-plan.md")
    if len(weights) == 3:
        total = sum(weights.values())
        if total != 100:
            problems.append(f"assessment weights sum to {total}%, not 100% ({weights})")
        notes.append(f"assessment weights: {weights} = {total}%")
    # six labs at 7.5% each must equal the labs weight
    if weights.get("labs") is not None and abs(6 * 7.5 - weights["labs"]) > 1e-9:
        problems.append(f"6 labs x 7.5% = 45%, but labs weight is {weights['labs']}%")
else:
    problems.append("course/assessment-plan.md missing")

# ------------------------------------------- 4. nothing that belongs private
FORBIDDEN = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key block"),
    (re.compile(r'"private_key"\s*:'), "service-account key JSON"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}"), "Google API key"),
    (re.compile(r"\bya29\.[0-9A-Za-z_\-]{20,}"), "OAuth access token"),
    (re.compile(r"^#+\s*Answer key", re.I | re.M), "answer key heading"),
    (re.compile(r"^#+\s*(Model|Expected)\s+answers?", re.I | re.M), "expected-answers heading"),
    (re.compile(r"^#+\s*(Reference\s+)?Solution\b", re.I | re.M), "solution heading"),
]
scanned = 0
for p in ROOT.rglob("*"):
    if not p.is_file() or ".git" in p.parts:
        continue
    if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip"}:
        continue
    try:
        body = p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    scanned += 1
    if p == Path(__file__):
        continue  # this file contains the patterns by definition
    for pat, label in FORBIDDEN:
        if pat.search(body):
            problems.append(f"{label} found in {p.relative_to(ROOT)} (this repo is PUBLIC)")
notes.append(f"files scanned for private content: {scanned}")

# ------------------------------------------------- 5. every CLO is assessed
if plan.exists():
    text = plan.read_text(encoding="utf-8")
    for i in range(1, 10):
        if f"CLO-{i}" not in text:
            problems.append(f"CLO-{i} never appears in course/assessment-plan.md")
    notes.append("CLO-1..9 presence in assessment plan: checked")

# -------------------------------------- 6. session plans = 180 contact min
#
# A-05/A-06 fix the session at three hours. A session plan that sums to more than that is
# not a plan, it is a wish: the block that gets cut on the day is whichever one is last,
# which in every one of these guides is the practical. Checking it mechanically is the only
# way it stays true as the guides are edited.
SESSION_ROW = re.compile(r"^\|\s*(?!Block\b)([^|]+?)\s*\|\s*(\d+)\s*\|")
PLACEHOLDER = "STATUS: not yet authored"
guides = 0
notes_checked = 0
for wk in range(1, 16):
    week_dir = ROOT / "weeks" / f"week-{wk:02d}"
    guide = week_dir / "teaching-guide.md"
    student_notes = week_dir / "student-notes.md"

    # Student notes are checked for existence and for having been authored, but not for
    # length or content -- those are judgements, and this file only makes mechanical claims.
    if not student_notes.exists():
        problems.append(f"week {wk:02d} has no student-notes.md")
    elif PLACEHOLDER in student_notes.read_text(encoding="utf-8"):
        problems.append(f"week {wk:02d} student notes have reverted to a placeholder")
    else:
        notes_checked += 1

    if not guide.exists():
        problems.append(f"week {wk:02d} has no teaching-guide.md")
        continue
    text = guide.read_text(encoding="utf-8")
    if PLACEHOLDER in text:
        # Every week is authored as of 2026-09-22, so a placeholder reappearing is a
        # regression rather than work in progress. It is reported and skipped, because a
        # placeholder's session plan is boilerplate and summing it would just add noise.
        problems.append(f"week {wk:02d} teaching guide has reverted to a placeholder")
        continue
    lines = text.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines)
                     if ln.strip().startswith("| Block") and "Min" in ln)
    except StopIteration:
        problems.append(f"week {wk:02d} teaching guide has no session-plan table")
        continue
    total = 0
    for ln in lines[start + 2:]:
        if not ln.strip().startswith("|"):
            break
        m = SESSION_ROW.match(ln.strip())
        if m:
            total += int(m.group(2))
    guides += 1
    if total != 180:
        problems.append(
            f"week {wk:02d} session plan sums to {total} min, not 180 "
            f"(the contact block is three hours, A-05/A-06)"
        )
if guides != 15:
    problems.append(f"{guides} of 15 weekly session plans are authored and checkable")
notes.append(f"session plans checked: {guides}/15 · student notes: {notes_checked}/15")

# ------------------------------------------------------------------ report
print("Course repository audit")
print("=" * 60)
for n in notes:
    print(f"  · {n}")
print("-" * 60)
if problems:
    print(f"{len(problems)} PROBLEM(S):\n")
    for pr in problems:
        print(f"  ✗ {pr}")
    sys.exit(1)
print("No problems found.")
print("\nNote: this audit checks structure and consistency only. It cannot check")
print("whether the teaching is good, whether timings are realistic, or whether a")
print("cloud lab actually works. Those need a human and a pilot run.")
