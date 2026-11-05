---
marp: true
theme: cloudcourse
paginate: true
footer: 'Week 6 · Storage abstractions'
---

<!--
Deck for week 6. Derived from weeks/week-06/teaching-guide.md — that file is authoritative
for the teaching; this is what goes on the wall.

Render:  bash course/slides/render.sh 06
-->

<!-- _class: lead -->

# Storage abstractions

## Week 6

Cloud Computing: Principles and Practice

<!--
TIMING: 180 min total — 85 concepts · 15 quiz · 10 discussion · 60 practical · 10 break.
Guide: weeks/week-06/teaching-guide.md
Before you start: check the billing report. Anyone over $1 has left something running from Lab 2 — have that conversation first.
-->

---

<!-- _class: ask -->

## The application stores two things.
## Where should each one go?

Documents · job records

<!--
BEFORE naming any of the four abstractions. Collect answers on the board. By the time you name object storage they will have said "documents never change after they're written" — which IS the justification.
Guide: "Make them choose before you tell them"
-->

---

<!-- _class: block -->

<span class="min">25 minutes</span><span class="clock">0:00 – 0:25</span>

# Four ways to store bytes

Four access patterns, not four products

---

## Block storage

A raw device. The OS puts a filesystem on it and uses it like a disk — because it is one. Attached to **one** machine at a time.

**Assumes** one writer, arbitrary reads and writes at arbitrary offsets, low latency.

**Costs you** — it belongs to a machine. Your Lab 2 boot disk was block storage, which is why deleting the VM was a question about the disk as well.

---

## File storage

A filesystem over a network, shared by several machines. POSIX semantics — directories, permissions, partial writes.

**Assumes** several machines genuinely need to see the same filesystem.

**Costs you** more than the alternatives, and its semantics are hard to make fast over a network. Usually chosen because existing software demands a filesystem.

---

## Object storage

A flat namespace of keys and byte-blobs, over HTTP. Written whole, read whole.

**No partial writes. No appends. No rename.**

**Assumes** write once, read many, never modified in place.

**Gains you** effectively unlimited capacity, very high durability, no machine that owns it, and a price per gigabyte far below the others.

---

## Databases

Structured records, with query, update in place and — usually — transactions.

**Assumes** you need to find things by their contents, change part of a record, or make several changes atomically.

**Costs you** a per-byte price far above object storage, size limits per record, and a schema or index design you cannot avoid.

---

<!-- _class: punch -->

## Not "what am I storing?" — but how will it be read and written, and by how many things at once?

---

## The course application, answered

| | Access pattern | Fits |
|---|---|---|
| **Documents** | Written once, read whole, never modified, nobody queries the contents | **Object storage** |
| **Job records** | Small, updated several times, looked up by id, listed by recency, searched by key | **A database** |

That is Lab 3 Part 1 — and you defend the options you **rejected**, too.

---

<!-- _class: block -->

<span class="min">25 minutes</span><span class="clock">0:25 – 0:50</span>

# Object storage, properly

The property that changed architecture

---

<!-- _class: ask -->

## A 1 GB log file sits in a bucket.
## Append one line. What happens?

<!--
Let it land. You upload the whole gigabyte again.
Guide: "The no-append property is the one that matters"
-->

---

## You upload the whole gigabyte again

That is why:

- nobody puts a database **on** object storage, and
- append-only workloads write **many small objects** instead of one growing one.

To "edit" an object, you write a new one.

---

## Why it changed how applications are built

**Before:** "the files" lived on a server, and that server was special.

**After:** they live nowhere in particular, and **no server is special**.

Everything about stateless execution in weeks 9–12 follows from that.

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:50 – 1:05</span>

# Durability and availability

What a number with many nines claims

---

## Two different questions

**Durability** — does my data still exist later?

**Availability** — can I reach it right now?

Providers quote them separately, because they are different.

---

## What "eleven nines" covers

A statement about **hardware and media failure**, achieved by writing your object to several independent places.

It is **not** a claim about:

- you deleting it by mistake
- your code writing the wrong bytes
- your credentials being stolen
- your account being closed

---

<!-- _class: punch -->

## Replication protects against the media. Versioning and backups protect against you.

---

<!-- _class: cost -->

## Versioning has a bill attached

With versioning on, deleting the object you can see leaves a **version** behind — and it still occupies storage.

Lab 3's graded teardown asks you to check, and to say **how** you checked.

---

<!-- _class: block -->

