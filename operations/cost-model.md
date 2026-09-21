# Cost model

> **Deliberately incomplete.** Every rate cell below is empty.
>
> Two official pricing pages were fetched on 2026-09-21 and neither returned usable
> E2-family figures (`course/references.md`, R-04). Writing a plausible-looking number
> here would be worse than leaving it blank, because students and the instructor would
> both act on it. Rates are filled in during Stage C, per lab, each stamped with the date
> it was retrieved.
>
> **What is already decided and usable:** the estimation method, the quantities, the
> region, the spending ceilings, and the list of things that keep billing after you think
> you turned them off. Those are the parts that carry the teaching.

---

## 1. Method

Every cloud lab produces an estimate in this form, before anything is deployed:

```text
Resource · Quantity · Duration or operation count · Region · Unit rate · Rate retrieved on · Estimated cost
```

Rules:

- **Estimate before deploying, not after.** Producing the estimate is part of the lab, and
  the gap between estimate and actual is itself a teaching moment.
- **State the region.** Rates differ by region. `us-central1` unless a lab says otherwise (D-18).
- **State the date.** A rate without a retrieval date is not a rate.
- **Label estimates as estimates.** Never present one as a measured bill.
- **Subtract the Always Free allowance explicitly**, and say what happens if the student
  exceeds it (they are billed at the normal rate for the excess — the free tier is a
  discount, not a cap).
- **Round up.** An estimate that is too low teaches nothing useful.

### Where to get rates

1. <https://cloud.google.com/pricing/list> — authoritative per-SKU list
2. <https://cloud.google.com/products/calculator> — useful for a whole-lab total
3. The service's own pricing page

Record the URL, the figure and the date in the lab's own cost section, and add the source
to `course/references.md`.

---

## 2. Spending ceilings

Conservative targets, set so that substantial credit remains at the end. The $300 is a
ceiling, not a target, and no mark anywhere in this course rewards spending more.

| Scope | Target | Hard stop — investigate immediately |
|---|---|---|
| Per student, whole course | **under $30** | $75 |
| Per two-week cloud lab | **under $6** | $15 |
| Lab 4 load experiment (the largest single burst) | **under $3** | $8 |
| Project, weeks 13–15 | **under $12** | $30 |

Even at the *hard stop* figures, a student who hit every one of them would finish well
inside $300. The targets exist so that a problem is visible long before the credit is.

**If a student passes a hard stop:** stop the experiment, inventory resources, find what is
running that should not be. This is almost always an un-deleted resource rather than a
genuinely expensive experiment — usually a VM left on, a static address, or a disk that
survived its instance.

---

## 3. What the labs consume (quantities fixed; rates pending)

Quantities are design decisions and are already settled. They are what bound the spend.

### Lab 2 — VM and networking (weeks 4–5)

| Resource | Quantity | Duration | Region | Rate | Retrieved | Est. |
|---|---|---|---|---|---|---|
| VM instance (smallest sufficient; `e2-micro` if adequate) | 1 | ≤ 8 h running total, stopped between sessions | us-central1 | — | — | — |
| Boot disk (standard persistent) | 10 GB | life of the lab | us-central1 | — | — | — |
| External IP while attached | 1 | ≤ 8 h | us-central1 | — | — | — |
| Egress | < 1 GB | — | — | — | — | — |

*Free-tier note:* one `e2-micro` per month in `us-central1` plus 30 GB-months of standard
persistent disk falls in the Always Free tier (R-01). Much of this lab may cost nothing.
Students still produce the estimate — the skill is the point, not the saving.

*Watch:* a **stopped** VM still bills for its disk, and an external address can bill when
it is reserved but unattached.

### Lab 3 — Object storage and managed data (weeks 6–7)

| Resource | Quantity | Duration | Rate | Est. |
|---|---|---|---|---|
| Cloud Storage, regional | < 1 GB | 2 weeks | — | — |
| Class A operations | < 5,000 | — | — | — |
| Class B operations | < 50,000 | — | — | — |
| Managed data service (**not yet chosen — D-14 / Q-03**) | smallest tier | ≤ 2 weeks | — | — |

*Free-tier note:* 5 GB-months regional storage and those operation counts are Always Free
in US regions (R-01), so the object-storage half should be free at these quantities.

*This is the highest-risk lab for cost*, because a managed database instance is typically
**always-on and billed per hour whether used or not**. The service choice (Q-03) must
weigh this above every other consideration, and the lab must tell students either to stop
the instance between sessions or to choose a service that does not bill when idle.

### Lab 4 — Managed execution and load (weeks 8–9)

