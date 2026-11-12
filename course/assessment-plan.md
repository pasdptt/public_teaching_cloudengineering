# Assessment plan

| Component | Weight | Count | Individual? |
|---|---|---|---|
| Quizzes | **10%** | 6 | Yes |
| Labs | **30%** | 6 | Yes |
| Project | **30%** | 1 | Individual or pair, with individual accountability |
| Midterm exam | **15%** | 1 (week 8) | Yes |
| Final exam | **15%** | 1 (week 14) | Yes |
| | **100%** | | |

The same required work, outcomes and criteria apply to undergraduate and graduate students
(A-09). A midterm and a final examination were added when the teaching was compressed to
twelve weeks; that superseded A-10's "no exams" and D-02's weights (D-66, D-68). **The weights
above are a default, adopted so work could proceed, and are the instructor's to change** —
`planning/audit.py` checks only that they sum to 100% and that the lab weight divides evenly
across six labs.

---

## Quizzes — 10%

Six quizzes of **10–15 minutes**, in weeks 2, 4, 6, 9, 11, 13, taken during the
discussion block of the session. They do not extend contact time.

### What a quiz covers

Only outcomes **already taught and practised**. Never material from the same day's lecture,
and never something first encountered in a lab that has not yet been completed.

| Quiz | Week | Covers material from weeks | Outcomes |
|---|---|---|---|
| 1 | 2 | 1 | CLO-1, CLO-2 (intro) |
| 2 | 4 | 1–3 | CLO-1, CLO-2, CLO-3 (intro) |
| 3 | 6 | 3–5 | CLO-3, CLO-4 (intro) |
| 4 | 9 | 5–7 | CLO-1, CLO-2, CLO-4 |
| 5 | 11 | 7, 9, 10 | CLO-5, CLO-6 (intro) |
| 6 | 13 | 10–12 | CLO-5, CLO-6; CLO-7 and CLO-9 via their threads only |

There is no Quiz 7. It sat in week 14, which is now the final exam; its questions became the
final exam's practice set (D-70), handed out in class before week 14.

Quiz papers and the practice set are kept in the instructor repository and printed for the
room, so no question is readable before it is asked (D-71).

Each quiz's opening line states the weeks it draws on, so students can prepare honestly
inside the 30-minute reading budget.

**One case needs care.** Quiz 6 sits in week 13, the same session in which declarative
infrastructure, environments and cost models are first taught. It therefore assesses those
outcomes **only through the threads students have already been living with**: CLO-7 through
the cleanup and resource-handling routine practised since Lab 2, and CLO-9 through the CI
workflow running on their pushes since week 3. It must **not** assess Terraform, environment
management or cost-model material from that day's lecture. The conceptual content of CLO-7
and CLO-9 is assessed in Lab 6, in the final exam and in the project.

### Question style

- Short scenarios: "a request from X reaches Y but not Z — name the most likely cause and
  the one check that would confirm it."
- Diagram interpretation: annotate where a boundary is crossed, or where state lives.
- Measurement interpretation: here is a latency-vs-load curve; what is the limiting factor,
  and what would you measure next?
- Short explanations, two to four sentences.

**Not used:** service-name recall, pricing trivia, console menu paths, "which GCP product
is equivalent to AWS X", or anything answerable by memorising a comparison table.

### Marking

Instructor keys (private repo) carry, for every question: the expected answer, the
reasoning, the common misconceptions that earn partial credit, the partial-credit
allocation, and the expected time to answer.

**Quiz scores are normalised before weighting.** Each quiz is converted to a percentage of
its own maximum, the six percentages are averaged, and that average is multiplied by 10%.
A 12-mark quiz and an 18-mark quiz therefore count equally.

**Missed quizzes:** policy is the instructor's to set (see `planning/open-questions.md`).
Dropping the single lowest quiz is safe for every outcome: each of CLO-1 … CLO-7 appears in at
least two quizzes **or** in a quiz and an exam, CLO-8 is not quiz-assessed at all, and CLO-9
appears in Quiz 6 only through its thread. No outcome's evidence base depends on one quiz.

---

