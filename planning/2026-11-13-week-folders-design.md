# Design: week folders that a student can work from

**Status:** implemented 2026-11-13 (D-72). Approach C, chosen by the instructor. Plan: `planning/2026-11-13-week-folders-plan.md`.

## Intent

Today a student who opens `weeks/week-NN/` finds the slides, the notes and a teaching guide
written for the instructor. Everything else they need that week is elsewhere: the lab in
`labs/`, the exam rules in `exams/`, the project in `project/`.

The goal: **a student opens one folder and learns what to read, what to do, and what is due.**
The audience is students. Instructor preparation material moves out of their way.

## Goals, non-goals, anti-goals

- **Goal.** Every week folder opens with a `README.md` in three sections: **Read**, **Do**
  and **Due**.
- **Goal.** Each lab lives inside the week it starts.
- **Goal.** No instructor-only file sits in a week folder.
- **Non-goal.** Rewriting any teaching content. Files move; only paths and links change.
- **Non-goal.** Moving code shared by every week. These stay where they are:
  - `application/`;
  - `infra/`;
  - `.github/`;
  - `operations/`;
  - `course/` (except the teaching guides).
- **Anti-goal.** A command a student copies from a lab or the notes no longer works. A path
  that is still right on the page but wrong on disk is a failure, even if every link renders.
- **Anti-goal.** Leaving a public copy of anything that is private (D-01, D-71).

## Approaches considered

- **A. A front page per week only.** Nothing breaks, but the files are still scattered on
  disk.
- **B. A front page, and labs, exams and project move into weeks.** The teaching guides stay
  in the week folders.
- **C. B, plus the week folders hold only student material.** This is the one chosen. It is
  the physical rearrangement that was asked for, and it keeps instructor preparation material
  out of the folder students are told to open.

## The layout

```text
weeks/week-NN/
  README.md          Read · Do · Due for this week (new)
  student-notes.md
  slides.md          the deck's source
  lab-0N/            only in the week the lab starts: README, rubric, starter/
  exams.md           week 08 only (was exams/README.md); week 14 links to it
  project/           week 11 only (was project/): brief, milestones, rubric
course/teaching-guides/week-NN.md     was weeks/week-NN/teaching-guide.md
```

Where each lab moves:

| Lab | New home | Second week (links back) |
|---|---|---|
| Lab 1 | `weeks/week-02/lab-01/` | week 3 |
| Lab 2 | `weeks/week-04/lab-02/` | week 5 |
| Lab 3 | `weeks/week-06/lab-03/` | week 7 |
| Lab 4 | `weeks/week-09/lab-04/` | week 10 |
| Lab 5 | `weeks/week-11/lab-05/` | week 12 |
| Lab 6 | `weeks/week-13/lab-06/` | none (one-week lab) |

The project moves to week 11, where it is released. Weeks 12 to 15 link to its milestones.

**The README content.** Each week's README is drawn from material that already exists, not
written fresh:

- `course/weekly-schedule.md`: what is due;
- `course/workload-budget.md`: the reading time;
- the student notes: what to read.

The README links to:

- the claude.ai deck;
- the notes;
- the lab parts for the week;
- anything due, with its day.

## Constraints the builder must respect

- **Use `git mv`**, so each file keeps its history.
- **Starter scripts move one folder deeper.** `../../../application` becomes
  `../../../../application` in Lab 2 `02-deploy.sh`, Lab 4 `03-build-push.sh`, and any other
  script that climbs. Check every `dirname`, `../` and `ROOT` in every script.
- **Rewrite every path reference across the repository.** About 60 point at labs, and about 35
  at `project/` and `exams/`. This includes:
  - `.github/workflows/deploy.yml`;
  - the `.gitignore` lines for `config.env`;
  - `operations/cleanup.md`;
  - the slides, notes and guides;
  - `planning/`;
  - the `cd` commands students type.
- **The private repository refers to public paths too.** For example,
  `lab-solutions/lab-01/apply_solution.sh`. Update it in the same session.
- **Tooling:**
  - `audit.py` check 6 reads teaching guides from the new path;
  - check 8 reads the exam document from week 8;
  - the link check must still pass;
  - `to_artifact.py` is unaffected, because slides stay at `weeks/week-NN/slides.md`.
- **Decks.** Regenerate the claude.ai decks. Republish only the slides whose text names a
  moved path.
- **Record it.** Add decision D-72, revising D-12 on where the teaching guides live. Update
  the README tree, the syllabus's "Where things are", and `progress.md`.

## Verification (definition of done)

- **No stale paths.** A grep for `labs/lab-`, `exams/README`, `project/` and
  `weeks/week-NN/teaching-guide` finds nothing stale. Each surviving match is checked by
  hand.
- **Tests and checks pass:**
  - `audit.py` reports no problems;
  - `leakcheck.py` passes;
  - the application tests pass.
- **Every starter script resolves its paths.**
  - Run each with `bash -n`.
  - Echo-test the computed `APP_SRC`/`ROOT` of each from its new location. They cannot be run
    for real without a cloud project.
- **Every relative Markdown link resolves.**

## Left to the builder

- The exact wording of each README's three sections.
- Whether week 14's exam pointer is a link or a short excerpt (a link is preferred).
- Order of work.
