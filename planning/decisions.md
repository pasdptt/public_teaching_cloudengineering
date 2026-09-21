# Decision log

Every entry is either **CONFIRMED** (settled by the academic team) or **DEFAULT**
(a design proposal adopted so work can proceed; revisable without redesigning the course).
Do not re-open CONFIRMED entries without recording a superseding decision here.

Last updated: 2026-09-21.

---

## A. Confirmed academic requirements

| ID | Decision | Status | Note |
|---|---|---|---|
| A-01 | One shared course for junior/senior CS undergraduates and early graduate students | CONFIRMED | Same outcomes and standard for all — see A-09 |
| A-02 | ~10 students, one instructor, **no teaching assistant** | CONFIRMED | Constrains grading load and support design |
| A-03 | Prerequisites: some programming and basic Linux shell only | CONFIRMED | No assumed cloud, networking, OS, DB, Docker or distributed-systems background |
| A-04 | Mixed Windows and macOS student machines, with install permission | CONFIRMED as a planning assumption | Must still be **verified** by the Week 1 environment check (see D-11) |
| A-05 | 15 weeks × 3 contact hours | CONFIRMED | |
| A-06 | Session shape: ~90 min instruction · ~30 min discussion/quiz · ~60 min guided practical | CONFIRMED | Quizzes consume discussion time, never extra contact time |
| A-07 | Independent workload ≈ 180 min/week **total** | CONFIRMED | Includes reading, quiz prep, labs and project |
| A-08 | GCP as workbench, funded by the $300 / 90-day new-user trial, subject to eligibility | CONFIRMED | Terms re-verified 2026-09-21, see `course/references.md` R-01 |
| A-09 | Identical required work, outcomes and grading criteria for undergraduates and graduates | CONFIRMED | Enrichment is optional and never assessed differently |
| A-10 | Assessment = biweekly quizzes + substantial labs + project. **No midterm or final exam** | CONFIRMED | |
| A-11 | Project groups of one **or two** students; two is the hard maximum | CONFIRMED | Individual accountability required either way |
| A-12 | Balanced emphasis: conceptual understanding *and* application engineering | CONFIRMED | |
| A-13 | Claude Code authors and maintains this repository | CONFIRMED | |

---

## B. Decisions taken in this session (2026-09-21)

| ID | Decision | Rationale |
|---|---|---|
| D-01 | **Two-repository split from the start.** This public repo holds student-facing material only; a sibling private repo `../cloudengineering-instructor` holds quiz keys, lab solutions, delivery guide and pilot evidence. | The configured git remote is a **public** GitHub repository. Deleting a key later does not remove it from public history. Chosen by the instructor over gitignoring an `instructor/` folder. |
| D-02 | **Assessment weights: quizzes 20% · labs 45% · project 35%.** | Confirmed by the instructor. Lab-heavy weighting matches a course with no exam and a "measure then explain" emphasis. |
| D-03 | **Terraform** is the infrastructure-as-code tool, pinned to the `hashicorp/google` provider `~> 8.0`. | Chosen by the instructor. Widest free documentation and strongest employability transfer. Licence note: Terraform CLI is BUSL-1.1 since v1.6; classroom and course-authoring use is not a competing offering, so it is unrestricted here. OpenTofu remains a drop-in fallback if the licence ever becomes an institutional issue — the course teaches the declarative model, not vendor syntax. |
| D-04 | **Semester dates deferred.** The schedule is authored as relative weeks 1–15; `planning/calendar-worksheet.md` is the single place where real dates, holidays and institutional deadlines get filled in. | Instructor will supply dates later. The trial-window arithmetic in `operations/cloud-access-and-fallback.md` must be re-run once dates exist — it is not safe to assume 15 consecutive weeks. |

---

## C. Adopted defaults (revisable)