## Labs — 30%

Six labs, equally weighted at **5% each**. Individual submission (D-17). Labs 1–5 span two
weeks each; **Lab 6 is a one-week lab in week 13** (D-67), due at the start of week 14.

### Rubric bands — the same four for every lab

| Band | Share | What earns the marks |
|---|---|---|
| Working implementation | **35%** | The required behaviour actually works, verifiably |
| Conceptual explanation and experimental evidence | **40%** | The prediction, the measurement, and an explanation that accounts for the result |
| Reproducibility, security and resource handling | **15%** | Reproducible steps; least-privilege identity; no credentials in the submission; resource inventory; **verified** cleanup |
| Communication | **10%** | Clear, concise, honest; a reader can follow the reasoning |

Explanation and evidence outweigh working code. This is the point of the course and
students are told so in the syllabus.

### Rules that apply to every lab

- **An unsuccessful experiment can still earn full analysis credit** when the evidence is
  real and the reasoning is sound. Ending up with "I predicted X, observed Y, and here is
  why my model was wrong" is a good submission.
- **Fabricated evidence earns zero** for the lab and is treated as academic misconduct.
  This is the one hard line.
- **Screenshots alone are not evidence.** A screenshot may illustrate, but the measurement
  must be reproducible: the command or configuration, the conditions, and the numbers.
- **No marks for spending more.** Not for more services, not for more credit, not for a
  bigger instance. Where two designs meet the requirement, the cheaper one is the better
  answer and should say so.
- **Cleanup is graded, and claiming it is not the same as verifying it.** The
  reproducibility band requires evidence that resources are gone — a listing, not an assertion.

### Submission template

Every lab submits the same short structure, so marking is recognition and not archaeology:

1. Prediction (written before implementing)
2. What you did — commands and configuration, not prose narration
3. Measurements, with conditions and units
4. Explanation — including where the prediction was wrong
5. Resource inventory and cleanup verification
6. AI-assistance disclosure (per the policy under review, Q-05)

### Late work

Instructor policy. The design constraint: labs 1–5 span two weeks and feed the next lab, so
a late lab compounds. A per-lab grace window is preferable to an open late policy.

---

## Examinations — 30%

Two written examinations of **120 minutes**, sat in the room during the session: the
**midterm in week 8** (15%) and the **final in week 14** (15%). Format, coverage and allowed
materials are in [`exams/README.md`](../exams/README.md); the papers and their keys are in the
instructor repository and never in this one.

| Exam | Week | Covers weeks | Outcomes |
|---|---|---|---|
| Midterm | 8 | 1–7 | CLO-1, CLO-2, CLO-3, CLO-4; CLO-5 foundations |
| Final | 14 | 1–13, weighted towards 9–13 | CLO-2, CLO-5, CLO-6, CLO-7, CLO-9; one design-defence question for CLO-8 |

The exams follow the quiz rules, at greater length: scenarios, diagrams and measurements to
interpret, never recall of service names, prices or console paths. **An exam that needs a
separate study session beyond its week's revision allowance is asking for recall, and is
rewritten** — the same rule `course/workload-budget.md` applies to quizzes. Neither exam
asks for anything first met in a lab that had not been completed by the exam week.

**Why exams and not more quizzes.** The compression removed one quiz slot and the week 13–14
project time. Two exams give the course individual, invigilated evidence for every outcome —
including CLO-7 and CLO-9, whose only other individual evidence is lab work done outside the
room — without adding contact time, since they occupy weeks that no longer teach.

---

## Project — 30%

Released week 11 · proposal week 12 · design review week 13 · built weeks 13–15 (week 14
shared with the final exam) · demonstrated week 15.

**The project inherits the delivery path.** Its reproducible-deployment and environment
requirements are met by reusing the Terraform configuration and pipeline built in Lab 6, not
by building new ones (D-28). A project proposing to build its own pipeline from scratch has
been scoped wrong, and the week-13 design review exists partly to catch that.

### Required deliverables

