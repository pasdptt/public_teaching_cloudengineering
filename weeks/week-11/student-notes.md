# Week 11 — Partial failure, resilience and observability

**Lab 5 is due this week. So is the project proposal.** No quiz.

This is the tightest week in the course. Your reading is deliberately short and the proposal
is deliberately brief — see `course/workload-budget.md`, which says exactly what was traded
for what.

---

## Partial failure is the normal condition

A single machine fails simply: it works, or it does not. A distributed system mostly runs in
a third state — **some of it is broken**, and the rest is still serving requests, possibly
badly, possibly without anyone noticing.

Your application has four dependencies now: a bucket, Firestore, a broker, and the platform
underneath. Each can be slow, unreachable, or wrong, independently. "Is it up?" stopped being
a question with an answer several weeks ago.

## Timeouts and retries are one decision, not two

A timeout is a guess about how long is too long (week 3). A retry is what you do afterwards.
Choosing either without the other is a bug you have not met yet.

Here is the arithmetic that catches everyone. A client calls your service with a 10-second
timeout and retries 3 times. Your service calls Firestore with a 10-second timeout and
retries 3 times.

Worst case, the inner sequence takes 30 seconds. The outer one retries *that* three times.
**Ninety seconds**, from two policies that each looked reasonable.

> **Nested retries multiply.** Nobody designs ninety seconds; everyone chooses a sensible
> local policy.

Two rules:

- **A timeout without a retry policy is half a decision**, and so is the reverse.
- **Retry at one level** — usually the outermost one that knows what the user is waiting for.

In Lab 5, your push subscription retries and your service does not retry internally. That is
not an oversight.

## Circuit breaking

Count failures against a dependency. Past a threshold, stop calling it and fail immediately.
After a while, let one request through to see whether it has recovered.

What it buys: the struggling dependency gets room to recover, and your own threads stop being
consumed waiting for something that is not going to answer.

What it costs, and this is the part people skip: **while the breaker is open you are failing
requests that might have succeeded.** That is a deliberate trade. A breaker with a badly
chosen threshold is not protection, it is an outage you built yourself.

## Graceful degradation

When a dependency fails, you have three options: fail the whole request, serve something
reduced, or pretend nothing happened. The third is usually wrong and always tempting.

Work it through on your own application:

| Failure | Can you still…? | Reasonable behaviour |
|---|---|---|
| Firestore unreachable | accept documents — **yes**, different dependency | Accept uploads; refuse job submission with a clear 503 |
| Firestore unreachable | accept jobs — **no**, nowhere to record one | Say so honestly rather than accepting work you will lose |
| Bucket unreachable | report on existing jobs — **yes** | Serve status; refuse new documents |
| Processing failing for every job | accept submissions — **maybe** | This one has no clean answer. Accepting work you cannot do is sometimes right and sometimes a way to hide an outage. |

Notice that these are **per-dependency** decisions. There is no global "degraded mode"; there
are specific choices about specific failures.

You made the first one in week 2 without knowing it: `/healthz` deliberately touches no
dependency. If it checked Firestore, a brief Firestore blip would make the platform believe
your instances were dead and restart perfectly healthy ones.

## How you would even know: logs, metrics, traces

Three tools, three questions, and — more usefully — three things each one cannot tell you.

| Question | Use | Because |
|---|---|---|
| "What happened to **this** request?" | **Logs** | A metric averaged that answer away |
| "Is it getting **worse**?" | **Metrics** | You cannot see a trend in individual lines |
| "**Which hop** was slow?" | **Traces** | Each log knows one hop; a metric knows none |

**Logs** — discrete events with context. Expensive: 50 GiB per project per month is free and
then it is not, so a debug line in a hot path is a recurring bill. Yours are structured JSON
on stdout, which is the format every cloud logging system wants.

**Metrics** — numbers over time, aggregated. Cheap, and the aggregation is exactly the
problem: a p99 tells you a request was slow, never which one or whose.

**Traces** — one request's journey across services, with timing per hop. The only tool that
answers "where did the time go" in a system with several components, and the most fragile:
every hop must propagate the context, and one that does not breaks the chain.

**None of them tells you what a user experienced.** All three instrument the system.

### You already have a trace, sort of

Since week 2, every request has carried a `request_id` — generated if the client did not
supply one, echoed in the `X-Request-Id` response header, and attached to every log line that
request produces. That is why "follow one request through the logs" has been possible all
term. It is a distributed trace with one hop, hand-rolled, minus the tooling.

## SLOs and error budgets

An **SLI** is a measurement: the fraction of job submissions that succeed within 500 ms. An
**SLO** is a target for it: 99%, over 30 days. The **error budget** is what is left: 1%.

Do the arithmetic, because it is always surprising. 99% over 30 days permits about **7 hours**
of failure a month. 99.9% permits about 43 minutes. 99.99% permits about 4 minutes — which
nobody achieves by being careful; it requires redundancy, automation and people on call.

The budget is the useful part:

> **An error budget is permission to spend reliability on something else.** Budget left over
> means you can ship risky things. Budget exhausted means stop shipping and fix things.

Two habits worth forming now. Measure the SLI from as close to the user as you can — a
server-side metric misses the requests that never arrived. And never pick a target without
costing it: a number chosen without knowing what it requires is decoration.

## This week's work (~180 minutes)

| | |
|---|---|
| Read these notes | 15 min |
| Lab 5 Parts 3–6, including the failure experiment and verified teardown | 135 min |
| Project proposal | 30 min |

**Both are due at the end of this week.** The proposal is short on purpose. If you are
running out of time, the thing to protect is Lab 5's teardown — an orphaned subscription
keeps costing, and the trial has to last until week 15.

## Check yourself

1. Client timeout 10 s with 3 retries, calling a service with the same policy. Worst-case
   wait? What went wrong?
2. Why is "set a generous timeout" bad advice?
3. What does an open circuit breaker cost you? Be specific.
4. Firestore is unreachable. Which of your endpoints should still work, and what should the
   others return?
5. Why does `/healthz` deliberately check nothing downstream?
6. Give a question logs answer that metrics cannot, and one metrics answer that logs cannot.
7. What breaks a distributed trace?
8. 99.5% over 30 days. How much downtime is that? Work it out rather than guessing.
9. Your error budget is spent with two weeks to go. What should the team do?

## Next week

Infrastructure stops being a set of shell scripts you maintain by hand. Declarative
provisioning, what Terraform state is, drift, and managing two environments from one
configuration — and why a secret in a repository is permanent.

**Lab 6 spans weeks 12 and 13**, and is the last lab.
