# Week 10 — Teaching guide: Queues and event-driven processing

| | |
|---|---|
| **Outcomes** | CLO-5 |
| **Assessment** | **Quiz 5** (weeks 7–9) |
| **Practical** | Lab 5 Parts 0–2 · **project brief released** |
| **Prep time** | ~3.5 h first delivery, ~1 h subsequently |

## Session objectives

1. Say why slow work leaves the request path, and what the client gives up when it does.
2. Distinguish a queue's delivery guarantees, and explain why at-least-once is the one
   almost everything offers.
3. Explain why retries are unavoidable and what makes a naive retry dangerous.
4. Define idempotency operationally — not as a word, but as a test you could apply to a
   given operation.
5. Say what a dead-letter destination is for, and what it costs to have one.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| Taking work off the request path | 15 | Their Lab 4 numbers. What the client loses. |
| **Delivery guarantees** | 20 | At-most-once, at-least-once, "exactly-once" and why it is a lie of omission |
| **Duplicates are the normal case** | 20 | Where the second delivery actually comes from |
| Break | 10 | |
| Retries, backoff, and dead letters | 20 | The retry storm; where a message goes when it cannot succeed |
| **Idempotency** | 20 | The operational test. Their own `run_job`. |
| **Quiz 5** | 15 | Weeks 7–9 |
| Practical | 60 | Lab 5 Parts 0–2 + the project brief |

**180 minutes exactly.** 95 concepts · 15 quiz · 60 practical, plus the break.

---

## Teaching notes

### Start from their own measurement

They measured this service two weeks ago. Put a student's Lab 4 table on screen (with
permission) and ask what the 250 ms was doing. Waiting. Then:

> Every user of this service waits for work that has nothing to do with answering them.

Ask what would happen if the processing took thirty seconds. They will say "add more
instances", because that is what they just learned. Let that sit, then point out it does not
reduce anyone's wait by a millisecond — it only buys more places to wait. Scaling is about
capacity; this is about latency, and they are different problems.

Then the honest cost, before anything else: **the client stops being told the answer.** Every
complication in this lab follows from that one sentence, and putting it first stops the queue
looking like free performance.

### Delivery guarantees, in the order of increasing honesty

Three claims, and make them argue about which they would want:

- **At-most-once** — never duplicated, sometimes lost. Fine for a metric sample; not fine for
  a payment.
- **At-least-once** — never lost, sometimes duplicated. What almost everything actually gives
  you.
- **"Exactly-once"** — say the phrase, then unpack it. What is really offered is
  at-least-once delivery plus deduplication inside a specific boundary, usually with
  conditions and usually at a cost. The moment your side effect leaves that boundary — you
  write to a bucket, you charge a card, you send an email — you are back to at-least-once.

> **"Exactly-once" is at-least-once with somebody else doing the idempotency for you, inside
> a boundary you should know the edges of.**

### Where the second delivery comes from

Students accept "it might duplicate" and never ask why, which makes it feel like a defect
they could avoid by choosing a better product. Walk it through concretely:

The consumer receives a message, does the work, and acknowledges it. Now put a failure at
each step and ask what the broker knows:

- Crash before the work: broker heard nothing, redelivers. Correct.
- Crash after the work, before the ack: broker heard nothing, redelivers. **The work is
  done twice.**
- Ack sent but lost on the way back: same again.

> The broker cannot distinguish "the consumer died" from "the consumer is slow" from "the
> ack is in flight". That is week 3's slow-vs-dead problem, in a different costume.

Landing the callback to week 3 is the point of this block. They have met this before.

### Retries, backoff, dead letters

Retry is the only available response to an ambiguous failure. Then make them find the
problem: a hundred clients retrying a struggling service immediately, all at once.

Draw it: the service gets slow, everyone retries, load doubles, it gets slower. **A retry
storm is a positive feedback loop**, and week 9's control-loop language is right there to
reuse. Exponential backoff plus jitter breaks it — and be explicit that jitter is not
decoration: synchronised retries are the problem, so desynchronising them is the fix.

