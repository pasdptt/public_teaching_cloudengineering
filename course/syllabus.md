# Cloud Computing: Principles and Practice — Syllabus

> Dates are not yet fixed. Weeks are relative; the instructor fills the calendar from
> `planning/calendar-worksheet.md` before the course runs.

| | |
|---|---|
| **Credit format** | 15 weeks × 3 contact hours |
| **Audience** | Junior/senior CS undergraduates and early graduate students, one shared course |
| **Class size** | ~10 students, one instructor, no teaching assistant |
| **Cloud platform** | Google Cloud Platform, funded by the $300 / 90-day new-user trial |
| **Assessment** | Quizzes 20% · Labs 45% · Project 35% — **no midterm, no final exam** |
| **Independent work** | ~180 minutes per week, total |

---

## What this course is

Cloud platforms are usually taught as a tour of products. This course does the opposite.
For every topic we start with the problem that made the abstraction necessary, then the
mechanism that solves it, then the tradeoffs it forces — and only then the GCP service
that implements it.

The test of success is not that you can deploy something. It is that when a deployment
behaves strangely, you can say **why**.

You will build one application across the whole semester. It starts as a Python program on
your own machine and ends as a deployed, scaled, asynchronous, reproducible cloud service
that you can measure, break deliberately, explain, and tear down completely.

## What this course is not

- It is not certification preparation. We do not memorise product names.
- It is not a Kubernetes administration course. Orchestration is covered conceptually.
- It is not a course in which "it worked" is the goal. Evidence and explanation carry more
  marks than a working deployment (see the rubric balance below).
- It does not require a second cloud account. Provider independence is taught by analysis.

## Prerequisites

Some programming experience and basic comfort with a Linux-style shell (`cd`, `ls`, running
a command, reading an error). Python is used for the labs and starter code is supplied.

**No prior experience is assumed** with cloud platforms, networking, operating systems
internals, databases, Docker, or distributed systems. The concepts you need from those
areas — processes, ports, HTTP, DNS, IP addressing, persistence, basic concurrency — are
taught briefly at the point where the course actually needs them.

---

## Learning outcomes

By the end of the course you will be able to:

1. Explain cloud characteristics, service models and the shared-responsibility boundary,
   and apply that boundary to a specific incident.
2. Compare virtual machines, containers and managed/serverless execution, and justify a
   choice while naming what it gives up.
3. Trace a request through a cloud application's network and identity boundaries, and
   predict the effect of changing an access rule before testing it.
4. Select storage and data services using durability, consistency, access pattern, latency
   and cost — and state what the choice makes hard later.
5. Design a small application using stateless execution, external state, asynchronous work
   and horizontal scaling.
6. Measure behaviour under load and controlled failure, and explain the result with
   evidence, including its limitations.
7. Reproduce and completely remove an environment using scripts and Terraform, verifying
   that nothing billable remains.
8. Defend an architecture on security, reliability, cost and provider dependence.

Full, assessable wording and the outcome→assessment map: `learning-outcomes.md`.

---

## How the semester runs

### A typical session (3 hours)

| Block | Time | What happens |
|---|---|---|
| Concepts | ~90 min | Instruction and worked examples — the mechanism, not the menu |
| Discussion | ~30 min | Architecture exercise, prediction discussion, **or** a quiz |
| Guided practical | ~60 min | You start the lab with the instructor present |

Quizzes replace part of the discussion block. They never add contact time.

### The lab cycle

Every lab follows the same four steps:

> **predict → implement → measure → explain**

You write down what you expect **before** you run it. A wrong prediction that you can
explain is worth more than a right one you cannot.

### Labs

Six labs, each normally spanning two weeks, all building on the same application:

1. **Local foundations** — run and inspect the application, trace a request, examine
   process and container boundaries, reason about state and failure.
2. **Compute and networking** — deploy on a small VM, configure narrow access, trace the
   network path, explain the identity and responsibility boundaries.
3. **State and storage** — move application state out of the compute instance into object
   storage and one managed data service; justify the design.
4. **Managed execution and elasticity** — deploy the containerised service, run a bounded
   load experiment, and compare latency, throughput, scaling and operational burden
   against the VM.
5. **Asynchrony and resilience** — introduce a queue, handle retries and duplicate
   delivery, make processing idempotent, and inspect evidence from a controlled failure.
6. **Reproducibility and economics** — complete a Terraform skeleton, recreate the
   environment, explain a cost estimate, then verify teardown.

