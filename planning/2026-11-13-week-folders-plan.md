# Week Folders Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task by task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make each `weeks/week-NN/` folder a student's starting point that shows what to read,
what to do, and what is due. Labs, exam rules and the project move into their weeks, and the
teaching guides move out.

**Architecture:** Every move is made with `git mv` from one path map. All references in both
repositories are rewritten by a single scripted pass driven by that same map. A new audit
check pins the result: retired paths must not exist, and nothing may refer to them.

**Tech stack:**
- Python 3 standard library, for the rewrite script and `audit.py`;
- bash, for the starter scripts;
- git.

**Spec:** `planning/2026-11-13-week-folders-design.md`

## Global constraints

- **History.** Use `git mv` for every move, so each file keeps its history.
- **Path map.** These are exact.

  | From | To |
  |---|---|
  | `labs/lab-01` | `weeks/week-02/lab-01` |
  | `labs/lab-02` | `weeks/week-04/lab-02` |
  | `labs/lab-03` | `weeks/week-06/lab-03` |
  | `labs/lab-04` | `weeks/week-09/lab-04` |
  | `labs/lab-05` | `weeks/week-11/lab-05` |
  | `labs/lab-06` | `weeks/week-13/lab-06` |
  | `exams/README.md` | `weeks/week-08/exams.md` |
  | `project/` | `weeks/week-11/project/` |
  | `weeks/week-NN/teaching-guide.md` | `course/teaching-guides/week-NN.md` |

- **Content.** Do not change teaching content. Only paths, links and the new READMEs change.
- **Course-wide folders stay put:**
  - `application/`;
  - `infra/`;
  - `.github/`;
  - `operations/`;
  - `course/`, except the teaching guides.
- **The private repository** at `../cloudengineering-instructor` gets the same rewrite in the
  same session.
- **Decision.** Record it as D-72, which revises D-12.

## Review focus

1. **A `cd` command a student copies from a lab README or the notes**, for example
   `cd labs/lab-06/starter`, must point to a folder that exists. Task 3's stale-path grep
   covers commands in code spans as well as links.
2. **A starter script run from its new location** must find `application/`, because the
   folder is now one level deeper. Task 3 echo-tests every script that climbs with `../`.
3. **Relative links inside moved files**, such as a lab README linking to `../../application`
   or `../../operations/cleanup.md`, now need one more `../`. Task 3 rewrites them, and the
   link check in Task 6 proves them.
4. **The deploy workflow and `.gitignore`** use the paths as plain strings, not links. Task 3's
   rewrite includes them. Task 6 runs `git check-ignore` on the moved `config.env` paths.
5. **The claude.ai decks** show the old paths in slide text. Task 5 regenerates them and
   republishes only the slides whose files changed.

---

### Task 1: An audit check that pins the new layout (written first, fails first)

**Files:**
- Modify: `planning/audit.py`. Add check 10, "retired paths", after check 9.

**Produces:** check 10 lists, as problems, any file that still exists at a retired path, and
any reference to one.

- [ ] **Step 1: Add check 10.**
  - **Retired paths:**
    - `labs/`;
    - `exams/README.md`;
    - `project/`;
    - `weeks/week-NN/teaching-guide.md`.
  - **The pattern to search for:** the regex
    `\b(labs/lab-0\d|exams/README\.md|(?<![\w/-])project/(brief|rubric|milestones)\.md|weeks/week-\d\d/teaching-guide\.md)`.
  - **What it searches:** every publishable text file (`leakcheck.publishable()`), excluding
    `course/slides/artifact/`.
  - **Exemptions:** `planning/progress.md`, `planning/decisions.md` and the two
    `2026-11-13-week-folders-*.md` files, which keep history and the map. For those files,
    report the matches as notes.
- [ ] **Step 2: Run `python3 planning/audit.py`.**
  - **Expected:** it FAILS, with around 95 retired-path problems, and `labs/` reported as
    existing.

### Task 2: The moves

**Files:** everything in the path map above.

- [ ] **Step 1: Move the folders.**
  - Run `git mv` for each row of the map.
  - Create `course/teaching-guides/` and move the 15 guides into it.
- [ ] **Step 2: Remove the empty folders.**
  - `labs/`, `exams/` and `project/` should be empty. Remove them.
- [ ] **Step 3: Check the result.**
  - **Run:** `git status --short | grep -c '^R'`
  - **Expected:** 9 to 10 rename groups, covering about 70 files. There should be no `D`
    (delete) or `A` (add) lines for these paths.

