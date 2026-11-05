# Calendar worksheet

The schedule in `course/weekly-schedule.md` is written as **relative weeks 1–15**. This
worksheet is the one place real dates are entered, and the one place the GCP trial
arithmetic is re-checked after they are.

Status: **unfilled — awaiting Q-01.** Do not date the syllabus from anywhere else.

---

## 1. Fill in the teaching calendar

| Week | Date of session | Notes (holiday, deadline, break) |
|---|---|---|
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |
| 4 |  | ← trial activation week |
| 5 |  |  |
| 6 |  |  |
| 7 |  |  |
| 8 |  | ← **midterm exam** · trial check (no teaching) |
| 9 |  |  |
| 10 |  |  |
| 11 |  | ← project brief released |
| 12 |  | ← project proposal due, with Lab 5 |
| 13 |  | ← last teaching week · Lab 6 (one week) · design review |
| 14 |  | ← **final exam** · Lab 6 due · peer review (no teaching) |
| 15 |  | ← demonstrations + final submission |

Twelve teaching weeks (1–7, 9–13), and three that do not teach (8, 14, 15) — D-66. If the
institution fixes its own exam weeks, put the midterm and final there and move **only** the
exam; the teaching sequence does not depend on which week the exam occupies, as long as the
midterm falls between Lab 3 and Lab 4 and the final after Lab 6.

Also record: add/drop deadline · withdrawal deadline · final grade submission deadline ·
any institutional holiday that cancels a session · any week where the room or duration differs.

---

## 2. Re-run the trial-window check

The Free Trial is **90 days from the student's own signup date**, not from the start of
term (verified 2026-09-21, see `course/references.md` R-01). Students are instructed **not
to activate early** precisely so this window can be aimed.

Fill in:

```text
(a) Date of the Week 4 session (trial activation)         = ____________
(b) Trial expiry for a student who activates on (a)       = (a) + 90 days = ____________
(c) Date of the Week 15 session (demonstrations)          = ____________
(d) Final cleanup-verification deadline                   = ____________
(e) Slack remaining                                       = (b) − (d) = ______ days
```

**Decision rule:**

| (e) | Action |
|---|---|
| ≥ 14 days | Acceptable. Record the result here and in `decisions.md`. |
| 0 – 13 days | Too tight. A single missed week consumes it. Choose one remedy below. |
| < 0 days | Plan does not work as written. A remedy is mandatory. |

**Remedies, in order of preference:**

1. **Move activation later.** Labs 2 needs cloud access from week 4, but Lab 2 can be
   re-sequenced one week later if weeks 1–3 absorb more local work. Cheapest fix.
2. ~~Compress the cloud phase.~~ **Already applied** (D-66, D-67): Lab 6 is a one-week lab
   in week 13, so the last billable lab work ends at the start of week 14.
3. **Institutional billing account** (Q-02), which removes the 90-day constraint entirely.
4. **Move the demonstration earlier** and use week 15 only for cleanup, reflection and
   written submission — demonstrations do not require live cloud resources if the
   experiments were recorded as evidence, though a live teardown demonstration does.

Do **not** remedy this by telling students to create a second account to regain
eligibility. That is against Google's terms and is not an option the course offers.

---

## 3. Check quiz and milestone placement against the dated calendar

Quizzes sit in weeks 2, 4, 6, 9, 11, 13; the exams in weeks 8 and 14 (D-66). After dating:

- [ ] No quiz falls in a week whose session is cancelled by a holiday.
- [ ] Every quiz assesses only outcomes taught in or before the **previous** week — re-check
      if any week was moved.
- [ ] The project proposal (week 12) does not land in the same week as a quiz **and** a lab
      deadline. It currently shares week 12 with the Lab 5 completion; the 180-minute budget
      for that week already accounts for this (`course/workload-budget.md`), but a shifted
      calendar can break it.
- [ ] Week 15 has the full 3 hours available; demonstrations need up to 120 minutes of it.
- [ ] Weeks 8 and 14 each have the full 3 hours in one room, for a 120-minute written exam. If
      the institution requires exams in a separate exam period, record where they move and
      what the freed session is used for.

---

## 4. Record the outcome

Once filled, copy a two-line summary into `planning/decisions.md` as decision **D-19**
("Semester dates fixed; trial window verified with N days of slack") and update
`planning/progress.md`.
