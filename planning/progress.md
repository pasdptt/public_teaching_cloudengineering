# Authoring progress

**Resume from this file.** It records what exists, what has been validated and at what
level, and the single next concrete action. Do not restart the design from the brief.

Last updated: **2026-09-22** · Current stage: **A and B complete → C in progress** · tagged **v0.3.0**

---

## Next concrete action

> **Author week 15, then the assessment package.**
>
> **Week 15 is small but is not nothing**, and its placeholder currently *contradicts*
> `course/weekly-schedule.md`: the placeholder carries the standard 90/30/60 session plan,
> while the schedule specifies demonstrations up to 120 min · synthesis ~30 · cleanup and
> reflection ~30. The schedule is right. `audit.py` does not catch this because it skips
> files still marked "not yet authored" — worth fixing the file rather than the check.
>
> Week 15 needs: a demonstration running order and timing discipline for up to ten
> presentations, the individual-question protocol for pairs (A-11 requires individual
> accountability), the transfer discussion, and the in-session verified teardown, which is the
> last chance to catch an orphaned resource before the trial lapses.
>
> Then, in order of how much is blocked on them:
> 1. **Quizzes 1–7 and their keys** — seven files here, seven in the private repo. The largest
>    remaining gap, and nothing depends on them.
> 2. **The project package** — `project/brief.md`, `milestones.md` and `rubric.md` are
>    placeholders and are referenced from weeks 10, 13, 14 and 15. The brief is released in
>    week 10, so it is the more urgent of the two.
> 3. Instructor solutions for Labs 2, 4 and 6.

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
nine CLOs present in the assessment plan · **all 14 authored session plans sum to exactly 180
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

### Lab 5 authored (2026-09-22)

| Artefact | Status | Validation |
|---|---|---|
| `labs/lab-05/README.md` + `rubric.md` | done | REVIEWED |
| `labs/lab-05/starter/` — `lib.sh`, `config.env.example`, 7 scripts | done | **EXECUTED** — `bash -n` clean on all 8; the new message-retention guard triggered correctly on all five cases (empty, non-numeric, too short, too long, valid) |
| `docapp/threadqueue.py` — supplied local broker (D-35) | done | **EXECUTED** — async delivery, reproducible duplicates, bounded retry and dead-lettering, all covered by 9 new tests |
| `docapp/pubsub_queue.py` — student stub, two TODOs | done | **EXECUTED** — parses, imports lazily, raises actionable errors |
| `docapp/app.py` — `POST /tasks/process` push endpoint | done | **EXECUTED** — exercised over a real socket by 4 tests |
| `config.py` / `queue.py` / `wiring.py` — three queue backends | done | **EXECUTED** — factory now takes the whole Config; all call sites updated |
| `tests/test_threadqueue.py` — 9 tests | done | **EXECUTED** — suite grew 65 → **74 tests, all passing** |
| `tests/test_lab05_queue.py` — 16 acceptance tests | done | **EXECUTED** — 14 offline tests **fail against the stub and pass against the instructor reference** (D-39); the 2 real-Pub/Sub tests skip cleanly with nothing configured |
| `requirements.txt` — `google-cloud-pubsub==2.41.0` | done | **MEASURED** — adds only ~6 MB on top of storage + firestore, because grpc is already there |
| `weeks/week-10`, `week-11` guides + notes | done | REVIEWED |
| `operations/cleanup.md` — subscription rows, teardown ordering | done | REVIEWED |
| Instructor reference (private repo) | done | **PARTLY EXECUTED** — `decode_push_envelope` verified against all 14 offline tests; `PubSubQueue.submit` reviewed against google-cloud-pubsub 2.x and **not run** |

**The cloud half of Lab 5 has not touched Google Cloud.** No topic, subscription or
deployment was created. Specific things a pilot must confirm (**NEEDS CLOUD**): that the push
subscription's two IAM grants are as the lab describes; that dead-lettering fires at the
configured attempt count; that the retry intervals are wide enough to produce a readable
timeline in Part 5; and that `PubSubQueue.submit` works as the private reference has it.

**Measured while authoring:** adding `google-cloud-pubsub` to a tree that already has
`google-cloud-storage` and `google-cloud-firestore` costs about **6 MB**, not the ~40 MB the
package looks like in isolation, because grpc is already pulled in by Firestore. The marginal
cost of a dependency depends on what is already there. Recorded in `requirements.txt`, along
with the fact that the earlier 63 MB Linux figure and today's 80 MB macOS/arm64 figure for
the first two packages disagree — a platform difference, not worth chasing, and not silently
overwritten.

### Week 12 authored, and the infrastructure gap closed (2026-09-22)

| Artefact | Status | Validation |
|---|---|---|
| `infra/main.tf` — rewritten, 14 resources (D-40, D-41) | done | **VALIDATED** — see below |
| `infra/variables.tf`, `outputs.tf`, both tfvars examples | done | **VALIDATED** — every `validation` block passes for both environments, and bad values are rejected |
| `infra/README.md` — status, provenance table, guard rails | done | REVIEWED |
| `labs/lab-06/README.md` + `rubric.md` — updated for Labs 4–5 | done | REVIEWED |
| `weeks/week-12` guide + notes | done | REVIEWED |