| Deliverable | Where it is assessed |
|---|---|
| Architecture diagram and concise decision record | Architecture & reasoning |
| Reproducible deployment **through the Lab 6 pipeline**, and a verified cleanup path — reuse, not rebuild (D-28) | Reproducibility, security & cost |
| A named `dev`/`prod` split, with every difference between them accounted for | Reproducibility, security & cost |
| One experiment, **run** — performance or controlled failure/recovery, the student's choice | Experiments & interpretation |
| The other experiment, **designed but not run** — prediction, method, bounds, and the result that would change a decision (D-69) | Experiments & interpretation |
| Measured results with stated limitations | Experiments & interpretation |
| Cost model tied to a stated workload, with explicit assumptions | Reproducibility, security & cost |
| Conceptual migration discussion — what transfers, what is a commitment to this provider | Architecture & reasoning |
| Demonstration and architecture defence | Communication & individual understanding |

No second cloud account is required. The migration discussion is analysis, not deployment.

### Rubric

| Band | Share |
|---|---|
| Architecture and reasoning | **25%** |
| Functional implementation | **20%** |
| Experiments and interpretation | **25%** |
| Reproducibility, security and cost | **20%** |
| Communication and individual understanding | **10%** |

### Individual and pair projects

Groups are **one or two students; two is the maximum** (A-11).

- The **minimum project is scoped for one person** within the weekly budget. A pair is not
  required to build twice as much — no mandatory extra feature exists solely to occupy a
  pair, because that would make working alone structurally worse.
- A pair submits a short **contribution record**: who did what, agreed by both.
- **Both members answer an individual question** during the defence, about a decision they
  personally made. The communication and individual-understanding band is scored per
  student.
- A pair may receive different marks. The shared artefact bands are usually common; the
  individual band and the defence are not.

### Cloud access in a pair

Covered in `operations/cloud-access-and-fallback.md`, but the assessment-relevant rules:
the project is owned by one named student's trial account, the partner receives
**named-user access with narrowly scoped roles**, credentials are never shared, and the
submission states who owns the project, whose credit paid for it, who performed cleanup,
and how the partner's access was revoked afterwards. Those statements are marked under the
reproducibility and security band.

### Week 15 timing

Up to **12 minutes per group** including questions. Ten individual projects therefore fit
in 120 minutes, leaving ~60 minutes for transitions, synthesis, cleanup verification and
reflection. If the cohort forms five pairs instead, the same envelope gives more time per
group, not a longer session.

---

## Grade composition check

| Component | Weight |
|---|---|
| 6 quizzes, normalised and averaged | 10.0% |
| 6 labs × 5% | 30.0% |
| Project | 30.0% |
| Midterm exam | 15.0% |
| Final exam | 15.0% |
| **Total** | **100.0%** |

| Outcome | Assessed in |
|---|---|
| CLO-1 | Q1, Q2, Q4, midterm, project defence |
| CLO-2 | Q1, Q2, Q4, Lab 1, Lab 4, midterm, final |
| CLO-3 | Q2, Q3, Lab 2, midterm |
| CLO-4 | Q3, Q4, Lab 3, midterm, project |
| CLO-5 | Q5, Q6, Lab 4, Lab 5, final, project |
| CLO-6 | Q5, Q6, Lab 4, Lab 5, final, project |
| CLO-7 | Q6 (cleanup thread), Lab 6, final, project cleanup |
| CLO-9 | Q6 (CI thread), Lab 1 Part 6, Lab 6, final, project |
| CLO-8 | Final (design-defence question), project defence |

Every outcome has at least two independent pieces of evidence, and at least one that is not
a quiz.

---

## Academic integrity and AI assistance

The policy is under academic review (Q-05). The design already assumes the following and
the rubrics are built around it:

- Assistance is permitted for code and prose; **disclosure is required** in every submission.
- Individual understanding is verified directly — in quizzes and exams taken in class, in lab
  explanations that reference the student's own measurements, and in an oral question
  during the project defence.
- **Work a student cannot explain does not earn marks**, regardless of authorship. This
  needs no separate detection mechanism; it falls out of a rubric that weights explanation
  above implementation.
- Fabricated measurements are misconduct whether produced by a student or generated.
