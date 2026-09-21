# Authoring progress

**Resume from this file.** It records what exists, what has been validated and at what
level, and the single next concrete action. Do not restart the design from the brief.

Last updated: **2026-09-21** · Current stage: **A complete → B not started**

---

## Next concrete action

> **Build the course application** (`application/`): a minimal Python document/job-processing
> service that runs locally with synchronous behaviour only — submit a synthetic input,
> store it on local disk, request processing, poll status, read the result. No storage
> service, no queue, no container yet. Then write Lab 1 against it and time a novice run.

Stage B is deliberately narrow: the application and Lab 1 become the template every later
lab reuses, so they are validated before scope expands.

---

## Validation levels used in this repository

| Level | Meaning |
|---|---|
| **EXECUTED** | Actually run in this environment, output observed |
| **REVIEWED** | Read and checked for consistency, not executed |
| **NEEDS CLOUD** | Requires a real GCP account to verify; must not be claimed as working |
| **NEEDS INSTRUCTOR** | Requires a pilot run, a policy decision, or institutional information |

Nothing in this repository may be described as classroom-validated until an instructor has
piloted the labs under the intended access model.

---

## Stage A — course blueprint · COMPLETE

| Artefact | Status | Validation |
|---|---|---|
| `README.md` | done | REVIEWED |
| `.gitignore` / `.gitattributes` | done | REVIEWED |
| `planning/decisions.md` | done | REVIEWED |
| `planning/open-questions.md` | done | REVIEWED |
| `planning/progress.md` | this file | — |
| `planning/calendar-worksheet.md` | done, unfilled by design | NEEDS INSTRUCTOR (Q-01) |
| `planning/audit.py` | done | **EXECUTED** — passes clean |
| `course/syllabus.md` | done | REVIEWED |
| `course/learning-outcomes.md` | done | REVIEWED |
| `course/weekly-schedule.md` | done | REVIEWED |
| `course/workload-budget.md` | done | REVIEWED |
| `course/assessment-plan.md` | done | REVIEWED |
| `course/concept-to-gcp-map.md` | done | REVIEWED |
| `course/references.md` | done | REVIEWED — every URL fetched 2026-09-21 |
| `operations/cloud-access-and-fallback.md` | done | REVIEWED; trial terms verified 2026-09-21 |
| `operations/cost-model.md` | method + ceilings done; **per-lab figures deliberately absent** | NEEDS CLOUD for rates |
| `operations/publishing-checklist.md` | done | REVIEWED |
| `operations/student-setup.md`, `operations/cleanup.md` | placeholders only | — |
| `weeks/week-01…15/`, `labs/lab-01…06/`, `quizzes/`, `project/` | placeholders recording scope and constraints | — |
| Private instructor repo scaffolded | done | EXECUTED (`git init`) |

**Mechanical audit (`python3 planning/audit.py`) passes**, checking: all 11 relative links
resolve · all 15 weekly workload rows sum to exactly 180 · assessment weights total 100%
and 6 × 7.5% = 45% · 80 files scanned, no answer-key or credential-shaped content · all
eight CLOs present in the assessment plan. Run it before every commit.

**One inconsistency was found and fixed during the audit:** Quiz 6 (week 12) had been
mapped to CLO-4 and to CLO-7 conceptual material taught in that same session. It now
assesses CLO-5 and CLO-6, and touches CLO-7 only through the cleanup thread students have
practised since Lab 2.

**Facts verified 2026-09-21 by fetching official sources:**
- Free Trial: $300 credit, 90 days, new users only, payment method required for identity
  verification, workloads stop at expiry, upgrade to paid is manual. (R-01, R-02)
- Always Free tier limits for Compute Engine, Cloud Storage, Cloud Run, Pub/Sub, Logging. (R-01)
- `hashicorp/google` Terraform provider is on the 8.x line as of 2026-09-04. (R-03)

**Deliberately not done in Stage A:** no specific dollar figures for VM/storage/queue
pricing were recorded, because the official per-SKU pages could not be read reliably in
this session. Inventing them would be worse than their absence. `operations/cost-model.md`
states the method, the quantities, and where the rate goes; rates are filled in Stage C
from `cloud.google.com/pricing/list` with the date of retrieval.

---

## Stage B — teaching foundation · NOT STARTED

| Artefact | Status |
|---|---|
| `application/` minimal local service | not started |
| `application/` tests (meaningful behaviour, not implementation mirrors) | not started |
| `operations/student-setup.md` (Windows + macOS paths) | not started |
| `labs/lab-01/` brief, rubric, starter | not started |
| `weeks/week-01/`, `weeks/week-02/`, `weeks/week-03/` | not started |
| Novice workload estimate for Lab 1 | not started |

Gate before Stage C: Lab 1 runs end-to-end locally on both platform paths, and its
estimated novice completion time fits the Week 2–3 budget.

---

## Stage C — progressive development · NOT STARTED

Labs 2–6, weeks 4–15, quizzes 1–7 and keys, project package, `infra/`.
Operational guidance (cost, cleanup, resource inventory) is authored **with** each cloud
exercise, never afterwards.

## Stage D — audit and package · NOT STARTED

Coverage, sequencing, assessment fairness, timing, trial restrictions, cost assumptions,
cleanup, student/instructor separation.

---

## Standing constraints for every future session

1. Do not re-ask about class size, TA support, OS mix, install access, or maximum group
   size. See `decisions.md` §A.
2. Never invent a benchmark number, a cost, a deployment result, or a student completion
   time. Label illustrative data `ILLUSTRATIVE — NOT MEASURED`.
3. Never commit an answer key, solution or grading guide to this repository.
4. Creating course material does not authorise provisioning billable cloud resources.
   Validate locally; list cloud checks that need a real environment.
5. If a task exceeds the 180-minute weekly budget, **simplify the task** — do not silently
   add homework.
