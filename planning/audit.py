#!/usr/bin/env python3
"""Consistency audit for the course repository.

Checks that can be made mechanically, so they are not re-argued every session:

  1. Every relative Markdown link points at a file that exists.
  2. Every row of the weekly workload table sums to exactly 180 minutes.
  3. Assessment weights (quizzes, labs, project, midterm, final) sum to 100%, and the lab
     weight divides evenly across six labs.
  4. No answer-key, solution or credential-shaped content in this public repo.
  5. Every course learning outcome (CLO-1..9) is referenced in the assessment plan.
  6. Every teaching guide's session plan sums to exactly 180 contact minutes, and every
     week has an authored guide and authored student notes.
  7. Every quiz (six of them; private, D-71) is authored, states the weeks it covers, has question marks that
     add up to its stated total, and Quiz 6 does not reach into same-day infrastructure material.
  8. The two exam weeks (8 and 14) each give a 120-minute block to the exam, and the exam
     format document exists. Twelve teaching weeks is a structural claim (D-66); this is the
     part of it a script can check.

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
                      ("project", r"Project\s*\|\s*\*\*(\d+)%\*\*"),
                      ("midterm", r"Midterm exam\s*\|\s*\*\*(\d+)%\*\*"),
                      ("final", r"Final exam\s*\|\s*\*\*(\d+)%\*\*")):
        m = re.search(pat, text)
        if m:
            weights[name] = int(m.group(1))
        else:
            problems.append(f"could not find {name} weight in assessment-plan.md")
    if len(weights) == 5:
        total = sum(weights.values())
        if total != 100:
            problems.append(f"assessment weights sum to {total}%, not 100% ({weights})")
        notes.append(f"assessment weights: {weights} = {total}%")
    # six equally weighted labs: the labs weight must divide evenly, and every lab README
    # and rubric must state the same per-lab share
    if weights.get("labs") is not None:
        per_lab = weights["labs"] / 6
        share = f"{per_lab:g}% of the final grade"
        share_re = re.compile(r"(?<![\d.])" + re.escape(share))
        for lab in sorted((ROOT / "labs").glob("lab-0*")):
            for doc in ("README.md", "rubric.md"):
                f = lab / doc
                if f.exists() and not share_re.search(f.read_text(encoding="utf-8")):
                    problems.append(f"{f.relative_to(ROOT)} does not state '{share}' "
                                    f"(labs {weights['labs']}% / 6)")
else:
    problems.append("course/assessment-plan.md missing")

# ------------------------------------------- 4. nothing that belongs private
# One implementation, shared with the pre-commit and pre-push hooks (.githooks/): paths,
# answer-key and credential patterns, and a fingerprint against the private repository.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import leakcheck  # noqa: E402

leak_problems, leak_notes = leakcheck.check(leakcheck.publishable())
problems.extend(leak_problems)
notes.extend(f"private content — {n}" for n in leak_notes)

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
    guide = ROOT / "course" / "teaching-guides" / f"week-{wk:02d}.md"   # D-72
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
        problems.append(f"week {wk:02d} has no course/teaching-guides/week-{wk:02d}.md")
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

# ------------------------------------------------------------ 7. quizzes
#
# Mechanical claims only: authored, honest about coverage, marks that add up. Whether a
# question is any good is a judgement this file does not make.
#
# Quiz 6 gets one content check, because it is the defect this repository has already made
# once: it sits in the week declarative infrastructure is first taught (week 13 since D-66),
# and may reach CLO-7 and CLO-9 only through the cleanup and CI threads (assessment-plan.md).
# The terms below are that week's vocabulary, which no Quiz 6 question should need.
QUIZ_TOTAL = re.compile(r"^\*\*(\d+) marks\b", re.M)
QUESTION_MARKS = re.compile(r"^## Question \d+\b.*\((\d+) marks?\)\s*$", re.M)
SAME_DAY_Q6 = re.compile(r"\b(terraform|opentofu|tfvars|workspace|drift|state file)\b", re.I)
# The papers are private (D-71), so this check reads them from the instructor repository when
# it sits beside this one, and says it was skipped when it does not.
QUIZ_DIR = leakcheck.PRIVATE / "quizzes"
quizzes_checked = 0
for n in range(1, 7 if QUIZ_DIR.is_dir() else 1):
    quiz = QUIZ_DIR / f"quiz-{n:02d}.md"
    if not quiz.exists():
        problems.append(f"quiz {n} is missing")
        continue
    text = quiz.read_text(encoding="utf-8")
    if PLACEHOLDER in text:
        problems.append(f"quiz {n} is still a placeholder")
        continue
    head = "\n".join(text.splitlines()[:4])
    if not re.search(r"\*\*Covers weeks? [\d\u2013-]+", head):
        problems.append(f"quiz {n} does not state the weeks it covers in its opening lines")
    total = QUIZ_TOTAL.search(text)
    parts = [int(m) for m in QUESTION_MARKS.findall(text)]
    if not total or not parts:
        problems.append(f"quiz {n}: cannot find its stated total or per-question marks")
    elif sum(parts) != int(total.group(1)):
        problems.append(
            f"quiz {n}: questions carry {sum(parts)} marks but the quiz states {total.group(1)}")
    if n == 6:
        body = text.split("\n---\n", 1)[-1]  # questions only; the header may name what is excluded
        for m in sorted({m.group(0).lower() for m in SAME_DAY_Q6.finditer(body)}):
            problems.append(f"quiz 6 uses same-day week 13 material: '{m}'")
    quizzes_checked += 1
notes.append(f"quizzes authored and consistent: {quizzes_checked}/6" if QUIZ_DIR.is_dir()
             else f"quizzes: skipped, the papers are private (D-71) and {QUIZ_DIR} is absent")
if (QUIZ_DIR / "quiz-07.md").exists():
    problems.append("quizzes/quiz-07.md exists, but there are six quizzes (D-66); Quiz 7 became "
                    "the final practice set")

# ----------------------------------------------------------- 8. exam weeks
#
# D-66 cut teaching to twelve weeks by giving weeks 8 and 14 to written exams. If either
# week's session plan stops giving the exam its 120 minutes, teaching has crept back in.
exam_doc = ROOT / "weeks" / "week-08" / "exams.md"   # D-72: the exam rules live in week 8
if not exam_doc.exists():
    problems.append("weeks/week-08/exams.md is missing (exam format, D-68)")
for wk in (8, 14):
    guide = ROOT / "course" / "teaching-guides" / f"week-{wk:02d}.md"
    if not guide.exists():
        continue  # already reported by check 6
    rows = [ln for ln in guide.read_text(encoding="utf-8").splitlines()
            if re.match(r"^\|\s*\**[^|]*exam[^|]*\**\s*\|\s*120\s*\|", ln, re.I)]
    if not rows:
        problems.append(f"week {wk:02d} session plan has no 120-minute exam block (D-66)")
notes.append("exam weeks 8 and 14 checked for a 120-minute exam block")

# ------------------------------------------------- 9. slide decks, if present
#
# Decks are derived from the teaching guides and carry the guide's block timings. The sum
# has to be the same 180 minutes the workload budget and the session plans use, or the deck
# and the guide have drifted apart.
SLIDE_CLASSES = {"lead", "block", "ask", "demo", "cost", "punch", "split"}
decks = sorted((ROOT / "weeks").glob("week-*/slides.md"))
for deck in decks:
    rel = deck.relative_to(ROOT)
    body = deck.read_text(encoding="utf-8")

    if not body.lstrip().startswith("---"):
        problems.append(f"{rel}: no Marp front matter")
        continue
    if "marp: true" not in body:
        problems.append(f"{rel}: front matter does not set 'marp: true'")
    if "theme: cloudcourse" not in body:
        problems.append(f"{rel}: does not use the shared 'cloudcourse' theme")

    minutes = [int(m) for m in re.findall(r'<span class="min">[^<]*?(\d+)\s*minutes?', body)]
    total = sum(minutes)
    if not minutes:
        problems.append(f"{rel}: no block timing markers")
    elif total != 180:
        problems.append(
            f"{rel}: block timings sum to {total} minutes, not 180 "
            f"(found {minutes}) — the deck and the session plan have drifted"
        )

    used = set(re.findall(r"<!--\s*_class:\s*([\w\s]+?)\s*-->", body))
    for spec in used:
        for name in spec.split():
            if name not in SLIDE_CLASSES:
                problems.append(f"{rel}: unknown slide class '{name}'")

    if (ROOT / "course" / "slides" / "theme.css").exists() is False:
        problems.append("course/slides/theme.css is missing but decks reference it")
notes.append(f"slide decks checked: {len(decks)} (timings must sum to 180)")

# ----------------------------------------------- 10. retired paths (D-72)
# Each week folder is a student's starting point: its lab, the exam rules and the project
# live inside the weeks, and the teaching guides live in course/teaching-guides/. Nothing may
# remain at, or point to, the old places. The history files keep old paths on purpose.
RETIRED_DIRS = ["labs", "exams", "project"]
RETIRED_REF = re.compile(r"\b(labs/lab-0\d|exams/README\.md|(?<!week-11/)(?<!\()project/(brief|rubric|milestones)\.md"
                         r"|weeks/week-\d\d/teaching-guide\.md)")
HISTORY = {"planning/progress.md", "planning/decisions.md",
           "planning/2026-11-13-week-folders-design.md", "planning/2026-11-13-week-folders-plan.md"}
for d in RETIRED_DIRS:
    if (ROOT / d).exists():
        problems.append(f"{d}/ still exists; its contents belong in the week folders (D-72)")
for g in sorted((ROOT / "weeks").glob("week-*/teaching-guide.md")):
    problems.append(f"{g.relative_to(ROOT)} still exists; guides live in course/teaching-guides/")
history_hits = 0
for f in leakcheck.publishable():
    if f.startswith("course/slides/artifact/") or not f.endswith((".md", ".sh", ".yml", ".py", ".tf", ".txt")) \
            and not f.endswith(".gitignore"):
        continue
    if f == "planning/audit.py":
        continue   # holds the pattern by definition
    try:
        lines = (ROOT / f).read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        continue
    for i, line in enumerate(lines, 1):
        if RETIRED_REF.search(line):
            if f in HISTORY:
                history_hits += 1
            else:
                problems.append(f"{f}:{i}: refers to a retired path: {RETIRED_REF.search(line).group(0)}")
notes.append(f"retired paths: checked ({history_hits} mentions kept in history files)")

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
