# Workload budget

**Student independent work: ~180 minutes per week, total.** That figure includes reading,
quiz preparation, lab work, project work — everything outside the three contact hours.

This is a hard envelope, not an aspiration. The design rule when something does not fit is
**simplify the task**, never silently add homework.

---

## How these estimates were produced, and what they are worth

> **These are design estimates for a novice student. None of them has been validated by
> observation.** No lab has been piloted. No student has been timed. A script that runs in
> 40 seconds tells you nothing about how long a first-time student takes to understand what
> it did — which is the part the course is actually asking for.
>
> Each lab, when authored, carries two separate numbers: an **estimated novice completion
> time** and, once a pilot happens, an **observed pilot time**. They are never merged, and
> the second one is empty until someone has actually run it.

Assumptions behind the estimates: a student meeting the stated prerequisites and no more;
working with the supplied starter code; not blocked by an unresolved setup problem; and
reading at roughly 200 words per minute on unfamiliar technical material.

Setup failures are the largest risk to these numbers, which is why the week-1 environment
check exists and why unresolved setup issues are an instructor problem, not a homework problem.

---

## Standard weekly allocation

| Activity | Minutes |
|---|---|
| Reading and preparation | 30 |
| Lab or project work | 150 |
| **Total** | **180** |

Quiz preparation is **inside** the 30 minutes of reading, not added to it. The quizzes are
short, they cover material already taught and practised, and they are designed so that
doing the reading *is* the preparation. If a quiz requires a separate study session, the
quiz is wrong and gets rewritten.

---

## Week-by-week budget

| Wk | Reading | Lab / project | Other | Total | Notes |
|---|---|---|---|---|---|
| 1 | 30 | 120 | 30 | 180 | "Other" = environment check completion and troubleshooting. Deliberately light: this week's job is to find setup problems. |
| 2 | 30 | 150 | 0 | 180 | Lab 1 first half. Reading doubles as Quiz 1 prep. |
| 3 | 25 | 155 | 0 | 180 | Lab 1 completion and write-up. |
| 4 | 30 | 120 | 30 | 180 | "Other" = trial activation, billing alert setup, first cleanup verification. Lab 2 start is lighter to absorb this. |
| 5 | 25 | 155 | 0 | 180 | Lab 2 completion, including teardown verification. |
| 6 | 30 | 150 | 0 | 180 | Lab 3 first half. |
| 7 | 25 | 155 | 0 | 180 | Lab 3 completion + decision record. |
| 8 | 30 | 150 | 0 | 180 | Lab 4 first half (containerise and deploy). |
| 9 | 20 | 160 | 0 | 180 | Lab 4 load experiment and comparison write-up. Reading trimmed; the experiment is the learning. |
| 10 | 30 | 130 | 20 | 180 | "Other" = read the project brief and think about scope. Lab 5 start is sized to leave room. |
| 11 | 15 | 135 | 30 | 180 | **Tightest week.** Lab 5 completion + failure experiment (135) and the project proposal (30). Reading cut to 15 min — the week's reading is deliberately short and the proposal is deliberately brief. |
| 12 | 30 | 150 | 0 | 180 | Lab 6 is a single-week lab but reuses existing components; no new application code. |
| 13 | 20 | 160 | 0 | 180 | Project implementation. |
| 14 | 15 | 145 | 20 | 180 | "Other" = peer review of another group's work. |
| 15 | 0 | 150 | 30 | 180 | "Other" = demonstration preparation, final cleanup verification, reflection. |

**Every week totals 180 minutes.** Where a week carries an extra obligation — trial
activation, the project proposal, peer review — something else was reduced by the same
amount. Nothing was added on top.

---

## Two-week labs

Labs 1–5 each span two weeks and may use **both** weeks' practical sessions (2 × 60 min
in class) and **both** weeks' homework budgets (2 × ~150 min). So a two-week lab has an
envelope of roughly:

> 120 minutes guided + 300 minutes independent = **~7 hours total**

That is the number a lab must fit inside, including reading its brief, making the
prediction, implementing, running the experiment, writing the explanation, and tearing
down. A lab whose estimate exceeds it is cut down, not shipped with a warning.

Lab 6 is a single week: 60 min guided + ~150 min independent = **~3.5 hours**. It is sized
that way because it reuses Labs 2–5's components and adds no new application behaviour.

---

## The project does not add a second implementation load

Weeks 13–15 contain **no new lab**. The project's 150 minutes per week is the same 150
minutes that would otherwise have gone to a lab. Across weeks 10–15 the project gets
roughly:

| Source | Minutes |
|---|---|
| Week 10 — read brief, scope | 20 |
| Week 11 — proposal | 30 |
| Weeks 13–15 — independent work | ~455 |
| Weeks 13–15 — supervised contact time | ~180 |
| **Total** | **~11 hours** |

The project **extends** the existing application and reuses the existing Terraform. A
project that requires rewriting the application from scratch has been scoped wrong, and
the week-13 design review exists partly to catch that.

**Pairs do not get a doubled scope.** The minimum project is feasible for one person
within this budget. Pair membership buys depth or a more ambitious experiment, not a
mandatory second feature. Adding features purely to occupy a pair would make solo work
structurally disadvantageous, which decision A-11 rules out.

---

## Instructor workload — estimated separately

These are **not** part of the student budget and are also unvalidated estimates.

| Activity | Estimated time | Frequency |
|---|---|---|
| Session preparation (first delivery) | 3–4 h | per week |
| Session preparation (subsequent deliveries) | 1–1.5 h | per week |
| Quiz marking (~10 students, short answers) | 30–45 min | 7 times |
| Lab marking (~10 students, rubric-based) | 2.5–4 h | 6 times |
| Project design review | 15 min per group | week 13 |
| Project marking incl. defence notes | 30–45 min per group | week 15 |
| Cloud/cost monitoring and student access support | 30 min | per week, weeks 4–15 |

**Design constraints this imposes, given no TA:**

- Rubrics are analytic and reused across labs, so marking is recognition rather than
  invention.
- Objective functional checks are automated where a script can honestly check them
  (does the endpoint respond, is the bucket gone, does the retry path deduplicate).
  Everything conceptual stays with the instructor — that is the part that carries 40% of
  the lab mark and cannot be delegated to a checker.
- Submission templates are short and structured, so a marker reads evidence rather than
  hunting for it.
- Lab troubleshooting uses a **shared** routine: a visible checkpoint list, a common-errors
  section in every lab, and a class-visible issue log — so the same problem is solved once,
  not ten times.

If lab marking consistently exceeds 4 hours, the submission template is too long. That is
a fix to the template, not a reason to mark faster.

---

## Review triggers

Re-open this budget if any of the following is observed:

- A lab's pilot time exceeds its estimate by more than 25%.
- More than two students report a week exceeding 180 minutes.
- Setup problems consume more than 30 minutes of any week after week 2.
- Week 11's combination of Lab 5 and the proposal proves unworkable in practice — the
  first remedy is to move the proposal deadline to week 12, not to shorten Lab 5's analysis.
