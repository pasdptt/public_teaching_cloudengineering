---
marp: true
theme: cloudcourse
paginate: true
footer: 'Week 11 · Queues and event-driven processing'
---

<!--
Deck for week 11. Derived from course/teaching-guides/week-11.md — that file is authoritative
for the teaching; this is what goes on the wall.

Render:  bash course/slides/render.sh 11
-->

<!-- _class: lead -->

# Queues and event-driven processing

## Week 11

Cloud Computing: Principles and Practice

<!--
TIMING: 180 min total — 95 concepts · 15 quiz · 60 practical · 10 break.
Guide: course/teaching-guides/week-11.md
Before you start: Quiz 5 printed. A student's Lab 4 table, with permission, ready to project. application/docapp/service.py open at run_job. weeks/week-11/project/brief.md ready to release in the last ten minutes.
-->

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:00 – 0:15</span>

# Taking work off the request path

Starting from your own Lab 4 numbers

---

<!-- _class: ask -->

## Your service spent 250&nbsp;ms on every request.
## What was it doing?

<!--
Project a student's Lab 4 table. Answer: waiting.
-->

---

<!-- _class: punch -->

## Every user of this service waits for work that has nothing to do with answering them.

---

<!-- _class: ask -->

## The processing now takes thirty seconds.
## What do you do?

<!--
They will say "add more instances". Let it sit. Then: that does not reduce anyone's wait by a millisecond — it buys more places to wait. Scaling is capacity; this is latency.
-->

---

## The honest cost, first

Put the slow work behind a queue and the request returns at once.

**The client stops being told the answer.**

Every complication in this lab follows from that one sentence. A queue is not free performance.

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">0:15 – 0:35</span>

# Delivery guarantees

In order of increasing honesty

---

## Three claims

| Guarantee | Never | Sometimes | Fine for |
|---|---|---|---|
| **At-most-once** | duplicated | **lost** | a metric sample — not a payment |
| **At-least-once** | lost | **duplicated** | almost everything; what you actually get |
| **"Exactly-once"** | — | — | read the conditions |

<!--
Make them argue about which they would want before unpacking the third.
-->

---

## What "exactly-once" really offers

At-least-once delivery, **plus deduplication inside a specific boundary** — usually with conditions, usually at a cost.

The moment your side effect leaves that boundary — a bucket write, a card charge, an email — **you are back to at-least-once.**

---

<!-- _class: punch -->

## "Exactly-once" is at-least-once with somebody else doing the idempotency for you, inside a boundary you should know the edges of.

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">0:35 – 0:55</span>

# Duplicates are the normal case

Where the second delivery comes from

---

## Receive, work, acknowledge — and fail at each step

| The consumer… | The broker heard | So it | Result |
|---|---|---|---|
| crashes before the work | nothing | redelivers | correct |
| crashes after the work, before the ack | nothing | redelivers | **the work is done twice** |
| acks, but the ack is lost | nothing | redelivers | **the work is done twice** |

<!--
Walk it through concretely, one row at a time. Students accept "it might duplicate" and never ask why, which makes it feel like a defect a better product would avoid.
Guide: "Where the second delivery comes from"
-->

---

<!-- _class: ask -->

## Dead, slow, or ack in flight.
## Where have you met this before?

<!--
Week 3: slow versus dead. The broker cannot distinguish them. Landing that callback IS the point of this block.
-->

---

<!-- _class: punch -->

## The broker cannot tell "the consumer died" from "the consumer is slow". That is week 3's problem, in a different costume.

---

<!-- _class: block -->

<span class="min">Break — 10 minutes</span><span class="clock">0:55 – 1:05</span>

# Break

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">1:05 – 1:25</span>

# Retries, backoff, dead letters

The only response to an ambiguous failure — and its trap

---

<!-- _class: ask -->

## A hundred clients retry a struggling service immediately, all at once.
## What happens next?

<!--
Draw it: the service gets slow, everyone retries, load doubles, it gets slower.
-->

---

<!-- _class: punch -->

## A retry storm is a positive feedback loop.

<!--
Week 10's control-loop language is right there to reuse.
-->

---

## Backoff, and jitter

**Exponential backoff:** wait longer after each failure.

**Jitter:** randomise the wait.

Jitter is not decoration. **Synchronised retries are the problem**, so desynchronising them is the fix.

---

## Dead letters

After N attempts, stop — and put the message somewhere a human can look.

<!--
Keep it brief. Then the question on the next slide.
-->

---