| ID | Default | Why this default | What would change it |
|---|---|---|---|
| D-05 | Course title: **Cloud Computing: Principles and Practice** | Matches the brief's working title | An institutional catalogue title |
| D-06 | Teaching materials in **English** | Brief's proposal | A bilingual cohort requirement |
| D-07 | **Seven quizzes** in weeks 2, 4, 6, 8, 10, 12, 14 | Biweekly, each assessing only already-taught outcomes | Calendar gaps (D-04) may shift a quiz by one week |
| D-08 | **Six labs**, each spanning two weeks except Lab 6, all building on one application | Two-week labs fit the 60-min in-class + homework budget without a second implementation workload | Pilot timings showing a lab overruns |
| D-09 | **Markdown is authoritative.** No LMS integration, website, or slide framework. | Brief's proposal; keeps the repo the single source of truth | An institutional LMS requirement |
| D-10 | One consistent **Linux-oriented container environment** across Windows and macOS, plus a documented non-container fallback | Avoids two divergent lab instruction sets | Evidence that student machines cannot run containers |
| D-11 | Week 1 runs an **ungraded environment check** that must actually be executed by every student | A-04 is a planning assumption, not evidence. This is how it gets verified early enough to fix. | — |
| D-12 | Weekly **teaching guides stay in the public repo**; only answer keys, solutions and grading guidance move to the private repo. | Teaching guides contain no assessable answers, and publishing them helps reuse by other instructors. | An instructor preference for private teaching notes |
| D-13 | The course application is a small **document/job-processing service in Python**: submit a synthetic input, store it, request processing, poll status, read the result. | Gives a natural, honest reason to introduce object storage (Lab 3), managed execution (Lab 4) and a queue (Lab 5) without inventing new domain features. No AI APIs, no complex frontend. | — |
| D-14 | Lab 3's managed data service is **not yet fixed**. Candidate shortlist and the trial/cost check that decides it are in `operations/cloud-access-and-fallback.md`. | The brief forbids deploying several databases for comparison; the choice must follow a real trial-compatibility and cost check, not preference. | The Stage C service check |
| D-15 | Lab rubric balance: 35% working implementation · 40% concepts + experimental evidence · 15% reproducibility/security/resource handling · 10% communication | Brief's proposal; keeps reasoning worth more than a working deployment | Per-lab adaptation, kept explicit in each rubric |
| D-16 | Project rubric: architecture/reasoning 25% · implementation 20% · experiments/interpretation 25% · reproducibility/security/cost 20% · communication & individual understanding 10% | Brief's proposal | — |
| D-17 | Quizzes and labs are **individual submissions**; only the project may be done in a pair. | A-11 confirms group size but not submission mode; individual labs preserve individual evidence for A-09. | — |
| D-18 | Primary lab region: **`us-central1`** | Overlaps the Always Free tier regions (`us-west1`, `us-central1`, `us-east1`), which lowers the floor cost of the long-running pieces of Labs 2–6. Latency from Thailand is irrelevant to the measurements taught, and every latency experiment compares against itself. | A cohort requirement to use a nearer region; the cost model would then be re-computed |

---

## D. Explicit non-goals

Recorded so they are not quietly re-added later:

- Kubernetes **cluster administration**. Orchestration is covered conceptually only.
- Formal consensus proofs, service meshes, multi-cloud deployment, ML platforms, large data pipelines.
- A second cloud provider account. Provider-independence is taught by analysis, not by porting.
- Vendor certification preparation or service-name memorisation.
- Turning weeks 1–3 into a full prerequisite course in OS, networking and databases.
- Any grading or support design that implicitly assumes a TA exists.

---

## E. Deviations from the original brief

| Deviation | Reason |
|---|---|
| Instructor material is a **separate repository**, not an `instructor/` folder inside the deliverable tree. | The brief's own warning about public-repo history, applied to a remote that is in fact public. The folder names from the brief are preserved *inside* that private repo. |
| `operations/publishing-checklist.md` added (not in the brief's tree). | The brief requires documenting how to publish a clean student package; that needed a home. |
| `planning/calendar-worksheet.md` added. | D-04 needs one place where real dates are entered and the trial arithmetic is re-checked. |
