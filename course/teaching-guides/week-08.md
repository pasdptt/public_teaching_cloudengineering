# Week 8 — Teaching guide: Consolidation, Quiz 4 and the lab clinic

| | |
|---|---|
| **Outcomes** | CLO-1, CLO-2, CLO-4 (Quiz 4); CLO-1 to CLO-4 practised, not assessed |
| **Assessment** | **Quiz 4** — weeks 5–7, 15 min, in the session. Moved here from week 9 (D-74) |
| **Practical** | Practice questions · trial and cost check · lab clinic. **No new material** |
| **Prep time** | Re-read the practice key: ~20 min. Session: ~30 min |

> **Changed 2026-11-21 (D-74).** This week was the midterm, a 120-minute exam worth 15%. The
> midterm was removed: the final in week 14 is now cumulative, worth 25%, with about half its
> marks on weeks 1–7. Quiz 4 moves here from week 9. It already covers weeks 5–7, and in this
> week it sits after Lab 3 closes, on a day with no lecture to compete with. The time the exam
> used goes to practice questions in the final's style, and to a longer clinic.

## Session objectives

1. Every student sits Quiz 4 under the same conditions.
2. Every student finds, on paper, one thing from weeks 1–7 they cannot yet explain, while
   there is time to fix it before the final.
3. Every student states, out loud and from their own billing page, how much trial credit and
   how many trial days they have left.
4. Nobody starts week 9 with an unresolved Lab 3 problem or a container that will not build.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| **Quiz 4** | 15 | Weeks 5–7, on paper. The paper is in the instructor repository |
| Quiz 4, the answers | 15 | Collect the papers first, then go through each question |
| **Practice questions** | 50 | Weeks 1–7 in the final's four question kinds, in pairs, not marked |
| Break | 10 | |
| **Trial and cost check** | 20 | Every student, their own billing page, in the room |
| **Lab clinic** | 70 | Outstanding Lab 3 issues · Lab 4 pre-flight. No new content |

**180 minutes exactly.** Nothing after the quiz is examined or required by a later lab that is
not already in that lab's brief.

---

## Quiz 4 (15 min) and its answers (15 min)

- **The paper and key are in the instructor repository** (`quizzes/quiz-04.md`,
  `quiz-keys/quiz-04-key.md`). They are unchanged by the move: they were written for weeks 5–7,
  after Labs 2 and 3.
- **Go through the answers straight after collecting the papers.** In week 9 there was no time
  for this. Here there is, and the quiz's value is mostly in the feedback. Do the mechanism for
  each question, not the marks. Hand the marked scripts back in week 9.

## Practice questions (50 min)

**Four questions** on weeks 1–7, one of each kind in [`weeks/week-14/exams.md`](../../weeks/week-14/exams.md):
trace, interpret, predict and explain, choose and defend. Each is 5 marks, the size of one
question on the final. They are in the instructor repository, `exam-papers/week-08-practice.md`,
with a key beside it. They are the first half of the final practice set. Print one per pair.

- **Twelve minutes a question:** ten in pairs, in writing, then two minutes of answers from the
  room. Ask for the mechanism, and let a wrong prediction with a good mechanism stand as a good
  answer. That is how the final marks it. Record how long pairs actually take: it is the first
  evidence of whether the final is the right length.
- **Three of the four are about their own system**: the job store from Lab 1, the VM from Lab 2
  with the Lab 3 code on it, and the decision record from Lab 3. Tell students in week 7 to
  bring their Lab 1–3 write-ups.
- **Different scenarios from the final.** The real paper must not repeat them.
- **End with one minute of writing:** *the one thing from weeks 1–7 I could not explain today.*
  It goes on the top of their revision sheet, and it is what the week 8 reading budget is for.

## Trial and cost check (20 min)

Week 8 is roughly a third of the way through the 90-day trial window. It is the
last comfortable moment to find a student whose credit is draining.

Every student opens **their own** billing page and says three things, out loud:

1. Credit remaining.
2. Days remaining, and the date the trial ends. Check it against `planning/calendar-worksheet.md`
   — the trial must still be alive in week 15.
3. Anything currently running, and why. **The expected answer is "nothing".**

A student who finds something running has found something useful. Ask how it survived the
Lab 2 or Lab 3 teardown — the same treatment week 15 gives it (D-53). Then delete it, together,
and verify it with `operations/cleanup.md`.

## Lab clinic (70 min)

Not a lecture, and not new material. Two lists on the board:

- **Lab 3 left-overs.** Anyone whose Lab 3 submission recorded a problem they could not solve.
  The class issue log first, then one-to-one.
- **Lab 4 pre-flight.** `docker build` the application locally and run it. Lab 4 Part 0 needs a
  working local build, and a student who discovers in week 9 that their container runtime has
  stopped working loses the week. This is the week-1 environment check, rerun for one tool.

Students with neither may leave. Say so: the session ends when they are ready for week 9, not
at 180 minutes.

## Links

- Exam format: [`weeks/week-14/exams.md`](../../weeks/week-14/exams.md)
- Assessment weights: [`course/assessment-plan.md`](../assessment-plan.md)
- Previous week: [`week-07`](week-07.md) · Next week: [`week-09`](week-09.md)
