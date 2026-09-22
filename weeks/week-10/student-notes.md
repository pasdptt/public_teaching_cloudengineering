# Week 10 — Queues and event-driven processing

**Quiz 5 this week** (weeks 7–9). **Lab 5 starts. The project brief is released.**

---

## The problem with waiting

Your service does 250 ms of work for every job, and the user waits for all of it. In Lab 4
you scaled it, and every user still waited 250 ms. Scaling bought more places to wait.

That is fine at 250 ms. It is not fine at thirty seconds, and it is a disaster when the work
depends on something slow that you do not control.

So take the work off the request path. The request writes down what needs doing and returns;
something else picks it up and does it. The user gets an answer in milliseconds.

**And immediately loses something.** The response no longer contains the result. It contains
a receipt. Everything else in this week follows from that one change, and it is worth
resisting the urge to call it free.

## What a queue actually promises

A queue is a place to put a message so that something else can take it out later. What
matters is the **delivery guarantee**, and there are three claims you will meet.

**At-most-once.** Never delivered twice, sometimes not delivered at all. Acceptable for a
temperature reading. Not for a payment.

**At-least-once.** Never lost, sometimes delivered more than once. **This is what almost
everything gives you**, including Pub/Sub, and it is what Lab 5 is about.

**"Exactly-once."** Read this claim carefully whenever you see it. What is on offer is
at-least-once delivery plus deduplication inside a specific boundary — usually one broker,
one subscription, one time window, often at extra cost. The moment your side effect leaves
that boundary you are back where you started:

> **"Exactly-once" is at-least-once with somebody else doing the idempotency for you, inside
> a boundary whose edges you should know.**

If processing a job writes to a bucket, no broker guarantee covers that write.

## Why the second delivery happens

It is not a defect, and no product avoids it. Follow one message:

1. The broker hands the message to a consumer.
2. The consumer does the work.
3. The consumer acknowledges the message.
4. The broker deletes it.

Now break it in three places:

- Consumer crashes **before** step 2. The broker heard nothing, so it redelivers. Correct.
- Consumer crashes **after** step 2, before step 3. The broker heard nothing, so it
  redelivers. **The work is done twice.**
- The ack from step 3 is lost in the network. Same.

From the broker's side these are identical. It cannot tell "the consumer died" from "the
consumer is slow" from "the ack is on its way".

If that feels familiar, it should: it is week 3's **slow versus dead** problem wearing a
different hat. The broker has to choose between losing work and doubling it, and it chooses
doubling, because you can defend against doubling.

## Retries, and the storm

A retry is the only available response to an ambiguous failure. But consider a hundred
clients retrying a struggling service immediately:

The service slows → everyone retries → load doubles → it slows more → they retry again.

**A retry storm is a positive feedback loop**, and your retries are what feed it. Same shape
as week 9's autoscaler overshoot, with worse manners.

Two things fix it, and you need both:

- **Exponential backoff.** Wait 1 s, then 2, then 4, then 8. Each retry gives the service
  more room than the last.
- **Jitter.** Randomise the wait. Without it, a hundred clients that failed together retry
  together forever — you have made the herd politer, not smaller.

And a retry budget: after N attempts, stop. Which brings us to the last stop.

## Dead letters

After N failed deliveries, the broker moves the message to a **dead-letter** destination
instead of retrying forever. That is a decision to stop trying, and it is the right one: a
message that has failed five times is unlikely to succeed on the sixth, and retrying it
forever costs money and hides the problem.

But be clear about what it does:

> Dead-lettering **stops the retrying**. It does not handle anything. A dead-letter topic
> nobody reads is a place where failures go to be forgotten, and it still costs storage.

## Idempotency: the property that makes all of this safe

Everything above leads to one requirement. If a message can arrive twice, processing it
twice must be harmless.

The definition is short and the test is shorter:

> **Can I run this twice and end up in the same state as running it once?**

Work through some:

| Operation | Idempotent? | Why |
|---|---|---|
| `DELETE /documents/{id}` | Yes | Already gone is the desired state. Your code does this on purpose. |
| `POST /jobs` with an idempotency key | Yes | The second call finds the first job and returns it |
| `POST /jobs` without a key | **No** | Two jobs, two lots of work |
| "Add 100 to the balance" | **No** | Twice is 200 |
| "Set the balance to 400" | Yes | |
| "Send the email" | **No** | And no amount of cleverness makes it so |

Note the pattern: describing a **desired end state** tends to be idempotent; describing a
**change** tends not to be. That observation comes back in week 12, when Terraform turns out
to be the same idea applied to infrastructure.

### Your application already does this

Look at `run_job` in `docapp/service.py`. Near the top:

```python
if job.is_terminal:
    self.counters.duplicate_deliveries_skipped += 1
    return job
```

That is it. That is the whole defence, it has been there since week 2, and in Lab 5 you will
watch it earn its place: every message delivered twice, the work done once.

Then delete those lines in a scratch copy and run
`pytest tests/test_threadqueue.py`. Watching a test fail is a better way to understand what
it protects than any amount of reading.

### Where it is not enough

Two instances. Two copies of the message. Both arrive at the same instant. Both read the job,
both see it is not terminal, both start working.

The check is a read followed by a write with a gap in between — the **check-then-act** race
you found in `service.py` in week 7. The fix is a conditional write, which is exactly what a
transaction is for.

Lab 5 asks you to *describe* this, not fix it. Being able to see a race you are not going to
fix, and say what fixing it would cost, is a more useful skill than fixing it.

## What transfers, and what does not

**Transfers everywhere:** delivery guarantees, at-least-once as the practical default, the
ack window and why it creates duplicates, backoff with jitter, dead-lettering, and
idempotency as the property that makes retries safe.

**Does not transfer:** push versus pull, the envelope format, the flag names, the retention
defaults, the dead-letter configuration.

## This week's work (~180 minutes)

| | |
|---|---|
| Read these notes; prepare for Quiz 5 (weeks 7–9) | 30 min |
| Lab 5 Parts 0–2 — all of it on your laptop, no cloud account | 130 min |
| Read the project brief and think about scope | 20 min |

Parts 0–2 need nothing but Python. Get the fourteen offline tests green before you create a
single cloud resource next week; the base64 bug is much cheaper to find here.

## Check yourself

1. A queue does not make the work faster. What does it change?
2. What does the client lose when submission becomes asynchronous?
3. Explain at-least-once by tracing an ack that gets lost.
4. Someone offers you exactly-once. What two questions do you ask?
5. Why is jitter not optional in a retry policy?
6. Give three operations that are idempotent and three that are not. What is the pattern?
7. Which lines of `run_job` make duplicate delivery safe, and what exactly do they check?
8. Describe the interleaving that defeats them. What would fixing it require?
9. What is a dead-letter topic for, and what is one worth if nobody reads it?

## Next week

What to do when part of the system is broken but not gone: timeouts, circuit breaking,
graceful degradation — and how you would even know, which is logs, metrics and traces. You
finish Lab 5 by breaking it on purpose and explaining the evidence.

**Lab 5 and the project proposal are both due at the end of next week.** It is the tightest
week in the course. The proposal is deliberately short; start thinking about scope now.
