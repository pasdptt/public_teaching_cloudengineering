# Open questions

Only questions whose answer **changes course content or feasibility**. Anything already
settled is in `decisions.md` and must not be re-asked.

Each question states who can answer it, what is blocked, and what happens if no answer arrives.

Last updated: 2026-09-21.

---

## Blocking — needed before the schedule can be dated

### Q-01 · Semester dates, holidays and institutional deadlines
**Owner:** instructor / registrar
**Blocks:** fixing quiz dates, project milestones, and — critically — the date students
activate the GCP trial.
**Why it matters:** the trial is 90 days. Fifteen teaching weeks is 105 days even with no
break. The plan (trial activated in week 4) leaves roughly 77 days of teaching plus a
cleanup buffer inside the window *only if weeks run consecutively*. One break week, or a
week-15 submission deadline that slips, can push the project demonstration past trial
expiry — at which point student workloads stop.
**If unanswered:** the schedule stays relative. `planning/calendar-worksheet.md` carries
the arithmetic to re-run. Authoring continues; dates are the last thing fixed.

### Q-02 · Is there any institutional GCP sandbox, education credit, or billing account?
*Priority lowered 2026-09-21.* Under the free-tier-first design (D-19) expected spend is under
$1 per student, so this is no longer about funding — it now matters **only** for students who
cannot pass the trial's eligibility or payment-method check. Still worth pursuing, but it is
no longer a cost question.
**Owner:** instructor / department IT
**Blocks:** whether the personal-trial path is the primary access model or a fallback.
**Why it matters:** the personal trial requires each student to have a payment method and
to have never used GCP before. Neither is guaranteed. An institutional account removes
the eligibility problem entirely and changes the cost model.
**If unanswered:** design proceeds with personal trials as primary and the local fallback
as a first-class path, not an afterthought. This is the safe direction — an institutional
account discovered later only makes things easier.

---

## Material — needed during Stage B/C authoring

### ~~Q-03 · Which managed data service for Lab 3?~~ — **RESOLVED 2026-09-21**
**Answer: Firestore**, using the project's single free `(default)` database. Recorded as D-20.

Decided exactly as D-14 required — on idle cost, not preference. Firestore has **no fixed or
idle charge** and a real free quota (1 GiB, 50k reads / 20k writes / 20k deletes per day).
Cloud SQL was rejected because it has no free tier and bills per hour whether or not anything
connects; one forgotten instance would cost more than every other lab combined.

Remaining detail for Stage C authoring, not a blocker: which specific consistency behaviour
the lab demonstrates within about 60 minutes of guided work.

### Q-04 · Container tooling students install
**Owner:** instructor, informed by the Week 1 environment check
**Blocks:** `operations/student-setup.md` and the Lab 1 instructions.
**Why it matters:** Docker Desktop's licence terms depend on organisation size and it is a
heavy install; Podman and Rancher Desktop are lighter but less uniformly documented for
beginners. Apple Silicon vs Intel Mac image architecture also has to be settled here.
**If unanswered:** setup guidance is authored tool-neutral where possible, with one
recommended default and a documented alternative, and the fallback (no containers) kept working.

### Q-05 · AI-use policy
**Owner:** instructor / academic committee — this is a policy decision, not a design one
**Blocks:** the project brief and every rubric's communication criterion.
**Proposal to review** (drafted in `project/brief.md` once authored): assistance permitted
for code and prose, disclosure required, and individual oral explanation of an
architectural decision used as the check on understanding. That oral check is already in
the design (A-11, D-16), so the policy mainly decides the disclosure format.

### Q-06 · Where do students submit, and in what form?
**Owner:** instructor
**Blocks:** submission templates and the automated functional checks.
**Options:** git repository per student, LMS upload, or a shared drive. Affects whether
objective lab checks can be run automatically by the instructor.
**If unanswered:** submission templates are authored as self-contained Markdown + evidence
files, which work under any of the three.

---

## Non-blocking

### Q-07 · Licence for reuse of the teaching materials
**Owner:** instructor / institution
Affects the README licence line only. CC BY-SA or CC BY-NC are the usual choices for
course material; code in `application/` and `infra/` would normally carry a separate
permissive software licence.

### Q-08 · Should graduate students get optional enrichment?
**Owner:** instructor
A-09 fixes the *required* standard as identical. Optional, unassessed enrichment reading
is compatible with that, but adds authoring and must not become a hidden expectation.
Default until answered: no separate track.

---

## Answered this session

| Question | Answer | Recorded as |
|---|---|---|
| Public repo — how to protect keys? | Two-repository split from the start | D-01 |
| Assessment weights? | 20 / 45 / 35 | D-02 |
| IaC tool? | Terraform | D-03 |
| Semester calendar? | Supplied later; build relative weeks | D-04, Q-01 |
| How much should the labs cost? | **Free tier wherever possible**; credit is a buffer, not a budget | D-19, D-22 |
| Lab 3 data service? | **Firestore**, free `(default)` database — zero idle cost | D-20 |
