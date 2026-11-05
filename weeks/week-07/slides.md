---
marp: true
theme: cloudcourse
paginate: true
footer: 'Week 7 · Replication, consistency, choosing'
---

<!--
Deck for week 7. Derived from weeks/week-07/teaching-guide.md — that file is authoritative
for the teaching; this is what goes on the wall.

Render:  bash course/slides/render.sh 07
-->

<!-- _class: lead -->

# Replication, consistency, choosing a data service

## Week 7

Cloud Computing: Principles and Practice

<!--
TIMING: 180 min total — 85 concepts · 25 discussion · 60 practical · 10 break.
Guide: weeks/week-07/teaching-guide.md
Before you start: application/docapp/service.py open at create_job, ready to project. Lab 3 is due at the end of the week. Next week is the midterm — announce the format before the session ends.
-->

---

## Where we are

Last week the documents left the machine. This week the **job records** follow them.

After Lab 3 the application holds **nothing of its own**. Kill it, start it elsewhere, run three copies: the same answers.

That property is what weeks 9–12 are built on. Today is about what it costs.

---

<!-- _class: block -->

<span class="min">10 minutes</span><span class="clock">0:00 – 0:10</span>

# Replication

What it buys, and what it creates

---

## More than one copy

A single copy has a single point of failure. So systems keep several, on independent hardware, often in independent failure domains.

That buys **durability** and **availability**.

It also creates something subtler: **for some window of time, the copies can disagree.**

---

<!-- _class: punch -->

## Every consistency model is an answer to one question: what do readers see while the copies catch up?

---

<!-- _class: block -->

<span class="min">25 minutes</span><span class="clock">0:10 – 0:35</span>

# Consistency models

By what you can observe, not by definition

---

## Three models

| Model | Once a write is acknowledged… | The price |
|---|---|---|
| **Strong** | every later read sees it | Latency — enough replicas must agree, and some are far away |
| **Eventual** | it will propagate; until then a reader may see the old value | A bug you cannot reproduce: it succeeded, you read it back, it was not there |
| **Read-your-own-writes** | **you** see it at once; others may lag | Often enough, and often far cheaper than strong |

---

<!-- _class: punch -->

## What would a user actually notice if they read a stale value here?

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:35 – 0:50</span>

# Per operation

Two reads in your application, two requirements

---

<!-- _class: ask -->

## A job's status is read one second stale.
## Who notices?

<!--
Nobody. The page says "running" for a moment longer.
-->

---

<!-- _class: ask -->

## An idempotency-key lookup misses a key written a moment ago.
## What happens?

<!--
A SECOND JOB. A user-visible duplicate. Same application, same database, two completely different requirements.
Guide: "Teach consistency by consequence"
-->

---

## Same application, same database

| Read | Stale by one second | Requirement |
|---|---|---|
| Job status | Invisible — "running" for a moment longer | Eventual is fine |
| Idempotency-key lookup | **A second job** — a duplicate the user sees | Must see the latest write |

Consistency is a decision **per operation**, not one setting for the whole system.

---

<!-- _class: block -->

<span class="min">Break — 10 minutes</span><span class="clock">0:50 – 1:00</span>

# Break

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">1:00 – 1:20</span>

# Transactions, and the race

It is in your code today

---

## When you need a transaction

A transaction makes several operations atomic: all of them happen, or none does.

You need one when a half-finished change leaves the system **wrong** — not merely out of date.

---

<!-- _class: demo -->

## `create_job`, in `service.py`

```python
if idempotency_key:
    existing = self.jobs.find_by_idempotency_key(idempotency_key)
    if existing is not None:
        return existing, False

job = Job.create(document_id=document_id, operation=operation,
                 idempotency_key=idempotency_key)
self.jobs.put(job)
```

<!--
Project the real file, not just this slide. Walk it line by line.
Guide: "The race is the centrepiece — do it live"
-->

---

## Two requests, same key

```text
request A:  find_by_idempotency_key  ->  nothing there
request B:  find_by_idempotency_key  ->  nothing there
request A:  put(job)
request B:  put(job)
```

<!--
Ask: how many jobs, and what was the idempotency key supposed to guarantee?
-->

---

<!-- _class: ask -->

## You fixed this in Lab 1 with a lock.
## Why does a lock not work now?

<!--
Land on: a lock is scoped to one process, and there are about to be several. A transaction is the distributed answer.
DO NOT FIX IT. Lab 3 does not ask them to. Being able to see it is the objective.
-->

