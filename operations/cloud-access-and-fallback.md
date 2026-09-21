# Cloud access and fallback plan

How students get a cloud account, what happens when they cannot, and how the course stays
inside the trial window and inside a sensible spend.

All trial facts below were verified on **2026-09-21** against official Google
documentation (`course/references.md`, R-01 and R-02). **Re-verify before each offering
and before finalising setup instructions** — terms change.

---

## 1. The access model

**Primary path:** each student activates their own Google Cloud Free Trial in **week 4**.

| Fact | Detail | Consequence for the course |
|---|---|---|
| Credit | $300 "Welcome credit" | **A buffer against mistakes, not a budget.** Under the free-tier-first policy (D-19) the labs are designed to cost under $1 in total. |
| Duration | 90 days from that student's own signup | The window must reach week 15. This is the binding constraint. |
| Eligibility | Never a paying customer of Google Cloud, Google Maps Platform or Firebase; never previously used the trial | **Not all students will qualify.** Section 4 exists for them. |
| Payment method | Required, for identity verification. A temporary authorisation of roughly $0–$1 may appear for 1–14 business days | Some students have no card. Section 4 covers them too. |
| Personal card | Acceptable; a corporate card is not required | — |
| At expiry | Billing account closes, projects and resources are **stopped**; 30-day grace period to recover by upgrading | Work must be submitted and evidence captured **before** expiry, not recoverable after |
| Charges | Occur **only** after a manual upgrade to a paid account | The course never asks anyone to upgrade. Say this explicitly in week 4. |
| Per-person | Multiple people at one organisation may each sign up separately | A class of individual accounts is the expected shape |

**Students are instructed not to activate before week 4.** Every day spent before then is a
day taken off the end. Make this a visible rule in week 1, because keen students will
otherwise sign up the moment the course is mentioned.

## 2. Why week 4

| | |
|---|---|
| Weeks 1–3 | Entirely local. No account needed. Builds the mental model that makes week 4 legible. |
| Week 4 | Activation, guided, in class. Billing alerts configured the same session. |
| Weeks 4–12 | The billable phase. Lab 6 in week 12 deliberately ends it early. |
| Weeks 13–15 | Project. Light, bounded resource use; the heavy experiments were already done in Labs 4 and 5. |

**The arithmetic, and why it is not yet safe.** Fifteen consecutive weeks is 105 days.
Activating at week 4 leaves roughly 77 days of teaching before the week-15 session, which
fits inside 90 days with about two weeks of slack — **if weeks run consecutively**. One
break week consumes half that slack. Two consume it all.

Dates are not yet fixed (D-04, Q-01). `planning/calendar-worksheet.md` holds the
calculation, the decision rule, and four ranked remedies. **Do not declare the trial window
sufficient until that worksheet is filled in.** It is the single most likely way this plan
fails in practice.

## 3. Guardrails for every cloud lab

Authored **with** each lab, not bolted on afterwards.

1. **Free tier first (D-19).** Every resource a lab creates must sit inside an Always Free
   allowance, or the lab is redesigned. Verify against `operations/cost-model.md` §1, which
   lists each allowance with its source and retrieval date.
2. **Trial compatibility.** Verify each service, quota, region and feature works on an
   **unupgraded** trial account. Never require a feature that needs a paid upgrade.
3. **Region is a condition, not a preference.** `us-central1` (D-18). The Always Free
   `e2-micro` and Cloud Storage allowances exist **only** in `us-west1`, `us-central1` and
   `us-east1`. The same lab run in `asia-southeast1` is a billed lab.
4. **Bounded experiments.** Every load or failure experiment states a maximum duration,
   request count, concurrency and instance count. "Run it until it breaks" is not an
   instruction this course gives.
5. **No always-on resources without a reason.** If something must persist between sessions,
   the lab says why and what it costs to leave running.
6. **Cost estimated before deploying.** Quantity × duration × rate, with region and
   retrieval date. See `operations/cost-model.md`.
7. **Explicit create → verify → stop/delete → verify-gone.** The last step is graded.
   Resources that outlive compute are the trap: persistent disks, static external
   addresses, storage buckets, container images, snapshots, and retained logs.
8. **Budget alerts are notifications, not caps.** Configure them in week 4 with a **$1 first
   threshold**, and say plainly in the same breath that an alert stops nothing. A student who
   believes an alert is a spending cap has been actively misinformed.
9. **No credentials in code, ever.** Application identities get narrowly scoped roles.
   Project-owner is never used for a workload. A committed key is permanent — rotate it,
   do not just delete the commit.

## 4. Students without trial access

Assume some students will have no eligibility, no suitable payment method, or a previous
account. **Ask in week 1, not week 4** — publicly, as an ordinary logistics question, so
that saying "that's me" costs nothing socially.

Options in order of preference:

1. **Institutional billing account or sandbox**, if one exists (Q-02). Removes the problem
   entirely. Worth pursuing before term starts.
2. **Instructor-provisioned project** under a separate billing account, with the student as
   a named IAM principal holding narrowly scoped roles. Bounded, auditable, revocable.
3. **Local/emulated fallback path**, below.

