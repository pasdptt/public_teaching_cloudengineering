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
| 3 | 20 | 160 | 0 | 180 | Lab 1 completion and write-up, **including Part 6 — setting up CI** (~20 min). Reading trimmed by 5 to pay for it. |
| 4 | 30 | 120 | 30 | 180 | "Other" = trial activation, billing alert setup, first cleanup verification. Lab 2 start is lighter to absorb this. |
| 5 | 25 | 155 | 0 | 180 | Lab 2 completion, including teardown verification. |
| 6 | 30 | 150 | 0 | 180 | Lab 3 first half. |
| 7 | 25 | 155 | 0 | 180 | Lab 3 completion + decision record. |
| 8 | 30 | 0 | 150 | 180 | **Midterm week.** No lab is open. Reading = re-reading the weeks 1–7 notes; "Other" = revision from your own Lab 1–3 write-ups and the practice questions. |
| 9 | 30 | 150 | 0 | 180 | Lab 4 first half (containerise and deploy). |
| 10 | 20 | 160 | 0 | 180 | Lab 4 load experiment and comparison write-up. Reading trimmed; the experiment is the learning. |
| 11 | 30 | 130 | 20 | 180 | "Other" = read the project brief and think about scope. Lab 5 start is sized to leave room. |
| 12 | 15 | 135 | 30 | 180 | **Tightest week.** Lab 5 completion + failure experiment (135) and the project proposal (30). Reading cut to 15 min — the week's reading is deliberately short and the proposal is deliberately brief. |
| 13 | 30 | 150 | 0 | 180 | **Lab 6, in one week** (D-67). Reading raised to 30: the notes carry what the halved concept block could not. |
| 14 | 15 | 105 | 60 | 180 | **Final-exam week.** Reading = the synthesis notes, which are the method for the peer review. Project (105). "Other" (60) = final-exam revision. |
| 15 | 0 | 150 | 30 | 180 | "Other" = demonstration preparation, final cleanup verification, reflection. |

**Every week totals 180 minutes.** Where a week carries an extra obligation — trial
activation, the project proposal, exam revision, setting up CI — something else was reduced by
the same amount. Nothing was added on top. When the teaching was cut to twelve weeks (D-66),
nothing was moved into the exam weeks' independent time except revision and the project, and
Lab 6 was cut to fit one week rather than squeezed (D-67).

---

## Lab envelopes

Labs 1–5 each span two weeks and may use **both** weeks' practical sessions (2 × 60 min
in class) and **both** weeks' homework budgets (2 × ~150 min). So a two-week lab has an
envelope of roughly:

> 120 minutes guided + 300 minutes independent = **~7 hours total**

That is the number a lab must fit inside, including reading its brief, making the
prediction, implementing, running the experiment, writing the explanation, and tearing
down. A lab whose estimate exceeds it is cut down, not shipped with a warning.

**Lab 6 is a one-week lab** in week 13: 40 min guided + 150 min independent = **~3.2 hours**,
less than half the two-week envelope. It fits because it reuses Labs 2–5's components, adds
no new application behaviour, and since D-67 supplies the bootstrap — federation pool,
deployer identity, state bucket — as a script, so the student's time goes on the environment
differences, the gate, and the teardown, which are what is assessed. Its due date is the start
of week 14, so a student may use the weekend before the final exam; the exam week's budget
still gives Lab 6 nothing, on purpose.

---

## The project does not add a second implementation load

No lab is open after week 13. The project's time is the same lab-sized budget, and no more.
Across weeks 11–15 the project gets roughly:

| Source | Minutes |
|---|---|
| Week 11 — read brief, scope | 20 |
| Week 12 — proposal | 30 |
| Week 13 — design review (contact time) | ~4 per group |
| Week 14 — independent work, alongside final-exam revision | 105 |
| Week 15 — independent work before the demonstration | 150 |
| Week 14 — peer review (contact time) | 50 |
| **Total** | **~6 hours** |

**That is about 3.5 hours less than before the calendar was compressed (D-66), and the
project was simplified by the same amount rather than left to absorb it.** The remedy
`decisions.md` D-28 named in advance — *reduce the experiment requirements to one experiment*
— has been applied: the project now runs **one** experiment and designs, but does not run, a
second (D-69). It remains workable only because the project inherits a working delivery
pipeline and a `dev`/`prod` Terraform configuration from Lab 6, so its "reproducible
deployment" deliverable is satisfied by reuse rather than by new work.

If a pilot shows the project is still squeezed, the next remedy is to **drop the 10× cost
point** from the cost model, not to extend a week or to move work into the exam weeks. Record
whichever happens in `planning/decisions.md`.

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
| Quiz marking (~10 students, short answers) | 30–45 min | 6 times |
| Exam marking (~10 scripts, written answers) | 3–4 h | twice, weeks 8 and 14 |
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
- Week 12's combination of Lab 5 and the proposal proves unworkable in practice — the
  first remedy is to let the proposal be presented orally at the week 13 design review instead
  of written, not to shorten Lab 5's analysis.
- **Lab 6 does not fit one week.** This is the lab most changed by the compression (D-67) and
  the least tested: it was a 6.3-hour lab and is now a 3.2-hour one. Watch it in the first
  delivery. First remedy: make Part 3's "three things deliberately the same" the only written
  answer in that part, and drop the cost estimate in Part 6 to the per-project/per-account
  question alone. Never remedy it by moving Lab 6 work into week 14, which is exam week.
- **Exam revision spills into lab time.** If students report that week 8 or week 14 revision
  needed more than its allocation, the exam is asking for recall it should not — the same rule
  as for quizzes, and the fix is to the paper, not the budget.
- **CI setup in week 3 overruns its 20 minutes.** Likely causes are repository permissions or
  a student without a GitHub account. Fix the account problem in week 1, not week 3.