Then dead letters, briefly: after N attempts, stop and put the message somewhere a human can
look. Ask what a dead-letter topic is worth if nobody ever reads it. The answer is "nothing,
and it still costs storage" — which is Lab 5's teardown lesson arriving early.

### Idempotency, as a test rather than a word

Give the definition, then immediately make it operational:

> **Can I run this twice and end up in the same state as running it once?**

Go round the room with candidate operations: `DELETE /documents/{id}` (yes — and their own
code already does this deliberately). `POST /jobs` with a key (yes). `POST /jobs` without one
(no). "Add 100 to the balance" (no). "Set the balance to 400" (yes). Sending an email (no,
and no amount of cleverness makes it so).

Then their own code. Put `run_job` on screen and ask which lines provide the property. They
will find the terminal-state check. Then ask the harder question:

> Two instances, two copies of the message, arriving at the same instant, and the job is not
> terminal yet. What happens?

Both proceed. The check is a read followed by a write with a gap in the middle — the same
check-then-act race they found in `service.py` in week 7. **Do not fix it.** Lab 5 asks them
to describe it; the fix needs a conditional write, which is week 7's transaction material and
is worth naming as a connection rather than as new content.

---

## Common misconceptions

| Misconception | Surfaces as | Response |
|---|---|---|
| "A queue makes it faster" | Constantly | The work takes just as long. It happens where nobody is waiting. |
| "Exactly-once is available, we should use it" | Guarantees block | Ask where the boundary is, and what happens to your bucket write outside it. |
| "Duplicates mean something is broken" | Lab 5 Part 4 | Trace the ack. The broker cannot know you finished. |
| "We'll just retry until it works" | Retry block | Then a slow service becomes a dead one, faster. |
| "Idempotent means it does nothing the second time" | Definition block | It means the *state* is the same. It may well do work. |
| "The queue stores my messages" | Part 3 | Only a subscription holds anything. A topic with no subscriber is a hole. |
| "Dead-lettering handled the failure" | Part 5 | It stopped the retrying. Nothing has been handled until someone reads it. |
| "Pending means something is wrong" | First async run | It means the answer is not ready. This is the normal case now. |

---

## Practical (60 min): Lab 5 Parts 0–2, and the project brief

**Parts 0–2 need no cloud account at all**, and that is deliberate — the conceptual content
of this lab is in the local half, and a student who spends the session fighting IAM learns
the wrong subject.

- **Part 0 is written before anything runs**, and collected.
- **Run the duplicate demonstration together**, from the front, once:
  `DOCAPP_QUEUE=thread DOCAPP_QUEUE_DUPLICATE_PERCENT=100`. The `/stats` output showing
  `jobs_processed: 1` beside `duplicate_deliveries_skipped: 1` is the whole week in one
  screen.
- **Then have them delete the terminal-state check** in a scratch copy and run
  `pytest tests/test_threadqueue.py` again. Watching
  `test_duplicate_delivery_does_not_do_the_work_twice` fail is worth more than any
  explanation, and it takes ninety seconds.
- **Part 2 is pure functions over bytes.** Push them to get all fourteen offline tests green
  in the session. The base64 trap will catch about half the room, in two seconds, which is
  exactly where you want it caught.

**Last 10 minutes: release the project brief.** Read the scope constraints aloud, especially
that the deployment path comes from Lab 6 and is not to be rebuilt. The proposal is due at
the end of week 11, with Lab 5 — the tightest week in the course. Say so now, and say that
the proposal is deliberately short.

## Links

- Student notes: `weeks/week-10/student-notes.md`
- Lab: `labs/lab-05/README.md` · Rubric: `labs/lab-05/rubric.md`
- The local broker, with its limits in the docstring: `application/docapp/threadqueue.py`
- The behaviour, pinned as tests: `application/tests/test_threadqueue.py`
- Project: `project/brief.md` · `project/milestones.md`
- Solutions and the mistake list: private repo, `lab-solutions/lab-05/`