**Never** direct a student to create a duplicate account to regain eligibility. It breaches
Google's terms, and a course that suggests it has taught the wrong lesson about
professional conduct.

**No student is disadvantaged in grading by taking the fallback path.** The rubrics assess
reasoning, evidence and explanation, and the fallback produces all three.

### The fallback design

| Lab | Cloud version | Fallback | Honest gap |
|---|---|---|---|
| 1 | Local already | — | None |
| 2 VM + networking | VM, firewall rule, external address | Local container with an explicit published-port and host-firewall exercise; read a supplied trace of the cloud path | **Cannot reproduce:** a real provider network path, provider identity, or the difference between a security-group rule and a host firewall. Supplied instructor evidence covers what the student cannot observe. |
| 3 Object + managed data store | Cloud Storage + Firestore `(default)` (D-20) | An S3-compatible object store run locally, and a local database engine | **Cannot reproduce:** real durability guarantees, cross-zone replication, or a managed service's operational boundary. The *API shape and access-pattern reasoning* do transfer. |
| 4 Managed execution + load | Cloud Run + bounded load test | Container + local load generator, with a scaling discussion against supplied evidence | **Cannot reproduce:** cold start, real autoscaling feedback, or provider-side concurrency. This is the largest gap in the fallback and must be labelled as such. |
| 5 Queue + resilience | Pub/Sub + failure injection | Local queue broker with the same at-least-once semantics; same idempotency and duplicate exercises | **Small gap.** Duplicate delivery, retry, backoff and idempotency are all demonstrable locally. Managed dead-lettering configuration is not. |
| 6 Terraform + cost | Real apply/destroy | `terraform validate` and `terraform plan` against the real provider **without applying**, plus a local-provider apply/destroy to demonstrate state | **Cannot reproduce:** drift against real infrastructure, or a real bill. The cost estimate is still produced from published rates — that exercise is identical. |

Where a fallback student cannot observe something, the instructor supplies **clearly
labelled** evidence from a pilot run — real measurements from the instructor's own account,
marked as such. It is never presented as the student's own work, and never invented.

Fallback tooling is fixed in Stage B/C alongside `operations/student-setup.md`, so the
container runtime decision (Q-04) covers both paths at once.

## 5. Pairs and shared project access

Confirmed group size is one or two (A-11). Cloud access for a pair needs care, because
trial accounts are personal and credit cannot be pooled.

**Rules:**

- **One named student owns the project**, and their trial billing account pays for it. Both
  students state this in the submission.
- **The partner gets named-user IAM access** with narrowly scoped roles — not owner, not
  editor if a narrower role suffices.
- **Credentials are never shared.** No shared password, no shared key file, no "just use my
  login". This is graded under the security band and is also the professional habit the
  course is trying to build.
- **Credit does not pool.** Two trials do not become $600 for one project. The paying
  student's ceiling is the project's ceiling.
- **Adding a partner to a project does not lift their own eligibility constraints**, and it
  does not consume their credit either — usage bills to the project's billing account.
- **The submission states:** who owns the project, whose credit paid, who performed the
  cleanup, and how the partner's access was revoked afterwards.

If the owning student's trial expires first, the project stops for both. Pairs should
check both activation dates in week 11 when they submit the proposal.

## 6. Instructor checklist

**Before term:**
- [ ] Pursue Q-02 (institutional account or education credits) — it removes the single
      largest risk in this plan
- [ ] Re-fetch R-01 and R-02; update this file if terms changed
- [ ] Fill `planning/calendar-worksheet.md` and confirm ≥14 days of trial slack
- [ ] Verify every lab's services on an unupgraded trial account

**Week 1:**
- [ ] State the "do not activate before week 4" rule
- [ ] Ask openly who expects an eligibility or payment-method problem
- [ ] Run the environment check with every student

**Week 4:**
- [ ] Guided activation in class
- [ ] Billing alerts configured, and the "an alert is not a cap" point made explicitly
- [ ] Fallback students started on their path **in the same session**, not privately later
- [ ] First cleanup verification performed together

**Weekly, weeks 4–12:**
- [ ] Ask the class whether anyone has unexpected spend or orphaned resources
- [ ] Check that the previous lab's teardown was verified, not just claimed

**Week 15:**
- [ ] Final teardown verification with every student, in the session
- [ ] Remind students their trial will close on its own and no charge follows

## 7. What this plan does not guarantee

Stated plainly, because a plan that hides its own risks is not a plan:

- That every student qualifies for a trial.
- That $300 covers unbounded experimentation. It is not meant to be spent at all: the labs
  as designed cost under $1, and the credit is there so that a mistake is survivable.
- That "free tier" means "cannot be charged". The free tier is a **discount, not a cap** —
  exceed an allowance and billing starts silently at the normal rate.
- That the 90-day window fits the real semester. **Unverified until Q-01 is answered.**
- That the fallback path is pedagogically equal. It is *assessably* equal; the table in
  section 4 is honest about what it cannot show.
- That no student will ever be charged. A student who upgrades their account and leaves
  resources running can be. The course teaches them why, verifies teardown, and says this
  out loud — that is the realistic limit of what a course can promise.