<!-- _class: cost -->

## A dead-letter topic nobody reads

Is worth **nothing**.

And it **still costs storage**.

<!--
Lab 5's teardown lesson, arriving early.
-->

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">1:25 – 1:45</span>

# Idempotency

A test, not a word

---

<!-- _class: punch -->

## Can I run this twice and end up in the same state as running it once?

---

## Go round the room

| Operation | Idempotent? |
|---|---|
| `DELETE /documents/{id}` | |
| `POST /jobs` with an idempotency key | |
| `POST /jobs` without one | |
| "Add 100 to the balance" | |
| "Set the balance to 400" | |
| Send an email | |

<!--
Fill it in aloud. Yes (and their code does this deliberately) · yes · no · no · yes · no, and no amount of cleverness makes it so.
-->

---

<!-- _class: demo -->

## `run_job`, in `service.py`

```python
job = self.jobs.get(job_id)

if job.is_terminal:
    self.counters.duplicate_deliveries_skipped += 1
    return job

job.status = RUNNING
job.attempts += 1
self.jobs.put(job)
```

<!--
Project the real file. Ask which lines provide the property. They will find the terminal-state check.
-->

---

<!-- _class: ask -->

## Two instances, two copies of the message, the same instant — and the job is not terminal yet.
## What happens?

<!--
Both proceed. Read, gap, write: the same check-then-act race they found in create_job in week 7.
DO NOT FIX IT. Lab 5 asks them to describe it. The fix is a conditional write — week 7's transaction material. Name the connection; do not teach new content.
-->

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">1:45 – 2:00</span>

# Quiz 5

Weeks 7, 9 and 10

<!--
CLO-5, CLO-6 (introductory). Stateless execution and measurement, including Lab 4. Today's queue material is not assessed. Key in the private repository.
-->

---

<!-- _class: block -->

<span class="min">60 minutes</span><span class="clock">2:00 – 3:00</span>

# Practical

Lab 5 Parts 0–2, and the project brief

---

## No cloud account today

Parts 0–2 run entirely on your laptop. **That is deliberate.**

The ideas in this lab are in the local half. Fighting IAM today would teach you the wrong subject.

**Part 0 first** — five predictions, written before anything runs, and collected.

---

<!-- _class: demo -->

## Part 1 — make the duplicates happen

```bash
cd application
DOCAPP_QUEUE=thread DOCAPP_QUEUE_DUPLICATE_PERCENT=100 \
DOCAPP_PROCESSING_DELAY_MS=1000 python3 -m docapp
```

Submit a job: **`"status": "pending"`**. Wait two seconds, then:

```bash
curl -s localhost:8080/stats | python3 -m json.tool
```

<!--
Run it together, from the front, once. jobs_processed: 1 beside duplicate_deliveries_skipped: 1 is the whole week on one screen. The submit commands are in the Lab 5 README, Part 1.
-->

---

<!-- _class: demo -->

## Now delete the check, and watch it fail

In a **scratch copy**, delete the terminal-state check in `run_job`. Then:

```bash
python3 -m pytest tests/test_threadqueue.py -v
```

`test_duplicate_delivery_does_not_do_the_work_twice` fails. Ninety seconds, and worth more than any explanation.

---

<!-- _class: demo -->

## Part 2 — the envelope

Implement `decode_push_envelope` in `docapp/pubsub_queue.py`.

```bash
python3 -m pytest -m lab05
```

Get all **fourteen** offline tests green before you create a single cloud resource.

The payload is **base64-encoded**. Find that out here, in two seconds — not as a 404 from a real broker.

<!--
The base64 trap catches about half the room. Push them to finish all fourteen in the session.
-->

---

## The project brief — released today

Read `weeks/week-11/project/brief.md` and `weeks/week-11/project/milestones.md` this week.

- The deployment path **comes from Lab 6**. Do not rebuild it.
- **The proposal is due at the end of week 12**, with Lab 5 — the tightest week in the course.
- The proposal is **deliberately short**.

<!--
Last ten minutes. Read the scope constraints aloud.
-->

---

## This week's work — 180 minutes

| | |
|---|---|
| Read the notes | 30 min |
| Lab 5 first half: local queue, duplicates, the envelope | 130 min |
| Read the project brief; think about scope | 20 min |

---

<!-- _class: lead -->

# Next week

Partial failure, resilience and observability

**Lab 5 due** · **project proposal due** — the same week

<!--
Say it again: two deadlines in one week. Start the proposal now.
-->
