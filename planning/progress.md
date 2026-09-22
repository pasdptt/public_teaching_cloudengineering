# Authoring progress

**Resume from this file.** It records what exists, what has been validated and at what
level, and the single next concrete action. Do not restart the design from the brief.

Last updated: **2026-09-22** · Current stage: **A and B complete → C in progress** · tagged **v0.3.0**

---

## Next concrete action

> **Author Lab 5 and weeks 10–11** (queues, duplicates, idempotency, resilience). The seam is
> already in place: `docapp/queue.py` has the `Queue` Protocol and `InlineQueue`, and
> `build_queue` has the branch comment where Pub/Sub goes. `config.py`'s `queue_backend`
> currently accepts only `("inline",)` and must gain the new value there as well.
>
> Write it to the Lab 3/Lab 4 template — same section list, same four rubric bands, same
> predict → implement → measure → explain cycle. The assessed idea is **idempotency**, not the
> queue product; `service.run_job` already returns early for terminal jobs, and Lab 5's job is
> to make students prove that early return is load-bearing rather than decorative.
>
> Two things to get right before writing steps:
> - **A subscription with no consumer retains messages and bills for storage.** Teardown must
>   name it explicitly, and `operations/cleanup.md` already has the row.
> - Lab 5 reuses Lab 4's Cloud Run service, which Lab 4 tears down. Decide whether week 10
>   redeploys from the same image or whether Lab 4's teardown should keep the registry — and
>   record the decision either way.

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
and 6 × 7.5% = 45% · 153 files scanned, no answer-key or credential-shaped content · all
nine CLOs present in the assessment plan · **all 9 authored session plans sum to exactly 180
contact minutes** (check 6, added 2026-09-22). Run it before every commit.

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

## Stage C — progressive development · IN PROGRESS

### DevOps added to the curriculum, 2026-09-22 (D-23 … D-28)

On instruction to cover DevOps for cloud engineers. A **re-sequencing**, not an addition on
top — 15 weeks and 180 min/week are fixed.

- **CLO-9** added: build and operate an automated delivery path across environments, and
  explain what each gate protects. Nine outcomes now.
- **CI is a thread from week 3**, not a week-12 topic. Lab 1 gained Part 6.
- **Lab 6 became a two-week lab (weeks 12–13)**: infrastructure and environments, then the
  delivery pipeline. The week-13 synthesis lecture moved to week 14.
- **GitHub Actions + keyless Workload Identity Federation.** No service-account key exists
  anywhere in this course.
- **Two environments, `dev` and `prod`**, from one configuration and two variable files.
- **Every week still totals exactly 180 minutes** (verified by `audit.py`). Week 3 gave up
  5 minutes of reading for CI setup; week 13 splits 110/50 between Lab 6 and the project.
  The project lost ~1.5 h, recorded as a deliberate trade in D-28 because it now inherits a
  working pipeline instead of building one.

### Authored this session

| Artefact | Status | Validation |
|---|---|---|
| `.github/workflows/ci.yml` | done | **EXECUTED** — YAML parsed and asserted; every command it runs was executed locally and passes |
| `.github/workflows/deploy.yml` (Lab 6 starter, TODOs) | done | **EXECUTED** — YAML parsed; the `needs: test` gate and the `contents:read`/`id-token:write` permissions asserted programmatically |
| `labs/lab-01/` Part 6 + rubric band B1b | done | REVIEWED |
| `labs/lab-02/README.md` + `rubric.md` | done | REVIEWED |
| `labs/lab-02/starter/` — 7 scripts | done | **EXECUTED** — `bash -n` clean on all 7; the config, project-id, free-tier-region and firewall-range guard rails each triggered correctly in isolation |
| `labs/lab-06/README.md` + `rubric.md` | done | REVIEWED |
| `infra/` — Terraform, 4 `.tf` + 2 tfvars examples | done | **HCL PARSES** (verified with a parser). `terraform validate`/`plan` **NOT run** — no binary, no project. Provider schemas and argument names are reviewed, not verified. |
| `operations/cleanup.md` | done | REVIEWED |
| `weeks/week-04`, `week-05` guides + notes | done | REVIEWED |
| `weeks/week-12…14` placeholders | corrected to the new structure | — |
| Course docs updated for CLO-9 and the re-sequence | done | **audit.py passes**, now checking CLO-1…9 |

### Lab 3 authored (2026-09-22)

