#!/usr/bin/env python3
"""Check a lab or project write-up before you hand it in, and print the link to turn in
on Teams.

    python3 operations/check_submission.py 1          # Lab 1 (1 to 6); run anywhere in your repo
    python3 operations/check_submission.py proposal   # the project proposal, week 12
    python3 operations/check_submission.py project    # the final project submission, week 15

It reads your repository and changes nothing. Every problem is reported with what to do
about it. The link names one commit, so what the marker opens is exactly what you handed in.
How handing in works: operations/lab-submission.md.

Standard library only, Python 3.10+, macOS / Linux / Windows.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

COURSE_REPO = "pasdptt/public_teaching_cloudengineering"

# Credentials. The same shapes the course repository refuses for itself (planning/leakcheck.py).
SECRETS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "a private key"),
    (re.compile(r'"private_key"\s*:'), "a service-account key file"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}"), "a Google API key"),
    (re.compile(r"\bya29\.[0-9A-Za-z_\-]{20,}"), "an OAuth access token"),
    (re.compile(r"\beyJ[0-9A-Za-z_\-]{10,}\.eyJ[0-9A-Za-z_\-]{10,}\.[0-9A-Za-z_\-]{10,}"),
     "an identity token (JWT)"),
    (re.compile(r"\bgh[pousr]_[0-9A-Za-z]{30,}"), "a GitHub token"),
]
# Home directories in pasted output. ~/ is fine; /Users/<you>/ is not.
PERSONAL_PATH = re.compile(r"(/Users/|/home/|[A-Za-z]:\\Users\\)(?!yourname|you\b|USER|<)[^/\\\s`]+")
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
# Links shown inside code (a fenced block or an inline span) are examples, not links.
FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})[^\n]*\n.*?^[ \t]*\1[ \t]*$", re.M | re.S)
CODE_SPAN = re.compile(r"(`+)(?!`).+?(?<!`)\1", re.S)

problems: list[str] = []
notes: list[str] = []


def git(*args: str, cwd: Path | None = None) -> str:
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or f"git {' '.join(args)} failed")
    return out.stdout.strip()


def problem(msg: str) -> None:
    problems.append(msg)
    print(f"  ✗ {msg}")


def ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def note(msg: str) -> None:
    notes.append(msg)
    print(f"  · {msg}")


def owner_and_name(url: str) -> str | None:
    """'https://github.com/a/b.git' or 'git@github.com:a/b.git' -> 'a/b'."""
    m = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    return f"{m.group(1)}/{m.group(2)}" if m else None


def target_for(arg: str) -> tuple[str, str, str, tuple[str, str] | None, str] | None:
    """(label, folder, file, (where the item list is, its heading) or None, how to start it)."""
    if arg.isdigit() and 1 <= int(arg) <= 6:
        n = int(arg)
        folder = f"submissions/lab-{n:02d}"
        return (f"Lab {n}", folder, "README.md",
                (f"weeks/week-*/lab-{n:02d}/README.md", "What to submit"),
                f"mkdir -p {folder} && cp submissions/TEMPLATE.md {folder}/README.md")
    if arg == "project":
        return ("Project", "submissions/project", "README.md",
                ("weeks/week-11/project/brief.md", "What you submit"),
                "mkdir -p submissions/project && cp submissions/TEMPLATE.md "
                "submissions/project/README.md")
    if arg == "proposal":
        return ("Project proposal", "submissions/project", "proposal.md", None,
                "mkdir -p submissions/project, then paste the proposal template from\n"
                "      weeks/week-11/project/milestones.md (Week 12) into submissions/project/proposal.md")
    return None


def expected_items(root: Path, source: tuple[str, str]) -> list[tuple[str, bool]]:
    """The numbered items under the brief's list heading, as (name, optional).

    An item that applies only to pairs ("... if you are a pair") is optional."""
    pattern, heading = source
    briefs = sorted(root.glob(pattern))
    if not briefs:
        return []
    text = briefs[0].read_text(encoding="utf-8")
    m = re.search(rf"^## {heading}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return []
    return [(name, "if you are a pair" in rest)
            for name, rest in re.findall(r"^\d+\.\s+\*\*(.+?)\*\*(.*)$", m.group(1), re.M)]


def main() -> int:
    # A Windows console that is not UTF-8 would otherwise crash on the first tick mark.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    target = target_for(sys.argv[1].lower()) if len(sys.argv) == 2 else None
    if not target:
        print("usage: python3 operations/check_submission.py WHAT\n"
              "  WHAT is a lab number (1 to 6), proposal, or project")
        return 2
    label, folder, filename, source, start = target

    try:
        root = Path(git("rev-parse", "--show-toplevel"))
    except (RuntimeError, FileNotFoundError):
        print("✗ Not inside a git repository. cd into your cloned repository and run it again.")
        return 1
    writeup = root / folder / filename
    print(f"{label} — {folder}/{filename}\n")

    # ---- the write-up -------------------------------------------------------------------
    print("Write-up")
    if not writeup.is_file():
        problem(f"{folder}/{filename} does not exist. Start it with:\n      {start}")
        return finish(None, label)
    text = writeup.read_text(encoding="utf-8", errors="replace")
    ok("exists")

    sections = re.findall(r"^##\s+(.+?)\s*$", text, re.M)
    items = expected_items(root, source) if source else []
    if items:
        numbered = {int(n) for n in re.findall(r"^##\s+(\d+)[.)]", text, re.M)}
        missing = [f"{i}. {name}" for i, (name, optional) in enumerate(items, 1)
                   if i not in numbered and not optional]
        pairs_only = [f"{i}. {name}" for i, (name, optional) in enumerate(items, 1)
                      if i not in numbered and optional]
        if missing:
            problem(f"no numbered `## ` section for {len(missing)} of the {len(items)} items "
                    f"in the {source[1]} list:\n" + "\n".join(f"      {m}" for m in missing))
        else:
            required = sum(1 for _, optional in items if not optional) if pairs_only else len(items)
            ok(f"a numbered section for each of the {required} required items in the {source[1]} list")
        if pairs_only:
            note("no section for " + ", ".join(pairs_only) + ". Needed only if you are a pair")
    elif source:
        note(f"could not read the {source[1]} list; {len(sections)} sections found")
    if re.search(r"^# Lab N\b|Copy this file; do not edit it here", text, re.M):
        problem("still has the template's title or instructions. Replace them with your own")

    tracked = set(git("ls-files", cwd=root).splitlines())
    broken = []
    for target in LINK.findall(CODE_SPAN.sub("", FENCE.sub("", text))):
        if re.match(r"[a-z]+:|#|mailto:", target):
            continue
        path = (writeup.parent / target.split("#")[0]).resolve()
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            broken.append(f"{target} (outside the repository)")
            continue
        if not path.exists():
            broken.append(f"{target} (no such file)")
        elif path.is_file() and rel not in tracked:
            broken.append(f"{target} (exists, but is not committed)")
    if broken:
        problem("links the marker cannot follow:\n" + "\n".join(f"      {b}" for b in broken))
    else:
        ok("every relative link points at a committed file")

    personal = sorted({m.group(0) for m in PERSONAL_PATH.finditer(text)})
    if personal:
        problem("personal home-directory paths in the write-up (write ~/ instead): "
                + ", ".join(personal[:5]))
    else:
        ok("no personal paths")

    # ---- secrets, anywhere in the repository ---------------------------------------------
    print("\nCredentials (every committed file, and the write-up)")
    found = []
    for rel in sorted(tracked | {f"{folder}/{filename}"}):
        p = root / rel
        try:
            if not p.is_file() or p.stat().st_size > 2_000_000:
                continue
            content = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern, what in SECRETS:
            if pattern.search(content):
                found.append(f"{rel}: looks like {what}")
    if found:
        problem("possible credentials. Revoke first, then remove, then tell the instructor "
                "(GitHub 101, section 6):\n" + "\n".join(f"      {f}" for f in found))
    else:
        ok("nothing that looks like a key, token or password")

    # ---- git: committed, pushed, private ------------------------------------------------
    print("\nRepository")
    dirty_here = git("status", "--porcelain", "--", folder, cwd=root)
    if dirty_here:
        problem(f"uncommitted changes in {folder}/:\n"
                + "\n".join(f"      {line}" for line in dirty_here.splitlines()))
    else:
        ok(f"{folder}/ is committed")
    dirty = [l for l in git("status", "--porcelain", "--untracked-files=no", cwd=root).splitlines()
             if not l[3:].startswith(folder)]
    if dirty:
        note("other files have uncommitted changes, and they are NOT in the link. If the work "
             "needs them, commit them:\n"
             + "\n".join(f"      {line}" for line in dirty[:10]))

    head = git("rev-parse", "HEAD", cwd=root)
    try:
        origin = git("remote", "get-url", "origin", cwd=root)
    except RuntimeError:
        problem("no `origin` remote. Connect your private repository (GitHub 101, section 3)")
        return finish(None, label)
    repo = owner_and_name(origin)
    if not repo:
        problem(f"`origin` is not a GitHub repository: {origin}")
        return finish(None, label)
    if repo.lower() == COURSE_REPO.lower():
        problem("`origin` is the course repository, not yours. You cannot push there, and the "
                "marker would not find your work. GitHub 101, section 3, steps 3–5")
        return finish(None, label)
    ok(f"origin is {repo}")

    pushed = git("branch", "-r", "--contains", head, cwd=root)
    if not any(b.strip().startswith("origin/") for b in pushed.splitlines()):
        problem("this commit is not pushed. Run `git push`, then this check again")
        link_ready = False
    else:
        ok("this commit is pushed")
        link_ready = True

    if shutil.which("gh"):
        vis = subprocess.run(["gh", "repo", "view", repo, "--json", "visibility",
                              "-q", ".visibility"], capture_output=True, text=True)
        if vis.returncode == 0 and vis.stdout.strip() == "PRIVATE":
            ok("the repository is private")
        elif vis.returncode == 0:
            problem(f"the repository is {vis.stdout.strip()}. Make it private: Settings → "
                    "General → Danger Zone → Change visibility")
        else:
            note("could not ask GitHub whether it is private (offline, or `gh` not logged in). "
                 "Check on its page: it should say Private")
    else:
        note("GitHub CLI not installed, so visibility was not checked. Its page should say "
             "Private, and Settings → Collaborators should list the instructor")

    # A README opens with its folder, so link the folder; any other file is linked itself.
    url = (f"https://github.com/{repo}/tree/{head}/{folder}" if filename == "README.md"
           else f"https://github.com/{repo}/blob/{head}/{folder}/{filename}")
    return finish(url, label, link_ready)


def finish(url: str | None, label: str, link_ready: bool = True) -> int:
    print()
    if url and not problems:
        print(f"Ready. Turn this link in on the {label} assignment in Teams:\n\n  {url}\n")
        return 0
    print(f"{len(problems)} problem(s) to fix before you hand in.")
    if url:
        state = "not pushed yet" if not link_ready else "fix the problems first"
        print(f"\nThe link for this commit ({state}):\n\n  {url}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
