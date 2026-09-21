# Cloud Computing: Principles and Practice

Course repository for a 15-week, 3-contact-hour undergraduate/early-graduate course on
cloud computing. The course teaches **cloud-agnostic concepts and architectural
reasoning**, using **Google Cloud Platform (GCP) as the practical workbench**.

It is not a vendor-certification course. Students should leave able to explain *why* a
deployment behaves as it does — not only to reproduce a sequence of console clicks.

> **Build status: Stage A (course blueprint) complete.**
> Teaching materials, labs, quizzes and application code are in progress.
> See [`planning/progress.md`](planning/progress.md) for exactly what exists,
> what has been validated, and what the next action is.

---

## Start here

| If you are… | Read |
|---|---|
| A student | [`course/syllabus.md`](course/syllabus.md), then [`operations/student-setup.md`](operations/student-setup.md) |
| The instructor, planning delivery | [`course/weekly-schedule.md`](course/weekly-schedule.md) and [`course/workload-budget.md`](course/workload-budget.md) |
| Reviewing the course design | [`course/learning-outcomes.md`](course/learning-outcomes.md) and [`course/assessment-plan.md`](course/assessment-plan.md) |
| Worried about cloud cost or access | [`operations/cloud-access-and-fallback.md`](operations/cloud-access-and-fallback.md) |
| Resuming an authoring session | [`planning/progress.md`](planning/progress.md) |

## Repository layout

```text
planning/      Decision log, open questions, authoring progress, calendar worksheet
course/        Syllabus, outcomes, weekly schedule, workload budget, assessment plan
weeks/         Per-week teaching guide + student notes (week-01 … week-15)
labs/          Six substantial labs (lab-01 … lab-06): brief, rubric, starter code
quizzes/       Seven short quizzes, student versions only
project/       Integrative project brief, milestones, rubric
application/   The single Python application the whole course builds on
infra/         Terraform configurations used from Lab 6 onwards
operations/    Student setup, cloud access & fallback, cost model, cleanup
```

## Instructor material is NOT in this repository

**This repository is public.** Quiz keys, lab solutions, grading guidance and pilot
evidence live in a separate private repository, expected as a sibling directory:

```text
GitLocal/
  cloudengineering/             <- this repo (public, student-facing)
  cloudengineering-instructor/  <- private (keys, solutions, delivery guide)
```

Placing answer keys in an `instructor/` subfolder of a public repo does not protect
them — the history is public even after deletion. See
[`operations/publishing-checklist.md`](operations/publishing-checklist.md).

## Course at a glance

- **Duration:** 15 weeks × 3 contact hours (90 min concepts · 30 min discussion/quiz · 60 min guided lab)
- **Independent work:** ~180 minutes per week, total, including reading and quiz prep
- **Assessment:** quizzes 20% · labs 45% · project 35% — no midterm or final exam
- **Cloud access:** local-only for weeks 1–3; GCP trial activated in week 4; a
  documented local fallback covers students without trial eligibility
- **Same standard for everyone**, undergraduate and graduate alike

## Licence and reuse

Teaching materials in this repository are intended for reuse by other instructors.
Licence terms are pending — see [`planning/open-questions.md`](planning/open-questions.md) (Q-07).
