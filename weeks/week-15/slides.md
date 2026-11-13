---
marp: true
theme: cloudcourse
paginate: true
footer: 'Week 15 · Demonstration and defence'
---

<!--
Logistics deck for week 15. No lecture this week. Derived from course/teaching-guides/week-15.md,
which is authoritative.

Render:  bash course/slides/render.sh 15
-->

<!-- _class: lead -->

# Demonstration and defence

## Week 15

Cloud Computing: Principles and Practice

<!--
TIMING: 180 min total — 120 demonstrations · 30 synthesis · 30 teardown and reflection. No break block: the demonstrations run in two halves with a natural pause.
Guide: course/teaching-guides/week-15.md
Before you start: the running order published in advance and fixed; check the trial expiry dates collected in the week 8 check.
-->

---

## Today

| | | |
|---|---|---|
| **Demonstrations and defence** | 120 min | up to 12 minutes per group, questions included |
| **Synthesis** | 30 min | what transfers, and what was a commitment |
| **Teardown and reflection** | 30 min | destroy everything, prove it, then write |

---

<!-- _class: block -->

<span class="min">120 minutes</span><span class="clock">0:00 – 2:00</span>

# Demonstrations

Twelve minutes each, and the time is kept

---

## Your twelve minutes

| | |
|---|---|
| ~4 min | **The system running.** Actually running, not a screenshot |
| ~3 min | The architecture, and the decision that mattered most |
| ~2 min | The experiment: what you measured, what you found, what it does not show |
| ~3 min | Questions |

**In a pair, both of you answer an individual question** — about a decision you personally made. Everyone in every pair is asked one.

<!--
Announce the individual question now, to the whole room, so nobody reads it as suspicion.
Stop people at twelve minutes. The groups at the end are the ones who pay for the groups at the start running over.
-->

---

## Running order

| Slot | Starts | Group | | Slot | Starts | Group |
|---|---|---|---|---|---|---|
| 1 | 0:00 | | | 6 | 1:00 | |
| 2 | 0:12 | | | 7 | 1:12 | |
| 3 | 0:24 | | | 8 | 1:24 | |
| 4 | 0:36 | | | 9 | 1:36 | |
| 5 | 0:48 | | | 10 | 1:48 | |

<!--
Fill in the names in your own copy before the session; never commit them — this repository is public. With five pairs instead of ten individuals, the same 120 minutes gives each group more time, not a longer session.
-->

---

<!-- _class: punch -->

## Something broken on the day? Say so at the start, and spend the time on your evidence.

---

<!-- _class: block -->

<span class="min">30 minutes</span><span class="clock">2:00 – 2:30</span>

# Synthesis

What transfers, and what was a commitment

---

## One table, built by the room

Two columns on the board: **Transfers** · **Commitment to this provider**.

Every entry is defended in a sentence.

Then two questions:

1. **Look at the right-hand column. Roughly how many weeks to leave?**
2. **Which of those commitments would you make again?**

<!--
Expect: object storage's access pattern / the client library and IAM model; at-least-once and idempotency / the push envelope and retry shape; request-scoped execution / the scaling algorithm and $PORT; desired-state infra / every resource type in main.tf; OIDC federation / pools, providers and condition syntax; measuring before believing / nothing.
Guide: "Synthesis (30 min)"
-->

---

<!-- _class: block -->

<span class="min">30 minutes</span><span class="clock">2:30 – 3:00</span>

# Teardown and reflection

Destroy it, prove it, then write

---

## In this order, and not another

1. `terraform destroy` — **each** workspace
2. **The Artifact Registry repository** and its images, and `gs://PROJECT_cloudbuild` — never in state
3. **Deployer service account, WIF pool and provider** — `weeks/week-13/lab-06/starter/02-teardown-pipeline.sh`
4. **The state bucket, last**

**Pairs:** the owner revokes the partner's access, and records who did it and when.

---

<!-- _class: demo -->

## Then prove it

```bash
gcloud run services list           --project="$PROJECT_ID"
gcloud pubsub subscriptions list   --project="$PROJECT_ID"
gcloud pubsub topics list          --project="$PROJECT_ID"
gcloud storage ls                  --project="$PROJECT_ID"
gcloud artifacts repositories list --location=us-central1 --project="$PROJECT_ID"
gcloud compute instances list      --project="$PROJECT_ID"
gcloud compute addresses list      --project="$PROJECT_ID"
gcloud iam service-accounts list   --project="$PROJECT_ID"
```

**Empty output** is what clean means — apart from the **default service accounts** Google created with the project, which you did not make. It goes in your submission.

<!--
If someone finds something still running, say out loud that it is a success, and ask how it survived (D-53).
Do not ask anyone to close their account or upgrade. The trial lapses on its own without charge.
-->

---

## Half a page, before you leave

1. What did you believe about cloud computing in week 1 that you no longer believe?
2. Which measurement surprised you most, and what did you do about it?
3. Name a decision in your project you would now make differently, and why.
4. What would you want to learn next, and what makes you say that?

**Not graded.** It is worth more when nobody is performing.

---

<!-- _class: lead -->

# Thank you

The project is due by the end of this week

Cleanup evidence included