**The Terraform gap carried since the DevOps session is closed.** `tofu validate` **passes**
against the real `hashicorp/google` provider, which resolved to **8.3.0** under the `~> 8.0`
pin. Every resource type, argument name and type is now checked rather than reviewed; `fmt` is
clean; both variable files pass validation and deliberately bad values were confirmed to be
rejected.

**Caveat, stated rather than glossed:** validated with **OpenTofu 1.12.6**, not Terraform.
Homebrew no longer ships Terraform (BUSL), and OpenTofu is the drop-in D-03 already nominated.
Same HCL, same provider — a meaningful check, and not the same claim as "terraform validate
passes" (D-42). **`plan` and `apply` have still never been run**; they need a project and
credentials. Nothing in `infra/` has ever created a resource.

**Two real defects found, one of them only findable by validating:**

1. **A dependency cycle.** The push subscription declared `depends_on` both dead-letter IAM
   grants, and one of them is made *on the subscription*. Review had missed it across two
   readings; `validate` rejected it immediately. The fix is one line, and why one grant can be
   ordered and the other cannot is now a Lab 6 prediction question.
2. **The configuration would have deployed a broken service.** `DOCAPP_JOBSTORE` was never set,
   so Terraform would have brought up Cloud Run on the **in-memory job store** — the exact bug
   Lab 4 spends a week teaching. Week 12's practical would have handed students a broken
   environment and called it reproducible. Found by reading `infra/` against Labs 3–5 rather
   than by any tool.

### Week 13 authored, and three pipeline defects fixed (2026-09-22)

| Artefact | Status | Validation |
|---|---|---|
| `.github/workflows/deploy.yml` — rewritten (D-43…D-46) | done | **EXECUTED** — YAML parses; the `needs: test` gate, both permissions and the absence of any third, the empty `STATE_BUCKET`, the non-cancelling concurrency, the authenticated smoke test and the sha-tagged image are all asserted programmatically |
| `infra/versions.tf` — the backend, and why it is bootstrapped | done | **VALIDATED** — `tofu validate` and `fmt` still clean |
| `labs/lab-06/README.md` — Parts 4–6 rewritten | done | REVIEWED |
| `operations/cleanup.md` — teardown order, state bucket, WIF pool | done | REVIEWED |
| `weeks/week-13` guide + notes | done | REVIEWED |

**Three real defects in the pipeline, all of which would have bitten a student:**

1. **Local state in CI.** `terraform init` configured no backend, and a runner is a fresh
   machine every run — so the first deploy succeeds and the **second** fails on resources that
   already exist. Now a `TODO` with a bootstrapped state bucket behind it (D-43), and it turns
   out to be the best available motivation for the shared backend week 12 argues for
   abstractly.
2. **No workspace selection.** `dev` and `prod` would have shared one state file. Same class of
   bug, also invisible on a first run (D-44). Lab 6 now tells students to merge **twice**
   before concluding anything works, and asks what the two have in common.
3. **The smoke test could not reach its own service.** Since D-41 made the service private, the
   unauthenticated `curl` would have returned 403 on every healthy deployment (D-45).

**One thing named rather than minimised (D-46):** the deployer account has to create service
accounts and grant project-level IAM, so by the end of Lab 6 it is close to the most powerful
principal in the project, acting on whatever is on `main`. Teaching least privilege for eleven
weeks and then going quiet at the one genuinely hard point would have been the wrong call, so
`deploy.yml`, the lab and the notes all state it and invite a reasoned answer — including
"nothing, and here is why".

### Week 14 authored (2026-09-22)

| Artefact | Status | Validation |
|---|---|---|
| `weeks/week-14/teaching-guide.md` | done | REVIEWED — session plan sums to 180 (D-48) |
| `weeks/week-14/student-notes.md` | done | REVIEWED |

The last week with substantial new teaching content. Three things in it are new rather than
assembly:

- **The three-pass method for reading an architecture** — where state lives, where the
  boundaries are, what each identity may do — which is what both the peer review and the
  week 15 defence actually require.
- **Lock-in priced in weeks**, with a per-component table for the course's own application
  (D-50). Their `Protocol` seams made object storage cheap to move; Terraform and the queue's
  semantics are the expensive pieces, and seeing that is the payoff for a design decision made
  in week 2.
- **The structured peer review** (D-49): four written questions, answered in silence, and the
  author may not defend. Not graded.

Everything else is deliberately revision. Lab 4's confounds paragraph and Lab 5's
proves/does-not-prove paragraph are named in the guide as the rehearsals they were, and their
rubric language is reused rather than reinvented.

### Still to author

**Week 15** · quizzes 1–7 and keys · the project package · instructor solutions for Labs 2, 4
and 6. Operational guidance is authored **with** each cloud exercise, never afterwards.

**Carried forward:** `weeks/week-15/` is still a placeholder, and its session plan contradicts
`course/weekly-schedule.md` — see the next action above. `audit.py` skips unauthored files, so
nothing flagged it.

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