<span class="min">Break — 10 minutes</span><span class="clock">1:05 – 1:15</span>

# Break

---

<!-- _class: block -->

<span class="min">10 minutes</span><span class="clock">1:15 – 1:25</span>

# Access control on storage

Week 1's shared responsibility, made concrete

---

## The commonest breach is a configuration

A storage bucket readable by anyone. Not a sophisticated attack.

Two settings in Lab 3 worth understanding rather than copying:

- **Uniform bucket-level access** — permissions on the bucket, not per object. Otherwise nobody can say with confidence who can read what.
- **Public access prevention** — makes public access **impossible**, not merely not-yet-granted.

---

<!-- _class: punch -->

## Default-private and cannot-be-made-public are different guarantees. Only the second survives the next person.

---

<!-- _class: block -->

<span class="min">10 minutes</span><span class="clock">1:25 – 1:35</span>

# Storage cost

Three components, and beginners see one

---

<!-- _class: cost -->

## Not just per gigabyte

1. **Storage** — per GB per month
2. **Operations** — per request
3. **Egress** — per GB leaving the provider's network

| Cloud Storage operations | Examples | Free per month |
|---|---|---|
| **Class A** | writes, lists | 5,000 |
| **Class B** | reads, metadata lookups | 50,000 |

<!--
Ask what a tenfold difference in the free allowance implies about relative cost — and so which operations to be careful with.
-->

---

<!-- _class: cost -->

## Two traps, both of which pass the tests

**Many tiny objects** can cost more in operations than in storage.

**`exists()` written as a download.** Still one Class B operation — but it moves the **whole object** to answer yes or no. From your laptop, that is egress and time.

Lab 3's stub asks you which you wrote. **Question 3.**

<!--
Flag it; do not tell them which is which. Note who writes it as a download and raise it next week — their own answer to question 3 is worth more.
-->

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">1:35 – 1:50</span>

# Quiz 3

Weeks 3–5

---

<!-- _class: block -->

<span class="min">10 minutes</span><span class="clock">1:50 – 2:00</span>

# Discussion

Argue the bad case

---

## Two teams. Both are wrong.

**Team 1** argues that **job records** belong in object storage.

**Team 2** argues that **documents** belong in a database.

Five minutes to prepare. Then each makes its case — and the other team takes it apart.

**Write down what your opponents said.** It is the paragraph Lab 3's rubric wants.

<!--
Draw out: no query, no atomic update and a read-modify-write race for job records in a bucket; per-byte cost, record size limits and no streaming for documents in a database. Those are band B1.
Guide: "Discussion (10 min): argue the selection out loud"
-->

---

<!-- _class: block -->

<span class="min">60 minutes</span><span class="clock">2:00 – 3:00</span>

# Practical

Lab 3 Parts 1–2

---

## Part 1 — choose before you build

**Write the decision record first.** Half a page, and the single largest item in the rubric.

For documents and for job records:

1. Which abstraction, and **why** — from the access pattern, not the service name
2. What you give up by choosing it
3. What would have to change about the workload to reverse it

Then the two you **rejected**, and why.

---

<!-- _class: demo -->

## Part 2 — documents into object storage

```bash
gcloud storage buckets create "gs://${PROJECT_ID}-docapp-lab3" \
  --project="$PROJECT_ID" --location=US-CENTRAL1 \
  --uniform-bucket-level-access --public-access-prevention
```

```bash
cd application
DOCAPP_TEST_BUCKET="${PROJECT_ID}-docapp-lab3" python3 -m pytest -m lab03 -q
```

The tests are **the same contract `LocalStorage` already passes**.

<!--
gcloud auth application-default login is a DIFFERENT credential from gcloud auth login. Explain it once to the whole room, not five times individually.
Bucket names are globally unique — that is what the ${PROJECT_ID}- prefix is for.
-->

---

## Then delete `data/`

With the application running on object storage, **delete the local `data/` directory**. Restart. Fetch a document you created earlier.

Record what happened, and why.

> If your backend passes the same contract `LocalStorage` passes, you have **proved** the backends are interchangeable. That is the whole lab in one sentence.

---

## This week's work — 180 minutes

| | |
|---|---|
| Read the notes; prepare for Quiz 3 | 30 min |
| Lab 3 Parts 1–2: the decision record, then documents into Cloud Storage | 150 min |

---

<!-- _class: lead -->

# Next week

Replication, consistency, and choosing a data service

**Lab 3 due** — job records move to Firestore
