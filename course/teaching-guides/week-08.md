# Week 8 — Teaching guide: Midterm examination

| | |
|---|---|
| **Outcomes** | CLO-1, CLO-2, CLO-3, CLO-4; CLO-5 foundations (exam evidence) |
| **Assessment** | **Midterm exam** — 120 min, 60 marks, weeks 1–7 (`weeks/week-08/exams.md`) |
| **Practical** | Trial and cost check · lab clinic. **No new material** |
| **Prep time** | Paper and key: ~6 h first delivery, ~2 h subsequently. Session: ~30 min |

> **Added 2026-11-05 (D-66).** The course teaches in twelve of its fifteen weeks. This week is
> the mid-semester exam, placed at the one point where an exam can sit between labs rather than
> inside one: Lab 3 closed in week 7 and Lab 4 opens in week 9.

## Session objectives

1. Every student sits the midterm under the same conditions.
2. Every student states, out loud and from their own billing page, how much trial credit and
   how many trial days they have left.
3. Nobody starts week 9 with an unresolved Lab 3 problem or a container that will not build.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| **Midterm examination** | 120 | Written, in the room. Start on time; collect at 120 minutes exactly |
| Break | 10 | |
| **Trial and cost check** | 20 | Every student, their own billing page, in the room |
| **Lab clinic** | 30 | Outstanding Lab 3 issues · Lab 4 pre-flight. No new content |

**180 minutes exactly.** The two blocks after the exam are support, not teaching: nothing in
them is examined or required by a later lab that is not already in that lab's brief.

---

## The exam (120 min)

- **The paper is in the instructor repository** (`exam-papers/midterm.md`), with its key.
  It does not exist yet; writing it is the main preparation this week needs. Write it to
  `weeks/week-08/exams.md`: 60 marks, the four question kinds, nothing that needs recall.
- **Check every question against the rule.** Weeks 1–7 and Labs 1–3 only. A question that
  needs managed execution, queues or Terraform is out of scope, however natural it feels.
- **Use their own systems.** At least one question should ask about the VM each student ran in
  Lab 2 or the decision record they wrote in Lab 3 — the quizzes have shown that questions about
  a student's own work are the hardest to answer without understanding.
- **Allowed:** one A4 sheet of handwritten notes, both sides. No devices. Say this in week 7,
  and again in the week 7 notes.
- **Mark within a week.** The feedback is most useful before Lab 4's prediction is written,
  and marking ten 60-mark scripts is roughly three to four hours (`course/workload-budget.md`).

## Trial and cost check (20 min)

The midterm week is roughly a third of the way through the 90-day trial window. It is the
last comfortable moment to find a student whose credit is draining.

Every student opens **their own** billing page and says three things, out loud:

1. Credit remaining.
2. Days remaining, and the date the trial ends. Check it against `planning/calendar-worksheet.md`
   — the trial must still be alive in week 15.
3. Anything currently running, and why. **The expected answer is "nothing".**

A student who finds something running has found something useful. Ask how it survived the
Lab 2 or Lab 3 teardown — the same treatment week 15 gives it (D-53). Then delete it, together,
and verify it with `operations/cleanup.md`.

## Lab clinic (30 min)

Not a lecture, and not new material. Two lists on the board:

- **Lab 3 left-overs.** Anyone whose Lab 3 submission recorded a problem they could not solve.
  The class issue log first, then one-to-one.
- **Lab 4 pre-flight.** `docker build` the application locally and run it. Lab 4 Part 0 needs a
  working local build, and a student who discovers in week 9 that their container runtime has
  stopped working loses the week. This is the week-1 environment check, rerun for one tool.

Students with neither may leave. Say so: the session ends when they are ready for week 9, not
at 180 minutes.

## Links

- Exam format: [`weeks/week-08/exams.md`](../../weeks/week-08/exams.md)
- Assessment weights: [`course/assessment-plan.md`](../assessment-plan.md)
- Previous week: [`week-07`](week-07.md) · Next week: [`week-09`](week-09.md)
