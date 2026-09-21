# Authoring progress

**Resume from this file.** It records what exists, what has been validated and at what
level, and the single next concrete action. Do not restart the design from the brief.

Last updated: **2026-09-21** · Current stage: **A and B complete → C not started**

---

## Next concrete action

> **Author Lab 2 and weeks 4–5** (compute and networking). Before writing any steps, verify
> on a real unupgraded trial account that: one `e2-micro` in `us-central1` is genuinely free;
> an ephemeral external IP behaves as `operations/cost-model.md` §2 claims; and the whole lab
> can be created and destroyed inside the free tier. Then write the lab to the Lab 1 template
> — same section list, same four rubric bands, same predict → implement → measure → explain
> cycle.
>
> Lab 2 also needs `operations/cleanup.md`, which is a placeholder until a lab creates
> something billable.

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

**Free-tier-first policy added 2026-09-21 (D-19 … D-22)**, on instruction to minimise cost.
Consequences: Q-03 resolved to Firestore on idle-cost grounds (D-20); Lab 2 uses an ephemeral
IP and deletes rather than stops its VM (D-21); ceilings cut from $30/$75 to $5/$15 (D-22);
`us-central1` became a condition rather than a preference (D-18). Expected spend per student
for the whole course is now **under $1**, with the external IP in Lab 2 (~$0.04) as the only
reliably charged item. Four further pricing sources were fetched and cited (R-09 … R-12), so
`operations/cost-model.md` now carries **verified rates** rather than empty cells.

**Facts verified 2026-09-21 by fetching official sources:**
- Free Trial: $300 credit, 90 days, new users only, payment method required for identity
  verification, workloads stop at expiry, upgrade to paid is manual. (R-01, R-02)
- Always Free tier limits for Compute Engine, Cloud Storage, Cloud Run, Pub/Sub, Logging. (R-01)
- `hashicorp/google` Terraform provider is on the 8.x line as of 2026-09-04. (R-03)

**Still deliberately absent:** the `e2-micro` on-demand rate. Two Compute Engine pricing
pages were fetched and neither returned usable E2-family figures. It turned out not to
matter — under D-19 that VM is free-tier — and no plausible-looking number was invented to
fill the gap. See R-04.

---

## Stage B — teaching foundation · COMPLETE

| Artefact | Status | Validation |
|---|---|---|
| `application/docapp/` — 11 modules, stdlib only | done | **EXECUTED** — runs, serves traffic, verified by curl |
| `application/tests/` — 47 standard tests | done | **EXECUTED** — all pass |
| `application/tests/test_lab01_filejobstore.py` — 14 acceptance tests | done | **EXECUTED** — fail as intended until the student implements `FileJobStore` |
| `application/tools/measure.py` | done | **EXECUTED** — produced real measurements at concurrency 1 and 4 |
| `application/Dockerfile` + `.dockerignore` | done | **REVIEWED, NOT BUILT** — no container runtime was available. Build on Apple Silicon and Intel before week 2. |
| `application/README.md`, `samples/` | done | REVIEWED |
| `operations/check_environment.py` | done | **EXECUTED** — 7 pass, 2 warn, 0 fail on the authoring machine |
| `operations/student-setup.md` | done | **REVIEWED** — Windows and macOS paths **not executed on those platforms** |
| `labs/lab-01/README.md` + `rubric.md` | done | REVIEWED |
| Instructor solution + teaching notes (private repo) | done | **EXECUTED** — reference `FileJobStore` passes all 14 lab01 tests and the 47 standard tests |
| `weeks/week-01…03/` teaching guides + student notes | done | REVIEWED |

**Gate passed?** Partly, and the gap is named rather than papered over:

- ✅ The application runs end-to-end and its tests pass.
- ✅ Lab 1's exercise has a verified reference solution.
- ⚠️ **Not verified on Windows or macOS.** Authoring happened on Linux. Both platform paths
  are reviewed, not executed.
- ⚠️ **The Dockerfile has never been built.** Lab 1 Part 2 depends on it.
- ⚠️ **Novice completion time is an estimate only.** ~2 h guided + ~5 h independent. Nobody
  has been timed. `course/workload-budget.md` says why that number is worth little until a
  pilot happens.

### Real measurements recorded this session

From `tools/measure.py` against the local server, `DOCAPP_PROCESSING_DELAY_MS=200`, 12
requests, one run each, client and server on the same host (a Linux container, **not** a
student laptop):

| Concurrency | Wall time | Throughput | p50 | p95 |
|---|---|---|---|---|
| 1 | 2.489 s | 4.82 req/s | 208.3 ms | 209.0 ms |
| 4 | 0.623 s | 19.26 req/s | 207.4 ms | 208.4 ms |

**Measured, not illustrative.** Filed in the private repo as pilot evidence. Deliberately
**not** printed in the student lab — producing their own numbers is the exercise.

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
