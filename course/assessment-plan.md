# Assessment plan

| Component | Weight | Count | Individual? |
|---|---|---|---|
| Quizzes | **20%** | 7 | Yes |
| Labs | **45%** | 6 | Yes |
| Project | **35%** | 1 | Individual or pair, with individual accountability |
| | **100%** | | |

The same required work, outcomes and criteria apply to undergraduate and graduate students
(A-09). There is no midterm and no final examination (A-10).

---

## Quizzes — 20%

Seven quizzes of **10–15 minutes**, in weeks 2, 4, 6, 8, 10, 12, 14, taken during the
discussion block of the session. They do not extend contact time.

### What a quiz covers

Only outcomes **already taught and practised**. Never material from the same day's lecture,
and never something first encountered in a lab that has not yet been completed.

| Quiz | Week | Covers material from weeks | Outcomes |
|---|---|---|---|
| 1 | 2 | 1 | CLO-1, CLO-2 (intro) |
| 2 | 4 | 1–3 | CLO-1, CLO-2, CLO-3 (intro) |
| 3 | 6 | 3–5 | CLO-3, CLO-4 (intro) |
| 4 | 8 | 5–7 | CLO-1, CLO-2, CLO-4 |
| 5 | 10 | 7–9 | CLO-5, CLO-6 (intro) |
| 6 | 12 | 9–11 | CLO-5, CLO-6; CLO-7 and CLO-9 via their threads only |
| 7 | 14 | 11–13 | CLO-6, CLO-7, CLO-8, CLO-9 |

Each quiz's opening line states the weeks it draws on, so students can prepare honestly
inside the 30-minute reading budget.

**One case needs care.** Quiz 6 sits in week 12, the same session in which declarative
infrastructure, environments and cost models are first taught. It therefore assesses those
outcomes **only through the threads students have already been living with**: CLO-7 through
the cleanup and resource-handling routine practised since Lab 2, and CLO-9 through the CI
workflow running on their pushes since week 3. It must **not** assess Terraform, environment
management or cost-model material from that day's lecture. The conceptual content of CLO-7
and CLO-9 is assessed in Quiz 7, in Lab 6 and in the project.

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
its own maximum, the seven percentages are averaged, and that average is multiplied by 20%.
A 12-mark quiz and an 18-mark quiz therefore count equally.

**Missed quizzes:** policy is the instructor's to set (see `planning/open-questions.md`).
Dropping the single lowest quiz is safe for CLO-1 … CLO-7, each of which appears in at
least two quizzes — that redundancy is deliberate. **CLO-8 and CLO-9 appear in Quiz 7 only**
(CLO-9 also in Quiz 6, but only through its thread). Their primary evidence is the project
defence and Lab 6 respectively, so no outcome loses its evidence base if one quiz is dropped.

---

## Labs — 45%

Six labs, equally weighted at **7.5% each**. Individual submission (D-17). Labs 1–5 span two
weeks each; **Lab 6 spans weeks 12–13** (D-24), sharing its second week with the start of the
project.

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

## Project — 35%

Released week 10 · proposal week 11 · built weeks 13–15 (week 13 shared with the end of
Lab 6) · demonstrated week 15.

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
| One performance experiment | Experiments & interpretation |
| One controlled failure/recovery experiment | Experiments & interpretation |
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
| 7 quizzes, normalised and averaged | 20.0% |
| 6 labs × 7.5% | 45.0% |
| Project | 35.0% |
| **Total** | **100.0%** |

| Outcome | Assessed in |
|---|---|
| CLO-1 | Q1, Q2, Q4, project defence |
| CLO-2 | Q1, Q2, Q4, Lab 1, Lab 4 |
| CLO-3 | Q2, Q3, Lab 2 |
| CLO-4 | Q3, Q4, Lab 3, project |
| CLO-5 | Q5, Q6, Lab 4, Lab 5, project |
| CLO-6 | Q5, Q6, Q7, Lab 4, Lab 5, project |
| CLO-7 | Q6 (cleanup thread), Q7, Lab 6, project cleanup |
| CLO-9 | Q6 (CI thread), Q7, Lab 1 Part 6, Lab 6, project |
| CLO-8 | Q7, project defence |

Every outcome has at least two independent pieces of evidence, and at least one that is not
a quiz.

---

## Academic integrity and AI assistance

The policy is under academic review (Q-05). The design already assumes the following and
the rubrics are built around it:

- Assistance is permitted for code and prose; **disclosure is required** in every submission.
- Individual understanding is verified directly — in quizzes taken in class, in lab
  explanations that reference the student's own measurements, and in an oral question
  during the project defence.
- **Work a student cannot explain does not earn marks**, regardless of authorship. This
  needs no separate detection mechanism; it falls out of a rubric that weights explanation
  above implementation.
- Fabricated measurements are misconduct whether produced by a student or generated.
