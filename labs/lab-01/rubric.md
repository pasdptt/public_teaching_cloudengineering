# Lab 1 — Rubric

**7.5% of the final grade.** Four bands, the same four used in every lab in this course.

| Band | Share |
|---|---|
| A. Working implementation | **35** |
| B. Conceptual explanation and experimental evidence | **40** |
| C. Reproducibility, security and resource handling | **15** |
| D. Communication | **10** |
| | **100** |

Read the shares before you start. **Explaining what happened is worth more than making it
work.** That is not a quirk of this lab; it is what the course is for.

---

## A · Working implementation — 35 marks

`FileJobStore` satisfies the `JobStore` contract.

| | Marks | Looks like |
|---|---|---|
| Excellent | 31–35 | All `-m lab01` tests pass **and** the default suite still passes. Implementation is compact and readable. Concurrency is handled with a lock held over both the in-memory state and the file. Writes are atomic. |
| Good | 24–30 | All `-m lab01` tests pass. Some roughness — re-reading the file on every call, a non-atomic write, or a lock held more broadly than needed. |
| Developing | 14–23 | Most tests pass. A contract violation remains: `get()` returns `None` instead of raising, a deleted job keeps its idempotency key, or `list_jobs` is ordered wrongly. |
| Limited | 0–13 | Does not run, or the persistence test does not pass — the one thing the exercise is about. |

The application must also run for real with `DOCAPP_JOBSTORE=file`. Passing the tests but
failing to start is Developing at best.

## B · Explanation and evidence — 40 marks

This is the largest band. Split across four pieces of work:

### B1 · Predictions, written before Part 3 (4 marks)
All three answered, with reasons. **Being wrong costs nothing.** Not committing to an answer,
or quietly editing a prediction after seeing the result, costs everything in this band.

### B1b · Continuous integration, Part 6 (2 marks)
Red run and green run both evidenced from the student's own pushes, and the four questions
answered. Full marks need question 4 to name something **specific** the pipeline cannot
catch — a deployment problem, a performance regression, an untested code path, a bad
configuration value — rather than "tests don't catch everything". This is the seed week 13
grows, so mark it for precision rather than length.

### B2 · Request trace and the process boundary (12 marks)
| | Looks like |
|---|---|
| Excellent | The trace names every hop and what it did. The three Part 2 answers are mechanistic: PID renumbering explained as a namespace, not "containers are isolated"; the port-publishing answer reasons about the boundary rather than quoting the flag; the `0.0.0.0` answer distinguishes "all interfaces in this container" from "all interfaces on a public machine" and sees why that is dangerous in the second case. |
| Good | Trace is complete; answers are correct but stay at the level of vocabulary rather than mechanism. |
| Developing | Trace has gaps, or an answer restates the question. A common one: "the container has its own kernel." |
| Limited | Description of the commands run, with no account of what they showed. |

### B3 · What survived, and why (10 marks)
The document/job asymmetry identified and explained. Full marks require the harder
distinction: the job record disappearing (state held **in memory**) is a *different* failure
from the containerised document disappearing (state held on storage that is **itself
disposable**). A submission that treats both as "it wasn't saved" has missed the point that
Lab 3 is built on.

Comparison against the student's own prediction, stated plainly, is required.

### B4 · The experiment (12 marks)
| | Looks like |
|---|---|
| Excellent | Table with conditions and units. Three runs per setting, variation acknowledged. Correctly identifies that throughput rises while per-request latency stays near the configured delay, and explains it in terms of concurrent waiting rather than faster work. Names a specific candidate limit at the saturation point **and** what they would measure to test it. Picks a real limitation from `measure.py --help` and connects it to their own setup. |
| Good | Data present and correct; explanation right but thin on the *why*; limitation named generically. |
| Developing | Single run per setting, or numbers reported without interpretation, or conflates throughput with latency. |
| Limited | No measurements, or numbers that cannot have come from the described setup. |

> **Fabricated measurements score zero for the whole lab** and are handled as academic
> misconduct. An experiment that failed, reported honestly, can still reach Excellent in B4
> if the reasoning about *why* it failed is sound.

## C · Reproducibility, security and resource handling — 15 marks

| | Marks | Looks like |
|---|---|---|
| Excellent | 13–15 | Someone else could reproduce every result from the submission alone. Cleanup performed **and verified**, with the verification output included. No credentials or personal paths in the submission. |
| Good | 10–12 | Reproducible with small gaps. Cleanup claimed and mostly evidenced. |
| Developing | 5–9 | Commands missing or implied. Cleanup asserted without evidence. |
| Limited | 0–4 | Not reproducible, or cleanup ignored. |

Nothing in this lab costs money. The habit is being graded, not the saving — from Lab 2
onwards the same band is about resources that bill.

## D · Communication — 10 marks

Clear, concise, honest. A reader can follow the reasoning without running anything. Length
is not a virtue: the 150-word explanation should be 150 words, not 600. Uncertainty stated
as uncertainty rather than dressed up as a conclusion earns marks here rather than losing
them.

---

## Rules that apply to every lab in this course

- **An unsuccessful experiment can earn full analysis credit** when the evidence is real and
  the reasoning is sound.
- **Fabricated evidence earns zero** and is an academic-integrity matter.
- **Screenshots alone are not evidence.** A screenshot may illustrate; the measurement must
  be reproducible — command, conditions, numbers.
- **No marks for spending more** credit, using more services, or choosing bigger instances.
  Where two designs meet the requirement, the cheaper one is the better answer and should
  say so.
- **Cleanup claimed but not verified does not earn the band C marks.**
- **AI assistance is permitted and must be disclosed.** Work you cannot explain does not earn
  marks, whoever wrote it — which is why band B is the largest one.

## Marking notes

Expected marking time: **15–25 minutes per student**. Bands A and C are largely mechanical —
run the tests, read the cleanup evidence. Band B is where the judgement is, and where the
time should go.

The full instructor guide, model answers and common-misconception list are in the private
repository at `lab-solutions/lab-01/`.
