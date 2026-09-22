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
| D-19 | **Free-tier-first.** Every cloud lab is designed to fit inside Google Cloud's **Always Free** tier. The $300 trial credit is a *buffer against mistakes*, not the budget. A lab that cannot be done for ~$0 is redesigned, not funded. | Instructor instruction, 2026-09-21: minimise cost, free tier preferred. Verified free-tier limits (R-01, R-09…R-12) make this achievable for all six labs. Target spend per student for the whole course is now **under $5**, not $30. |
| D-20 | **Lab 3's managed data service is Firestore**, using the project's single free **`(default)`** database. Resolves Q-03. | Decided on idle cost, exactly as D-14 required. Firestore has **no fixed or idle charge** and a real free quota: 1 GiB stored, 50,000 reads / 20,000 writes / 20,000 deletes per day (R-11). **Cloud SQL was rejected**: it has no free tier and bills per hour whether or not anything connects, so one student forgetting to delete an instance would cost more than every other lab in the course combined. Note: only one free database per project, and a *named* (non-default) database does not qualify. |
| D-21 | **Lab 2 uses an ephemeral external IP, never a reserved static one**, and the VM is deleted (not merely stopped) at the end of each session. | An **unattached reserved static IP costs $0.01/hour — double the $0.005/hour rate for one attached to a running VM** (R-09). A static IP also counts as "in use" while its VM is merely *stopped*. This is the course's best cost lesson and its most likely orphan, so the lab both avoids it and teaches it. |
| D-22 | **Revised spending ceilings:** under **$5** per student for the whole course; **$15** hard stop. | Follows from D-19. The previous $30/$75 figures were sized for a credit-funded course, not a free-tier one. |

---

## B2. DevOps added to the curriculum (2026-09-22)

Instruction: the course must cover DevOps for cloud engineers, including CI/CD and
environment management. Fifteen weeks and ~180 min/week are fixed, so this is a
re-sequencing, not an addition on top.

| ID | Decision | Rationale |
|---|---|---|
| D-23 | **CI is a thread from week 3, not a topic in week 12.** A GitHub Actions workflow runs the existing test suite on every push, starting as Part 6 of Lab 1. Students live with a pipeline for ten weeks before they are taught what one is. | The tests already exist from Lab 1, so CI costs about 20 minutes to set up and roughly 15 minutes of teaching. By week 13 "the pipeline" is something they have experience of rather than a diagram. Same reasoning as introducing idempotency in week 2 and the queue in week 10. |
| D-24 | **Lab 6 becomes a two-week lab across weeks 12–13: "Delivery, environments and reproducibility."** Week 12 is declarative infrastructure and environment management; week 13 is the delivery pipeline and pipeline security. The former week-13 architecture-synthesis lecture folds into week 14. | CI/CD and environment management are one subject — a pipeline that cannot target a named environment is a script, and an environment you cannot deploy to is a diagram. Splitting them across two labs would teach both badly. |
| D-25 | **CLO-9 added:** build and operate an automated delivery path across environments, and explain what each gate protects. | Chosen over folding it into CLO-7. An outcome that is taught but not separately assessed becomes decorative, and this is the part of the course an employer most directly means by "cloud engineer". Quiz 6 and Quiz 7 both cover it, and it has its own rubric line in Lab 6 and the project. |
| D-26 | **CI platform: GitHub Actions, authenticating to Google Cloud with keyless Workload Identity Federation.** No service-account key is ever created. | Actions minutes are **free for public repositories** (R-13), and this course repository is already public, so CI costs nothing. WIF is Google's own recommended method and the `google-github-actions/auth` documentation explicitly warns against exporting service-account keys (R-14). That turns the course's standing "never embed credentials" rule into something students implement rather than recite, and OIDC federation is a pattern that transfers to every other provider. Cloud Build remains available and is discussed; it is not the taught path. |
| D-27 | **Two environments: `dev` and `prod`.** One Terraform configuration, two variable files. | Enough to teach parameterisation, promotion, config/secret separation and why prod is not dev with a different name. A third environment would double the resources for no new concept, and risks pushing past the single free `e2-micro` and the single free Firestore database per project (D-19, D-20). |
| D-28 | **The project's reproducible-deployment requirement is satisfied by reusing the Lab 6 pipeline**, not by building a new one. | Protects A-07: the project must not become a second implementation workload. Weeks 13–15 give the project ~345 minutes of independent time (down from ~455 before this change), which is workable **only** because the delivery path already exists. If a pilot shows otherwise, the first remedy is to reduce the project's experiment requirements, not to extend the week. |

**Consequences recorded elsewhere:** `course/learning-outcomes.md` (CLO-9 and a revised map),
`course/weekly-schedule.md` (weeks 12–14), `course/assessment-plan.md` (quiz coverage, Lab 6
spans two weeks), `course/workload-budget.md` (weeks 2, 3, 12, 13 re-balanced; every week
still totals exactly 180), `labs/lab-06/`, `infra/`, and `.github/workflows/`.

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
| D-14 | ~~Lab 3's managed data service is not yet fixed.~~ **Superseded by D-20** — resolved to Firestore on idle-cost grounds. | — | — |
| D-15 | Lab rubric balance: 35% working implementation · 40% concepts + experimental evidence · 15% reproducibility/security/resource handling · 10% communication | Brief's proposal; keeps reasoning worth more than a working deployment | Per-lab adaptation, kept explicit in each rubric |
| D-16 | Project rubric: architecture/reasoning 25% · implementation 20% · experiments/interpretation 25% · reproducibility/security/cost 20% · communication & individual understanding 10% | Brief's proposal | — |
| D-17 | Quizzes and labs are **individual submissions**; only the project may be done in a pair. | A-11 confirms group size but not submission mode; individual labs preserve individual evidence for A-09. | — |
| D-18 | Primary lab region: **`us-central1`** | **Required, not preferred, under D-19.** The Always Free `e2-micro` and Cloud Storage allowances exist only in `us-west1`, `us-central1` and `us-east1`. A lab run in any other region leaves the free tier and starts billing. Latency from Thailand is irrelevant to the measurements taught, and every latency experiment compares against itself. | A cohort requirement to use a nearer region; the cost model would then be re-computed |

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