### Task 3: Rewrite every reference, in both repositories

**Files:**
- Create: `<scratchpad>/rewrite_paths.py`. This is a one-off and is not committed.
- Modify: every file that matches.

The script holds the path map as an ordered list of (old, new) pairs, applied longest first.
It covers each lab folder, the exam document, the project files, and the 15 guides.

- [ ] **Step 1: Rewrite repository-root paths.**
  - Replace them as plain strings in:
    - every text file in both repositories;
    - `.github/workflows/deploy.yml`;
    - `.gitignore`.
  - Exclude `.git/`, `course/slides/artifact/` and `Claude outputs/`.
- [ ] **Step 2: Fix relative links in files that moved.**
  - Re-resolve every relative Markdown link (`](…)`) from the file's **old** location.
  - Then re-relativise it to the file's **new** location.
  - Do this for files that link **to** a moved file as well.
- [ ] **Step 3: Fix starter-script depth.**
  - In every `*.sh` file under the new `weeks/week-*/lab-0*/starter/`, change
    `/../../../application` to `/../../../../application`, and do the same for any other
    `../` chain to the repository root.
- [ ] **Step 4: Echo-test each script that climbs.**
  - From its new location, evaluate the script's `APP_SRC`/root expression.
  - **Expected:** it prints `<repo>/application`.
  - Also run `bash -n` on every starter script. **Expected:** silent.
- [ ] **Step 5: Run `python3 planning/audit.py`.**
  - **Expected:** check 10 passes. The remaining failures are checks 6 and 8, which still
    point at old paths. Task 4 fixes those.

### Task 4: Tooling follows the layout

**Files:**
- Modify: `planning/audit.py`, checks 6 and 8.

- [ ] **Step 1: Update the paths in checks 6 and 8.**
  - Check 6 reads `course/teaching-guides/week-NN.md`.
  - Check 8 reads `weeks/week-08/exams.md`, plus the week 8 and week 14 guides at their new
    paths.
- [ ] **Step 2: Run `python3 planning/audit.py`.**
  - **Expected:** `No problems found.`
- [ ] **Step 3: Run `python3 planning/leakcheck.py`.**
  - **Expected:** `nothing private found`.

### Task 5: The week READMEs and the decks

**Files:**
- Create: `weeks/week-01/README.md` to `weeks/week-15/README.md`.
- Regenerate: `course/slides/artifact/`.

- [ ] **Step 1: Write each week's README.**
  - **Title:** `# Week N — <title from the schedule>`, followed by one line from the schedule.
  - **Read:** the student notes; the claude.ai deck, using the link in
    `course/slides/artifact/decks.json`; and the reading time from `workload-budget.md`.
  - **Do:** the lab parts for the session and for the independent time, linking to the lab
    README (in its own week, or back to the week the lab started).
  - **Due:** taken from the "Due" column of the schedule table, with the day it is due. Weeks
    8 and 14 link to `exams.md`. Weeks 11 to 15 link to `project/`.
- [ ] **Step 2: Regenerate the decks.**
  - Run `python3 course/slides/to_artifact.py all`.
  - Then `git status course/slides/artifact`. Expected: only slides whose text names a moved
    path have changed.
- [ ] **Step 3: Republish those slides only,** one Artifact call per affected deck.

### Task 6: Records, final verification, commit

**Files:**
- Modify:
  - `README.md` (the tree);
  - `course/syllabus.md` ("Where things are");
  - `course/weekly-schedule.md` (intro note);
  - `planning/decisions.md` (D-72);
  - `planning/progress.md`;
  - the design doc's status line, to "implemented".

- [ ] **Step 1: Write the records.**
- [ ] **Step 2: Run the stale-path grep.**
  - **Run:** `git grep -n -E 'labs/lab-0|exams/README|teaching-guide\.md'`
  - **Expected:** matches only in the exempted history files.
- [ ] **Step 3: Run the checks.**
  - **Run:** `python3 planning/audit.py && python3 planning/leakcheck.py && (cd application && python3 -m pytest -q)`
  - **Expected:** no problems, nothing private, and the tests pass.
- [ ] **Step 4: Check the ignore rules.**
  - **Run:** `git check-ignore -v weeks/week-04/lab-02/starter/config.env`
  - **Expected:** it is matched by a `.gitignore` rule. Repeat for labs 4, 5 and 6.
- [ ] **Step 5: Commit each repository.**
  - The public commit runs the leak hook. Push only when the instructor asks.
