---
marp: true
theme: cloudcourse
paginate: true
footer: 'Week 12 · Partial failure, resilience and observability'
---

<!--
Deck for week 12. Derived from weeks/week-12/teaching-guide.md — that file is authoritative
for the teaching; this is what goes on the wall.

Render:  bash course/slides/render.sh 12
-->

<!-- _class: lead -->

# Partial failure, resilience and observability

## Week 12

Cloud Computing: Principles and Practice

<!--
TIMING: 180 min total — 80 concepts · 30 discussion · 60 practical · 10 break.
Guide: weeks/week-12/teaching-guide.md
THE TIGHTEST WEEK IN THE COURSE: Lab 5 and the project proposal are both due. Protect the practical hour.
Before you start: the incident-timeline handout printed (private repo, teaching-notes/). Know where proposals are being submitted.
-->

---

## Where we are

Last week the work left the request path, and duplicates became the normal case.

This week, things fail **partly** — one dependency, one hop, some of the time — and you need to know what happened without being able to watch it.

**Two deadlines this week:** Lab 5, and the project proposal.

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:00 – 0:15</span>

# Timeouts and retries, together

The multiplication nobody intends

---

<!-- _class: ask -->

## A client calls a service: 10-second timeout, three tries. That service calls another: 10-second timeout, three tries.
## How long does the outermost caller wait, worst case?

<!--
Let them work it out. The inner sequence takes up to 30 seconds, and the outer one tries that three times.
-->

---

<!-- _class: punch -->

## Nested retries multiply. Nobody designed ninety seconds. Everyone chose a sensible local policy.

---

## Two rules

1. **A timeout without a retry policy is half a decision.** So is a retry policy without a timeout.
2. **Retry at one level, not at every level** — usually the outermost one, the one that knows what the user is waiting for.

In Lab 5, the push subscription retries and **your service does not**. That is not an accident.

---

<!-- _class: block -->

<span class="min">10 minutes</span><span class="clock">0:15 – 0:25</span>

# Circuit breaking

A policy, not a library

---

## The idea

Count failures against a dependency.

Past a threshold, **stop calling it** and fail at once.

After a while, let one request through to test the water.

**It buys:** breathing room for the dependency, and your own threads stop waiting on something that will not answer.

---

<!-- _class: punch -->

## While the breaker is open, you are failing requests that might have succeeded.

<!--
That is the cost students skip. A deliberate trade, not a free optimisation — and a breaker with a badly chosen threshold is an outage generator.
-->

---

<!-- _class: block -->

<span class="min">10 minutes</span><span class="clock">0:25 – 0:35</span>

# Graceful degradation

On your own application

---

## Three failures. What should your service do?

| Fails | Still possible? | What should the API say? |
|---|---|---|
| **Firestore** unreachable | Accept documents? Accept jobs? | |
| **The bucket** unreachable | Report on existing jobs? | |
| **Processing** fails for every job | Keep accepting submissions? | |

<!--
Concrete only. Documents yes (the bucket is a different dependency); jobs no (no way to record one) — ask which status code. Existing jobs: yes.
The third has no clean answer and is the best of the three: accepting work you cannot do is sometimes right and sometimes a way of hiding an outage.
-->

---

<!-- _class: punch -->

## Degradation is a per-dependency design decision. Your `/healthz` was the first one you made.

<!--
It deliberately touches no dependency (week 2). Ask what it would mean if it did.
-->

---

<!-- _class: block -->

<span class="min">Break — 10 minutes</span><span class="clock">0:35 – 0:45</span>

# Break

---

<!-- _class: block -->

<span class="min">25 minutes</span><span class="clock">0:45 – 1:10</span>

# Logs, metrics, traces

What each answers — and what none of them does

---

## Three questions

| Question | Answer it with | Why the others fail |
|---|---|---|
| "What happened to **this** request?" | **Logs** | a metric averaged the answer away |
| "Is it getting **worse**?" | **Metrics** | you cannot see a trend in individual lines |
| "**Which hop** was slow?" | **Traces** | logs know one hop each; a metric knows none |

<!--
Do it as three questions put to the room before revealing each row.
-->

---

## The honest limits

- **Logs are expensive and unbounded.** A debug line in a hot path is a bill.
- **Metrics have already thrown away what you need.** A p99 does not say *which* request, or for whom.
- **Traces need every hop to cooperate.** One service that drops the context breaks the chain.
- **None of them tells you what a user experienced.** All three instrument the system, not the person.

---

<!-- _class: cost -->

## "Log everything, you might need it"

Cloud Logging: **50 GiB per project per month free**, then billed.

And the line you need is now in a haystack **you paid for**.

---

## You have had a trace all term