| Artefact | Status | Validation |
|---|---|---|
| `tests/contracts.py` — shared backend contract | done | **EXECUTED** — the storage and job-store rules now live once and run against every backend; suite grew 47 → **62 tests**, all passing |
| `docapp/gcs_storage.py`, `docapp/firestore_jobstore.py` (student stubs) | done | **EXECUTED** — parse, import lazily, and raise actionable errors; wired into both factories without breaking the zero-dependency local path |
| `tests/test_lab03_cloud_backends.py` | done | **EXECUTED** — 22 tests **skip cleanly** with nothing configured, so they never run or bill by accident |
| `requirements.txt` — pinned clients | done | **MEASURED** — the two libraries add ~63 MB to site-packages (storage ~39, firestore ~24), which is what justified using them rather than hand-rolling the REST API against the 0.5 GiB Artifact Registry allowance |
| `labs/lab-03/README.md` + `rubric.md` | done | REVIEWED |
| `weeks/week-06`, `week-07` guides + notes | done | REVIEWED |
| Instructor reference backends (private repo) | done | **NOT EXECUTED** — reviewed against google-cloud-storage 3.x and google-cloud-firestore 2.x; no project was available |

### Lab 4 authored (2026-09-22)

| Artefact | Status | Validation |
|---|---|---|
| `labs/lab-04/README.md` + `rubric.md` | done | REVIEWED |
| `labs/lab-04/starter/` — `lib.sh`, `config.env.example`, 7 scripts | done | **EXECUTED** — `bash -n` clean on all 8; all **seven guard rails triggered correctly in isolation** (missing config, unedited project id, non-free-tier region, `MIN_INSTANCES != 0`, `MAX_INSTANCES > 10`, non-numeric max, and the all-valid path) |
| `tools/instances.py` — counts the instances answering a burst | done | **EXECUTED** — run against a live local server at concurrency 10 and 30 |
| `tools/measure.py` — repeatable `--header` (D-29) | done | **EXECUTED** — run with and without headers; existing behaviour unchanged |
| `tests/test_two_instances_disagree.py` — 3 tests | done | **EXECUTED** — suite grew 62 → **65 tests, all passing** |
| `docapp/app.py` — listen backlog raised to 128 | done | **EXECUTED** — see below |
| `Dockerfile` — `/app/data` created and chowned (D-33) | done | **REVIEWED, NOT BUILT** — still no container runtime in any authoring session |
| `weeks/week-08`, `week-09` guides + notes | done | REVIEWED |
| `operations/cleanup.md` — Lab 4 rows, service-account row, registry check | done | REVIEWED |
| `audit.py` check 6 — session plans sum to 180 | done | **EXECUTED** — found 6 real defects, see below |

**Nothing in Lab 4 has been run against Google Cloud.** No `gcloud` command in it has been
executed, no image has been built, no service deployed. Every command is reviewed against
current documentation and none is verified. Specific things a pilot must confirm
(**NEEDS CLOUD**): that `gcloud auth print-identity-token` is accepted by a private Cloud Run
service without an explicit `--audiences`; that the roles a student picks in
`04-runtime-identity.sh` are sufficient and minimal; that the Part 3 fan-out reproduces often
enough to teach with; and that a 15-minute idle really scales to zero.

**Two real bugs were found and fixed while authoring, neither by running the lab:**

1. **The server's listen backlog was the stdlib default of 5**, so roughly a third of a
   30-request concurrent burst was refused by the operating system before Python saw it.
   Invisible at the concurrency Labs 1 and 3 use, and it would have corrupted the local
   baseline Lab 4 compares against. Raised to 128 in `docapp/app.py`; the same burst now
   completes 60/60 with zero failures. **Measured before and after.**
2. **The container image could not have started on Cloud Run.** `/app` is owned by root, the
   process runs as `appuser`, and `LocalStorage` calls `os.makedirs` at startup. Fixed in the
   Dockerfile (D-33) — but still not built, so this is reasoning, not evidence.

### A course-wide defect found and fixed (D-32)

Adding the session-plan check to `audit.py` immediately failed **six of the seven authored
teaching guides**: weeks 1, 2, 3, 5, 6 and 7 had session plans summing to 190–220 minutes
against a fixed 180-minute contact block. Only week 4 was correct.

Nothing had caught it — the existing workload check covers independent study only. All six
were rebalanced by trimming concept blocks; **the 60-minute practical and every quiz were
left untouched**, because the last block is what actually gets cut on the day. Section
headings carrying their own durations were corrected to match, and
`course/weekly-schedule.md`'s envelope sentence now accounts for the break rather than
implying 180 minutes of teaching plus a break.

### Still to author

Labs 5 · weeks 10–14 teaching content · quizzes 1–7 and keys · the project package ·
instructor solutions for Labs 2, 4, 5, 6. Operational guidance is authored **with** each
cloud exercise, never afterwards.

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
