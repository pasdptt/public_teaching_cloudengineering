# Cost model

**Policy: free-tier-first (decision D-19).** Every cloud lab in this course is designed to
fit inside Google Cloud's **Always Free** tier. The $300 trial credit is a *buffer against
mistakes*, not the budget. A lab that cannot be run for approximately $0 is redesigned, not
funded.

**Expected total spend per student for the entire course: well under $1.**
Ceiling: $5. Hard stop: $15 (decision D-22).

All rates and allowances below were retrieved from official Google documentation on
**2026-09-21**. Each is cited to an entry in `course/references.md`. Re-verify before each
offering — and note that a free-tier limit changing is exactly the kind of change that
would break this design silently.

---

## 1. The free-tier allowances this course depends on

| Service | Always Free allowance | Ref |
|---|---|---|
| Compute Engine | 1 non-preemptible **`e2-micro`** per month, **only** in `us-west1`, `us-central1` or `us-east1`; 30 GB-months standard persistent disk; 1 GB egress | R-01 |
| Cloud Storage | 5 GB-months regional storage in those same US regions; 5,000 Class A and 50,000 Class B operations per month | R-01 |
| Cloud Run | 2,000,000 requests; 180,000 vCPU-seconds; 360,000 GiB-seconds per month (request-based billing) | R-01, R-12 |
| Artifact Registry | 0–0.5 GiB storage per month | R-10 |
| Cloud Build | 2,500 build-minutes per month (`e2-standard-2`) | R-01 |
| Firestore | 1 GiB stored; 50,000 reads, 20,000 writes, 20,000 deletes **per day**; 10 GiB egress per month | R-11 |
| Pub/Sub | 10 GiB of messages per month | R-01 |
| Cloud Logging | First 50 GiB per project per month | R-01 |
| External IPv4 | **1 hour per month per account** — and that is all | R-09 |

Two properties of the free tier that students must be told explicitly:

- **It is aggregated per billing account, not per project.** Making a second project does not
  double the allowance.
- **The region is not a preference, it is a condition.** An `e2-micro` in `asia-southeast1`
  is a billed VM. This is why D-18 fixes `us-central1`.

## 2. The one thing in this course that actually costs money

**External IPv4 addresses.** Verified rates (R-09):

| Situation | Rate | Per 30 days |
|---|---|---|
| Attached to a **running** standard VM | **$0.005 / hour** | ~$3.60 |
| Attached to a preemptible or Spot VM | $0.0025 / hour | ~$1.80 |
| **Reserved static IP, NOT attached to anything** | **$0.01 / hour** | **~$7.20** |

Free tier: **one hour per month per account.** That is the entire allowance.

Read that table again, because it contains the single best lesson in the cost module:

> **An idle, unused, reserved IP address costs twice as much as one doing useful work.**

And the trap behind it: a **static** IP counts as "in use" while its VM is merely *stopped* —
so "I stopped the VM, I'm not paying" is wrong twice over. An **ephemeral** IP is only in use
while the instance is running, and disappears when the instance is deleted.

**Design consequences (D-21):**

- Lab 2 uses an **ephemeral** external IP. Students never reserve a static address.
- The VM is **deleted**, not stopped, at the end of each session.
- The lab teaches the static-IP trap deliberately, with these numbers, rather than letting a
  student discover it from a bill.

Realistic Lab 2 cost: roughly 8 hours of attached ephemeral IP ≈ **$0.04**. Minus one free
hour. That is the course's largest single line item.

## 3. Per-lab cost model

Quantities are design decisions, chosen so that each row stays inside an allowance in §1.

### Lab 1 — Local foundations (weeks 2–3)

No cloud account, no billing account, no resources. **$0.00, guaranteed.**

### Lab 2 — VM and networking (weeks 4–5)

| Resource | Quantity | Free-tier status | Est. |
|---|---|---|---|
| `e2-micro`, `us-central1` | 1 | Always Free (1/month/account) | $0.00 |
| Standard persistent disk | 10 GB | Inside 30 GB-months | $0.00 |
| **Ephemeral external IPv4** | 1, ≤ 8 h attached | 1 h free, then $0.005/h | **~$0.04** |
| Egress | < 100 MB | Inside 1 GB | $0.00 |
| **Lab total** | | | **~$0.04** |

*Constraints that keep this true:* exactly one VM, in `us-central1`, `e2-micro` only, deleted
at the end of each session, ephemeral IP only.

### Lab 3 — Object storage and Firestore (weeks 6–7)