Every log line and every response has carried a `request_id` since week 2.

That is **a trace with one hop**, hand-rolled. It is why "follow one request through the logs" has been possible all along.

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">1:10 – 1:30</span>

# SLOs and error budgets

An introduction, with your own service

---

## A proposed SLO

> **99%** of job submissions succeed within **500 ms**, measured over **30 days**.

<!--
Read it out, then the question on the next slide.
-->

---

<!-- _class: ask -->

## What does 99% over thirty days permit?

<!--
About seven hours of failure a month (1% of 720 hours = 7.2). Watch the room react.
Then: would 99.9% be better? Make them cost it — what would they have to build, and who would be on call?
-->

---

<!-- _class: punch -->

## An error budget is permission to spend reliability on something else.

<!--
A team with budget left is allowed to ship. A team that has blown it should be fixing things. A number chosen without knowing what it costs is decoration.
-->

---

<!-- _class: block -->

<span class="min">30 minutes</span><span class="clock">1:30 – 2:00</span>

# Discussion

The failure timeline

---

## Read the incident, in pairs — fifteen minutes

1. What was the **first** symptom anyone could have seen, and how long before anyone saw it?
2. Which evidence did the responders have, and which did they **wish** they had?
3. Where did a retry make it **worse**?
4. What **single** piece of instrumentation would have shortened this most?

<!--
Hand out the timeline (a real public postmortem, or the private repo's teaching-notes one). Fifteen minutes in pairs, fifteen together.
-->

---

<!-- _class: punch -->

## In the practical you will run your own incident, with the logs and metrics you actually have.

<!--
Lab 5 Part 5, question 4 asks exactly question 4 about their own evidence — a large share of band B3.
-->

---

<!-- _class: block -->

<span class="min">60 minutes</span><span class="clock">2:00 – 3:00</span>

# Practical

Lab 5 Parts 3–6, ending with verified teardown

---

## Triage first — five minutes

Offline tests not green yet? **Do those, not the cloud.**

```bash
python3 -m pytest -m lab05
```

The lab's conceptual marks are in the local half, and the deadline is this week.

---

<!-- _class: demo -->

## Part 3 — the real broker

```bash
cd labs/lab-05/starter
./01-enable-apis.sh
./02-create-queue.sh          # prints a BUCKET_NAME
./03-build-push.sh
./04-deploy.sh                # TODO: one new permission
```

**Stop. Submit a job before you create the subscription.** Watch it stay `pending`.

```bash
./05-create-subscription.sh   # TODO: the push identity needs exactly one role
```

<!--
The push identity is where the session goes wrong. Two grants are needed, and the second — Pub/Sub's service agent needing token-creator permission — is not obvious. Say ONCE that the error message names the permission, and that reading it is the exercise.
-->

---

<!-- _class: cost -->

## A topic with no subscription

Those jobs are not delayed. **They are gone.**

A topic holds nothing. Only a subscription stores messages — and a subscription retaining messages for a broken consumer is the thing that **quietly eats the trial**.

---

<!-- _class: demo -->

## Part 5 — break the consumer on purpose

```bash
gcloud pubsub subscriptions update "$SUBSCRIPTION_NAME" \
  --project="$PROJECT_ID" \
  --push-endpoint="${SERVICE_URL}/tasks/does-not-exist"
```

Submit three jobs. **Record the time of every delivery attempt.** Then repair it:

```bash
gcloud pubsub subscriptions update "$SUBSCRIPTION_NAME" \
  --project="$PROJECT_ID" \
  --push-endpoint="${SERVICE_URL}/tasks/process"
```

<!--
Retries take minutes to play out. Have them write up Part 4 during the wait rather than refreshing a console. The describe / list-subscriptions / logging read commands are in the Lab 5 README, Part 5.
-->

---

<!-- _class: demo -->

## Part 6 — teardown, in the room

```bash
./06-teardown.sh
./07-verify-clean.sh
```

**The subscription goes first**, and the script does that. The subscriptions list must be empty.

<!--
RESERVE THE LAST FIFTEEN MINUTES FOR THIS, and watch it happen. Then take the proposals as they leave, or confirm where they are submitted. Two deadlines in one week is how one silently slips.
-->

---

## This week's work — 180 minutes

| | |
|---|---|
| Read the notes | 15 min |
| Lab 5: the real broker, duplicates, the failure experiment, teardown | 135 min |
| The project proposal | 30 min |

**Lab 5 and the proposal are both due at the end of this week.**

---

<!-- _class: lead -->

# Next week

Infrastructure as code, environments, and delivery pipelines

**Quiz 6** · **Lab 6** — one week · **project design review**

<!--
Week 13 is the last teaching week. Bring the proposal: the design review runs against it.
-->