### Project

Released in week 10, proposed in week 11, built in weeks 13–15, demonstrated in week 15.
You extend the course application to meet a small set of workload, security, reliability
and cost requirements, then defend the architecture.

Alone or in a pair — **two students maximum**. The minimum project is designed to be
achievable by one person within the weekly budget. A pair is not expected to build twice
as much; both members answer individual questions.

---

## Assessment

| Component | Weight | Form |
|---|---|---|
| Quizzes (7 × ~10–15 min, weeks 2, 4, 6, 8, 10, 12, 14) | **20%** | Individual, in class, during the discussion block |
| Labs (6, substantial) | **45%** | Individual submission |
| Integrative project | **35%** | Individual or pair, with individual accountability |
| | **100%** | |

Quiz scores are normalised before the category weight is applied, so quizzes of slightly
different length do not distort the total.

### How labs are marked

| Band | Share |
|---|---|
| Working implementation | 35% |
| Conceptual explanation and experimental evidence | 40% |
| Reproducibility, security and resource handling (including verified cleanup) | 15% |
| Communication | 10% |

Read that balance carefully: **explaining what happened is worth more than making it
work.** An experiment that failed can still earn full analysis credit if the evidence and
reasoning are sound.

Three things earn no marks: screenshots presented as the only evidence; spending more
cloud credit or deploying more services than the task needs; and cleanup you claim but do
not verify. One thing earns zero and is an academic-integrity matter: **fabricated
measurements**.

### How the project is marked

Architecture and reasoning 25% · functional implementation 20% · experiments and
interpretation 25% · reproducibility, security and cost 20% · communication and individual
understanding 10%.

Detail: `assessment-plan.md`, and the rubric in `project/rubric.md`.

---

## Cloud access, cost and your own money

**You will not be charged if you follow the course instructions.** But you are responsible
for understanding why, so this section is not boilerplate.

- Weeks 1–3 are **local only**. Do not activate a cloud trial before week 4 — activating
  early wastes days of a 90-day window that has to last to the end of term.
- In week 4 you activate the Google Cloud Free Trial: $300 of credit, valid 90 days.
  A payment method is required for identity verification. **Charging requires you to
  manually upgrade to a paid account, which this course never asks you to do.** When the
  trial ends, workloads stop rather than bill you. (Verified 2026-09-21 — re-check the
  current terms at signup; see `course/references.md`.)
- The $300 is a **ceiling, not a target**. Course labs are designed to use a small
  fraction of it. Marks are never awarded for spending more.
- **Budget alerts are notifications, not a spending cap.** An alert does not stop anything.
- Every cloud lab ends with a teardown step and a **teardown verification** step. Some
  resources keep costing money after the compute is stopped — disks, static addresses,
  buckets, images, logs. Verifying is part of the mark.

**If you cannot get the trial** — no eligibility, no suitable payment method, or you have
used it before — tell the instructor in week 1, not week 4. A documented local/emulated
fallback path covers the same assessed principles. You are **not** disadvantaged in
grading, and you must **not** create a duplicate account to regain eligibility.

Full detail, including what the fallback cannot faithfully reproduce:
`operations/cloud-access-and-fallback.md`.

## Security expectations

Real credentials, service-account keys and tokens never go into submitted work or into any
repository. Application identities get narrowly scoped permissions, never project-owner.
Shared passwords are not acceptable, including between project partners — use named access.
These are graded under the reproducibility/security band, and a leaked credential in a
submission is treated as a serious error regardless of whether anything was exploited.

## Equipment

A Windows or macOS laptop on which you can install Python and container tooling. Week 1
includes an environment check that you must actually run — it exists to find problems while
there is still time to fix them. Platform-specific setup lives in
`operations/student-setup.md`; the lab instructions themselves are the same on both platforms.

## Use of AI assistance

A policy is under academic review (`planning/open-questions.md`, Q-05). The working
expectation: assistance is permitted for code and prose, **disclosure is required**, and
your individual understanding is checked directly — in quizzes, in lab explanations, and in
an oral question about a decision you made in your project. Work you cannot explain does
not earn marks, whoever or whatever wrote it.

## Where things are

`course/` design documents · `weeks/` per-week notes · `labs/` lab briefs and starter code ·
`quizzes/` · `project/` · `application/` the course application · `infra/` Terraform ·
`operations/` setup, cloud access, cost and cleanup.

Answer keys and solutions are not in this repository.