| Resource | Quantity | Free-tier status | Est. |
|---|---|---|---|
| Cloud Storage, regional `us-central1` | < 100 MB | Inside 5 GB-months | $0.00 |
| Class A operations (writes, lists) | < 2,000 | Inside 5,000/month | $0.00 |
| Class B operations (reads) | < 10,000 | Inside 50,000/month | $0.00 |
| **Firestore `(default)` database** | < 10 MB, < 5,000 ops/day | Inside 1 GiB / 50k reads / 20k writes per day | $0.00 |
| **Lab total** | | | **$0.00** |

*Why Firestore and not a relational managed database (D-20):* Firestore has **no fixed or
idle charge**. Cloud SQL has no free tier and bills per hour whether or not anything
connects — a single forgotten instance would cost more than every other lab in this course
combined. The brief forbids deploying several databases for comparison, so one is chosen, and
it is chosen on idle cost.

*Two Firestore constraints students must know:* only **one free database per project**, and it
must be the **`(default)`** database — a *named* database does not qualify for free quota at
all. The daily quotas reset around midnight US Pacific time, which is mid-afternoon in
Bangkok; a student who exhausts writes while experimenting waits for that reset rather than
paying.

### Lab 4 — Managed execution and load (weeks 8–9)

| Resource | Quantity | Free-tier status | Est. |
|---|---|---|---|
| Cloud Run requests | ≤ 50,000 total | Inside 2,000,000/month | $0.00 |
| Cloud Run vCPU-seconds | ≤ 3,000 | Inside 180,000/month | $0.00 |
| Cloud Run GiB-seconds | ≤ 1,500 | Inside 360,000/month | $0.00 |
| Artifact Registry storage | < 0.4 GiB | Inside 0.5 GiB/month | $0.00 |
| Cloud Build minutes | < 30 | Inside 2,500/month | $0.00 |
| **Lab total** | | | **$0.00** |

**Experiment bounds — these are what keep it free:** max 5 minutes per run, max 3 runs, max
concurrency 50, `--max-instances` capped, and **`--min-instances=0`**.

Two ways a student can leave the free tier here, both taught explicitly:

1. **Minimum instances above zero.** A Cloud Run service with `min-instances=0` and no traffic
   costs exactly **$0.00** — there is no charge for a service merely existing (R-12). Set it
   above zero and you are buying an always-on instance.
2. **Image accumulation.** 0.5 GiB is not much. Every rebuild pushes new layers. The lab
   includes deleting old images, and explains that a registry is storage like any other.

### Lab 5 — Queue and resilience (weeks 10–11)

| Resource | Quantity | Free-tier status | Est. |
|---|---|---|---|
| Pub/Sub message volume | < 50 MB | Inside 10 GiB/month | $0.00 |
| Retained undelivered messages | short retention, bounded | Inside the same allowance | $0.00 |
| Consumer compute | reuses Lab 4's Cloud Run | Inside Cloud Run free tier | $0.00 |
| **Lab total** | | | **$0.00** |

*Orphan risk:* a subscription with no consumer **retains messages and bills for their storage**
once past the allowance. An abandoned subscription is this lab's signature orphan, and
teardown verification names it explicitly.

### Lab 6 — Terraform and cost (week 12)

| Resource | Quantity | Free-tier status | Est. |
|---|---|---|---|
| Recreated environment (subset of Labs 2–4) | 1, ≤ 2 h, applied and destroyed in one sitting | As above | ~$0.01 |
| **Lab total** | | | **~$0.01** |

The deliverable of this lab **is** a cost estimate, so §1–§2 of this file are its source
material. Students build the estimate themselves from official pricing pages, then compare it
with the actual billing report — the gap between the two is the assessed insight.

### Project (weeks 13–15)

Student-scoped, so the estimate is too. **The project must also be free-tier-first**: the
week-13 design review checks the student's own cost estimate against §1 *before* anything is
built, and a design that needs a paid resource is sent back for redesign rather than approved
with a budget.

### Course total

| Lab | Estimate |
|---|---|
| Lab 1 | $0.00 |
| Lab 2 | ~$0.04 |
| Lab 3 | $0.00 |
| Lab 4 | $0.00 |
| Lab 5 | $0.00 |
| Lab 6 | ~$0.01 |
| Project | ~$0.00–0.20 |
| **Total per student** | **well under $1** |

Against a $300 credit, that is a rounding error — which is the point. The credit exists so
that a mistake is survivable, not so that it gets spent.

---

## 4. Method (still required, even when everything is free)

Producing the estimate is assessed content, not a formality. Every cloud lab asks for one in
this form, **before** anything is deployed:

```text
Resource · Quantity · Duration or operation count · Region · Free-tier allowance ·
Amount above allowance · Unit rate · Rate retrieved on · Estimated cost
```

Rules:

- **Estimate before deploying.** The gap between estimate and actual bill is the lesson.
- **State the region.** A free-tier allowance that exists in `us-central1` does not exist in
  `asia-southeast1`.
- **Subtract the free-tier allowance explicitly, and say what happens above it.** The free
  tier is a **discount, not a cap**: exceeding it bills at the normal rate silently.
- **State the retrieval date.** A rate without a date is not a rate.
- **Round up.** An estimate that is too low teaches nothing useful.
- **"It's free" is not an estimate.** A student must be able to say *why* it is free, *which*
  allowance covers it, and *what* would take them outside it.

### Where to get rates

1. <https://cloud.google.com/free/docs/free-cloud-features> — the Always Free allowances
2. <https://cloud.google.com/pricing/list> — authoritative per-SKU rates
3. <https://cloud.google.com/products/calculator> — whole-environment totals

Record URL, figure and date in the lab's cost section, and add the source to
`course/references.md`.

---

## 5. Spending ceilings

| Scope | Target | Hard stop — investigate immediately |
|---|---|---|
| Per student, whole course | **under $5** | **$15** |
| Any single lab | **under $1** | $5 |
| Project, weeks 13–15 | **under $2** | $8 |

These are deliberately far below the expected spend of "well under $1". A student who reaches
$5 has not run an expensive experiment — **they have left something running.** Almost always
one of: a VM not deleted, a reserved static IP, a Cloud Run service with minimum instances
above zero, or a Firestore *named* database created instead of the free `(default)` one.

**No mark anywhere in this course rewards spending more.** Where two designs meet the
requirement, the cheaper one is the better answer and should say so.

---

## 6. Resources that keep billing after you stop the compute

Taught, not merely documented. This is how a student unexpectedly spends money.

| Resource | Survives | Why it is missed | Verified rate |
|---|---|---|---|
| **Reserved static external IP, unattached** | Everything. Deleting the VM does not release it | "I deleted the VM" — the *address* is a separate resource you reserved | **$0.01/h ≈ $7.20/month** (R-09) |
| **Static external IP on a *stopped* VM** | Stopping the instance | A static IP is "in use" whether the VM runs or not | $0.005/h (R-09) |
| Persistent disk | Stopping the VM, and deleting it too unless the delete rule says otherwise | "The VM is stopped, so I'm not paying" — the disk still occupies GB-months | Inside 30 GB free, then billed |
| Storage bucket and its objects | Everything else | Nothing about deleting a VM touches a bucket | Inside 5 GB free, then billed |
| Object versions / soft-deleted objects | Deleting the visible object | Versioning keeps paying for data you believe is gone | as storage |
| Container images in Artifact Registry | Deleting the Cloud Run service | Layers accumulate on every rebuild; 0.5 GiB goes quickly | $0.000137/GiB-h above 0.5 GiB (R-10) |
| Disk snapshots and custom images | Deleting the source disk | — | billed |
| Pub/Sub subscription with no consumer | Deleting the publisher | Retained messages are billable storage | inside 10 GiB free, then billed |
| **Cloud Run with `min-instances > 0`** | Having no traffic | It looks idle; it is provisioned | billed as running |
| **Firestore *named* (non-default) database** | — | It works identically but **qualifies for no free quota at all** | billed from the first operation (R-11) |
| Retained logs above the free allowance | Deleting the service | Retention outlives the workload | inside 50 GiB free, then billed |
| Load balancer forwarding rules | Deleting the backends | Forwarding rules bill independently | billed |

Every cloud lab's cleanup section lists the subset it can create. The teardown
**verification** step is what earns the reproducibility marks — a listing showing nothing
remains, not a sentence claiming it.

---

## 7. Budget alerts

Configured in week 4 on every student's account. Three things to say, in this order:

1. An alert emails you when spend crosses a threshold.
2. **An alert does not stop anything.** It is a smoke detector, not a sprinkler.
3. The real controls are: staying inside the free tier, bounded experiments, deleting what
   you create, and verifying.

Because expected spend is under $1, set the **first threshold very low — $1** — followed by
$5, $15 and $50 (thresholds are configured as amounts or as percentages of the credit). A $1
alert should never fire in a correctly-run course, which is exactly what makes it a useful
signal. An alert at 50% of $300 would fire only after something had gone very wrong for a
very long time.

---

## 8. Maintenance

| Task | When |
|---|---|
| Re-verify every allowance in §1 and every rate in §2 and §6 | Before each offering |
| Re-check that each lab's quantities still sit inside the allowances | Before each offering |
| Record **actual** observed spend from a pilot run | Private repo, `pilot-evidence/` |

Estimates and observations are never merged into one number. If a pilot shows a lab costs
more than this file predicts, the file is wrong and gets corrected — the lab is not quietly
re-budgeted.
