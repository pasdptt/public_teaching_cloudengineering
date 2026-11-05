---
marp: true
theme: cloudcourse
paginate: true
footer: 'Week 3 · State, latency, failure'
---

<!--
Deck for week 3. Derived from weeks/week-03/teaching-guide.md, which is authoritative.
"Slow vs dead" is the centre of the week and the centre of this deck — do not rush it to
reach the practical.

Render:  bash course/slides/render.sh 03
-->

<!-- _class: lead -->

# State, latency, failure

## Week 3

Lab 1 is due at the end of this week

<!--
TIMING: 180 min — 90 concepts · 20 discussion · 60 practical · 10 break.
Guide: weeks/week-03/teaching-guide.md
Have the application running with a document already created, for the idempotency demo.
-->

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:00 – 0:15</span>

# Crossing a machine boundary

---

## Last week everything was in one process

A function call was a function call. It succeeded, it raised, and it took nanoseconds.

Now put a network in the middle.

Three things change, and all three are permanent.

---

## 1. It got slower, by a lot

| | Roughly |
|---|---|
| Function call in-process | nanoseconds |
| Read from main memory | ~100 ns |
| Read from a local SSD | tens of µs |
| Round trip inside one datacentre | under 1 ms |
| **Round trip Bangkok ↔ Iowa** | **~200 ms** |

The last row is the speed of light in fibre plus the routers. No optimisation fixes it.

---

<!-- _class: ask -->

## Your design makes 20 sequential calls
## between Bangkok and Iowa.
## How long, before any work happens?

<!--
Do the arithmetic live: 20 × 200 ms = 4 seconds of pure waiting. Ask what to change. Steer
to FEWER, LARGER round trips — and note this is a design decision invisible in the source
code, which is why it survives code review and dies in production.
-->

---

## Why this course runs in Iowa

Someone will ask. The answer models the reasoning the course teaches:

- The free tier exists **only** in three US regions
- Every latency measurement here compares **against itself**, so a constant offset changes no conclusion
- For a real service serving Thai users, the answer would be **different**

Cost drove an architecture decision, the decision is recorded, and its downside is known.

---

## 2. It can fail in a new way

A local call returns or raises.

A remote call has a third outcome: **you never find out.**

- The request may have been lost on the way
- It may have arrived, executed perfectly, and the **response** was lost coming back

From where you stand, those two are **indistinguishable**.

---

## 3. Parts fail independently

In one process, a crash takes everything with it.

Across machines, one component can be dead while everything around it is fine — and the rest of the system has to decide what to do about that.

---

<!-- _class: block -->

<span class="min">25 minutes</span><span class="clock">0:15 – 0:40</span>

# Slow and dead look the same

The centre of the week

---

<!-- _class: punch -->

## You cannot distinguish
## a slow component from a dead one.

---

## So you wait. And then you decide.

That decision is a **timeout**, and a timeout is always a **guess**.

- Too short — you give up on work that was about to succeed
- Too long — your own caller gives up on **you**

There is no correct value. Only a trade-off you chose deliberately, or left to a default.

---

<!-- _class: ask -->

## You timed out. You retry.
## What have you just risked?

<!--
Doing it twice — the first attempt may have succeeded.
-->

---

<!-- _class: ask -->

## You timed out. You do *not* retry.
## What have you just risked?

<!--
Not doing it at all — the first attempt may have failed.
Let this sit. The discomfort here is what makes idempotency feel like a relief rather than a
technique. Do not shortcut to the answer.
Guide: "Slow vs dead is the centre of the week"
-->

---

<!-- _class: punch -->

## You cannot avoid the dilemma.
## So make doing it twice **harmless**.

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:40 – 0:55</span>

# Idempotency

The escape

---

<!-- _class: demo -->

## Send the same thing twice

```bash
curl -i -X POST http://127.0.0.1:8080/jobs \
  -H 'Content-Type: application/json' -H 'Idempotency-Key: demo' \
  -d '{"document_id":"<id>","operation":"wordcount"}'
```

First time: **201 Created**

Second time: **200 OK**, `"deduplicated": true`

```bash
curl -sS http://127.0.0.1:8080/stats     # jobs_created: 1
```

<!--
Same job, done once. The client did not have to know whether its first request arrived —
that is the whole point.
-->

---

<!-- _class: punch -->

## This has been in the application since week 2.
## Seven weeks before there is a queue to need it.

<!--
Designed in, not bolted on. That is the habit being taught, and it is worth saying out loud.
-->

---

<!-- _class: block -->

<span class="min">Break — 10 minutes</span><span class="clock">0:55 – 1:05</span>

# Break

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">1:05 – 1:25</span>

# Where state lives

---

## Two kinds, behaving differently

| | Where it lives | Survives a restart? |
|---|---|---|
| Document bytes | a directory on disk | **yes** |
| Job records | a Python dictionary | **no** |