| Resource | Quantity | Rate | Est. |
|---|---|---|---|
| Cloud Run requests | ≤ 50,000 total | — | — |
| Cloud Run vCPU-seconds | bounded by experiment cap | — | — |
| Cloud Run memory GB-seconds | bounded by experiment cap | — | — |
| Container image storage | < 1 GB | — | — |
| Cloud Build minutes | < 30 | — | — |

**Experiment bounds — these are the actual cost control:** maximum 5 minutes per run,
maximum 3 runs, maximum concurrency 50, maximum instance count capped in the service
configuration. A student who cannot get a result inside those bounds has a design problem,
not a budget problem.

*Free-tier note:* 2M requests, 360,000 GB-seconds, 180,000 vCPU-seconds per month, and
2,500 Cloud Build minutes are Always Free (R-01). This lab is likely free. The estimate is
still required.

*Watch:* a **minimum instance count above zero** turns request-priced execution into
always-on execution. The lab sets it to zero and explains why.

### Lab 5 — Queue and resilience (weeks 10–11)

| Resource | Quantity | Rate | Est. |
|---|---|---|---|
| Pub/Sub messages | < 100 MB | — | — |
| Retained undelivered messages | bounded by short retention | — | — |
| Compute for consumer | reuses Lab 4 | — | — |

*Free-tier note:* 10 GiB of Pub/Sub messages per month is Always Free (R-01).

*Watch:* a subscription with no consumer **retains messages and bills for storage**. An
abandoned subscription is the classic orphan from this lab, and teardown verification must
name it explicitly.

### Lab 6 — Terraform and cost (week 12)

| Resource | Quantity | Rate | Est. |
|---|---|---|---|
| Recreated environment (subset of Labs 2–4) | 1 | — | — |
| Duration | ≤ 2 h, applied and destroyed in one sitting | — | — |

This lab's deliverable **is** a cost estimate, so the method above is the assessed content.

### Project (weeks 13–15)

Scope is the student's, so the estimate is too. The project rubric requires a cost model
tied to a stated workload with explicit assumptions (20% band). The design review in week
13 checks the estimate against the ceiling in section 2 **before** anything is built.

---

## 4. Resources that keep billing after you stop the compute

This list is taught, not just documented. It is the single most common way a student
unexpectedly spends credit.

| Resource | Survives | Why students miss it |
|---|---|---|
| Persistent disk | Stopping **or** deleting the VM, depending on the delete rule | "The VM is stopped, so I'm not paying" — the disk still bills |
| Static external IP address | Detaching from the instance | An address that is reserved but unattached can bill *more* than an attached one |
| Storage bucket and its objects | Everything | Nothing about deleting a VM touches a bucket |
| Object versions and soft-deleted objects | Deleting the visible object | Versioning keeps paying for data you think is gone |
| Container images / artifacts | Deleting the service that ran them | Images accumulate silently across rebuilds |
| Disk snapshots and custom images | Deleting the source disk | — |
| Pub/Sub subscription with no consumer | Deleting the publisher | Retained messages bill for storage |
| Managed database instance | Idleness | Typically billed hourly whether or not anything connects |
| Retained logs above the free allowance | The service being deleted | Retention outlives the workload |
| Load balancer forwarding rules | Deleting the backends | Forwarding rules bill independently |

Every cloud lab's cleanup section lists the subset it can create, and the teardown
**verification** step is what earns the reproducibility marks — a listing showing nothing
remains, not a sentence claiming it.

---

## 5. Budget alerts

Configured in week 4, on every student's account. The three things to say, in this order:

1. An alert emails you when spend crosses a threshold.
2. **An alert does not stop anything.** It is a smoke detector, not a sprinkler.
3. The actual controls are: bounded experiments, deleting what you create, and verifying.

Suggested thresholds (percentages of the $300 credit): 5%, 10%, 25%, 50%. The first one
should fire long before anything is wrong, which is exactly what makes it useful.

---

## 6. Filling this file in (Stage C)

For each lab, when it is authored:

1. Retrieve each rate from an official source; record the URL and date.
2. Fill the rate and estimate cells in the table above.
3. Add the source to `course/references.md` with FETCHED status.
4. Copy the lab's own table into its `labs/lab-NN/README.md` cost section.
5. Check the total against the ceilings in section 2. **If a lab exceeds its ceiling,
   reduce the quantities** — do not raise the ceiling.
6. Update `planning/progress.md`.

After a pilot run, record **actual** observed spend in the private repository
(`../cloudengineering-instructor/pilot-evidence/`), clearly separated from estimates.
Estimates and observations are never merged into one number.