---

<!-- _class: punch -->

## A lock works within one process. In week 9 there will be several.

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">1:20 – 1:35</span>

# Choosing a data service

Work down the list; stop when it is answered

---

## The checklist

1. **Access pattern** — by key, by query, by range, by full text? This eliminates most options.
2. **Consistency**, *per operation*.
3. **Transactions**, and across how many records.
4. **Scale and shape** — record count, record size, read/write ratio.
5. **Operational burden** — who patches it, backs it up, and is woken when it breaks?
6. **Cost, including when idle.** The one beginners skip.

---

<!-- _class: cost -->

## Idle cost decided this course

| | Idle cost | Free quota |
|---|---|---|
| **Firestore** | **none** | 1 GiB · 50,000 reads / 20,000 writes / 20,000 deletes per day |
| Cloud SQL, smallest instance | **billed per hour, connected or not** | none |

A relational database was technically reasonable. It was rejected on **idle cost** (D-20): one forgotten instance would cost more than every other lab combined.

---

<!-- _class: ask -->

## For what workload would that reasoning be wrong?

<!--
Invite disagreement. The answer: complex relational queries with steady traffic — never idle, so idle cost is irrelevant to it. A student who gets there has understood the decision was CONTEXTUAL, not a ranking of databases.
-->

---

<!-- _class: block -->

<span class="min">25 minutes</span><span class="clock">1:35 – 2:00</span>

# Discussion

Defend one

---

## One workload, three candidates

> A small service storing **50,000 user profiles**, read by id on every request, updated rarely, with an **occasional report grouping users by country**.

**Document store · relational database · object storage**

Ten minutes in groups. Then each group defends one choice and takes questions.

<!--
Object storage goes fast. The real argument is the report query: does one grouping query justify a different data model for the 99% case? Let it stay unresolved.
-->

---

<!-- _class: punch -->

## "It depends — and here is what it depends on" is the correct professional answer.

---

<!-- _class: block -->

<span class="min">60 minutes</span><span class="clock">2:00 – 3:00</span>

# Practical

Lab 3 Parts 3–5

---

<!-- _class: demo -->

## Part 3 — job records into Firestore

```bash
gcloud firestore databases create --location=nam5 --project="$PROJECT_ID"
DOCAPP_TEST_PROJECT="$PROJECT_ID" python3 -m pytest -m lab03 -q
```

The location is a multi-region name — `nam5`, not `us-central1`.

<!--
Composite index errors are almost always an unnecessary order_by in find_by_idempotency_key. The intended implementations need no composite index.
Note who writes count() by streaming. Do not pre-empt their question-4 answer.
-->

---

<!-- _class: cost -->

## `(default)`, never a named database

There is **one free Firestore database per project**, and it must be `(default)`.

A **named** database qualifies for no free quota and bills from its first operation.

And `count()` has a cheap implementation and an expensive one. **Both pass every test.** Question 4 asks which you wrote.

---

## Part 4 — one variable: where the state lives

| | Documents | Job records |
|---|---|---|
| **A** | local | memory |
| **B** | Cloud Storage | memory |
| **C** | Cloud Storage | Firestore |

**Three runs each**, conditions stated. Then: how much latency did each move add, and how much of it is the round trip to Iowa?

**Commit to a prediction now:** would the same code run faster deployed in `us-central1`? Lab 4 settles it.

---

<!-- _class: demo -->

## Part 5 — teardown and verification

```bash
gcloud storage rm -r "gs://${PROJECT_ID}-docapp-lab3"
gcloud storage ls --project="$PROJECT_ID"
gcloud firestore databases list --project="$PROJECT_ID"
```

- **Object versions** — check, and say how you checked.
- **Firestore** — empty the collection; keeping the empty `(default)` database is fine *if you can show it is free*.

<!--
BEFORE ANYONE LEAVES: bucket deleted, versioning checked, verification output shown.
-->

---

## This week's work — 180 minutes

| | |
|---|---|
| Read the notes | 25 min |
| Lab 3 Parts 3–5: Firestore, the experiment, teardown | 155 min |

**Lab 3 is due at the end of this week**, with teardown verification.

---

<!-- _class: lead -->

# Next week

**Midterm** — 120 minutes, weeks 1–7 and Labs 1–3

One A4 sheet of your own handwritten notes · no devices

<!--
Say the format out loud, and point at weeks/week-08/student-notes.md for how to prepare in the 180 minutes the week allows.
-->