You watched this in Lab 1 Part 3.

Both feel equally real while the process is running. Only one of them is.

---

## But there is a subtler distinction

Run the application in a container with **no volume**. Write a document. Delete the container. Start a new one.

The document is gone — even though it *was* written to a filesystem.

---

## Three levels, not two

1. **In memory** — gone when the **process** ends
2. **On disposable storage** — gone when the **container or machine** ends
3. **On storage that outlives the compute** — survives both

Only level 3 is really state.

---

<!-- _class: punch cost -->

## Level 2 is dangerous *because it works*.
## It passes every test on a laptop.

<!--
INSIST ON THIS DISTINCTION. "We wrote it to disk" is not the same claim as "it is durable".
Students who conflate in-memory with on-disposable-storage will struggle in Lab 3, and this
is the cheapest moment to catch it. Lab 3 is the fix.
-->

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">1:25 – 1:40</span>

# Stateless execution

---

## What it unlocks

Once state lives somewhere that outlives execution, the execution can be **stateless** — any instance serves any request, because it remembers nothing between them.

- **Scale horizontally** — add instances
- **Fail cheaply** — an instance dies, traffic goes elsewhere, nothing is lost
- **Deploy without drama** — stop old, start new

---

## What forecloses it

None of that works if a request handler remembers something the next request needs.

> "Put it in a variable on the server" is a decision that quietly forecloses **everything in weeks 9–12.**

---

## Failure boundaries and blast radius

A **failure boundary** is a line a failure does not cross.

A **blast radius** is how much stops when one thing does.

Ask of any design:

1. If this component dies, what else stops?
2. **Could it have been less?**

Today, the process *is* the boundary. Kill it and everything stops.

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">1:40 – 2:00</span>

# Discussion

Compare your Part 3 results

---

<!-- _class: ask -->

## Who predicted the document would survive?
## Who predicted the job record would?
## Who got the **container** case right?

<!--
The container case is where the room splits, and the split is the lesson. Draw out the
difference between "it was in memory" and "it was on storage that was itself disposable".
Then ask the question the lab does NOT: what would you change so the containerised document
survived? Let them invent volumes and object storage — weeks 6–7 then arrive as ANSWERS
rather than as topics.
-->

---

<!-- _class: block -->

<span class="min">60 minutes</span><span class="clock">2:00 – 3:00</span>

# Practical

Lab 1, Parts 4–5 — the heaviest block so far

---

<!-- _class: demo -->

## Part 4 — make job records survive

```bash
python3 -m pytest -m lab01 -q     # the specification
```

Implement `FileJobStore` in `docapp/jobstore.py`.

```bash
python3 -m pytest -m lab01 -q     # your exercise
python3 -m pytest -q              # nothing else broke
```

The four docstring questions are **worth more marks than the code**.

<!--
Expect: a lock taken twice on the same thread → the concurrency test hangs (most common by
a distance; point at the read-modify-write path, don't give the answer); get() returning None
instead of raising JobNotFound; re-reading the file on every call (passes, very slow — ask
them about it, don't fail it); forgetting to release the idempotency key on delete.
-->

---

<!-- _class: demo -->

## Part 5 — the experiment

```bash
python3 tools/measure.py --url http://127.0.0.1:8080 \
  --requests 12 --concurrency 1
python3 tools/measure.py --url http://127.0.0.1:8080 \
  --requests 12 --concurrency 4
```

**Run each three times.** Then try 8, 16, 32.

One run is one sample of a noisy system.

<!--
Watch for single runs. Insist on three. The variation between them IS the finding, and a
student who reports one run has not yet understood what a measurement is.
-->

---

<!-- _class: cost -->

## What the rubric actually weights

| Band | Marks |
|---|---|
| Working implementation | 35 |
| **Explanation and evidence** | **40** |
| Reproducibility, security, resources | 15 |
| Communication | 10 |

A perfect `FileJobStore` with a thin write-up scores **worse** than a rough one with a good analysis.

<!--
Say this out loud. It is counter to every instinct they have from other courses.
-->

---

<!-- _class: cost -->

## Before you go

**Do not activate a cloud trial before next week's session.** Ninety days must reach week 15.

Anyone expecting an eligibility or payment-method problem — **speak to me this week**, so your path starts in the same session as everyone else's.

**Next week costs real money for the first time: about four cents.**

<!--
Say the four-cent figure. It sets the tone that cost is something this course measures
rather than worries about.
Repeat the trial warning. Someone always forgets.
-->

---

## This week's work — 180 minutes

| | |
|---|---|
| Read the week 3 notes | 25 min |
| Lab 1 Parts 4–5 and the write-up | 155 min |

**Lab 1 is due at the end of this week.** The write-up is part of the work, not an extra.

---

<!-- _class: lead -->

# Next week

Cloud proper

Resource hierarchy · regions and zones · virtual machines · identity

You activate your trial **in the session**, and Lab 2 starts
