# Week 11 — Teaching guide: Partial failure, resilience and observability

| | |
|---|---|
| **Outcomes** | CLO-5, CLO-6 |
| **Assessment** | — (**Lab 5 and the project proposal both due**) |
| **Practical** | Lab 5 Parts 3–6 |
| **Prep time** | ~3.5 h first delivery, ~1 h subsequently |

## Session objectives

1. Explain how a timeout and a retry interact, and why choosing one without the other is a
   bug.
2. Describe circuit breaking as a policy, and say what it protects and what it costs.
3. Give a concrete degradation for a stated dependency failure.
4. Say what logs, metrics and traces each answer, and which question each cannot.
5. State an SLO for the course application and say what its error budget permits.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| Timeouts and retries together | 15 | The multiplication nobody intends |
| Circuit breaking | 10 | A policy, not a library. What it costs. |
| Graceful degradation | 10 | Worked examples on their own application |
| Break | 10 | |
| **Logs, metrics, traces** | 25 | What each answers. What none of them answers. |
| SLOs and error budgets | 20 | An introduction, with their own service as the example |
| **Discussion: the failure timeline** | 30 | Read a real incident; find the missing evidence |
| Practical | 60 | Lab 5 Parts 3–6, ending with verified teardown |

**180 minutes exactly.** 80 concepts · 30 discussion · 60 practical, plus the break.

> **This is the tightest week in the course.** Lab 5 and the project proposal are both due.
> Protect the practical hour: it is the only supervised time students get for the failure
> experiment, and the teardown at the end of it is what keeps the trial alive to week 15.

## Teaching notes

### Timeouts and retries multiply

Start with an arithmetic ambush. A client calls a service with a 10-second timeout and
retries three times. The service calls another with a 10-second timeout and retries three
times.

Ask how long the outermost caller waits, worst case. Let them work it out: the inner
sequence can take 30 seconds, and the outer one retries that three times.

> **Nested retries multiply.** Nobody designed ninety seconds. Everyone chose a sensible
> local policy.

Two rules follow, and they are worth writing down:

- **A timeout without a retry policy is half a decision.** So is a retry policy without a
  timeout.
- **Retry at one level, not at every level.** Usually the outermost one that knows what the
  user is waiting for.

Then connect to Lab 5: their push subscription retries. Their service does not retry
internally. That is not an accident, and it is worth saying so out loud.

### Circuit breaking, as a policy

Keep this short and resist the urge to make it a library. The idea: count failures against a
dependency; past a threshold, stop calling it and fail immediately; after a while, let one
request through to test the water.

Ask what it buys: the struggling dependency gets breathing room, and your own threads stop
being consumed waiting for something that will not answer.

Then ask what it costs, which is the part students skip: **while the breaker is open you are
failing requests that might have succeeded.** That is a deliberate trade, not a free
optimisation, and a breaker with a badly chosen threshold is an outage generator.

### Graceful degradation, on their own application

Concrete only. Put three failures up and ask for the degraded behaviour of *their* service:

- **Firestore is unreachable.** Can you still accept documents? (Yes — the bucket is a
  different dependency.) Can you accept jobs? (No: no way to record one.) What should the
  API return, and what status code?
- **The bucket is unreachable.** Can you still report on existing jobs? (Yes.)
- **Processing is failing for every job.** Should submission keep succeeding? This one has no
  clean answer and is the best of the three — accepting work you cannot do is sometimes
  right and sometimes a way of hiding an outage.

The useful conclusion: **degradation is a per-dependency design decision**, and the fact that
their `/healthz` deliberately touches no dependency (week 2) was the first one they made.

### Logs, metrics and traces — what each cannot tell you

The block students remember. Do it as three questions:

| Question | Answer it with | Why the others fail |
|---|---|---|
| "What happened to *this* request?" | **Logs** | A metric averaged the answer away |
| "Is it getting worse?" | **Metrics** | You cannot see a trend in individual lines |
| "Which hop was slow?" | **Traces** | Logs know one hop each; a metric knows none |

Then the honest limits, which matter more than the taxonomy:

- **Logs are expensive and unbounded.** 50 GiB/month free, then not. A debug line in a hot
  path is a bill.
- **Metrics have already thrown away what you need.** A p99 does not tell you *which*
  request, or for whom.
- **Traces need every hop to cooperate.** One service that drops the context breaks the
  chain.
- **None of them tells you what a user experienced.** All three are instrumentation of the
  system, not of the person.

Then show them theirs: the application has emitted a `request_id` on every log line and every
response since week 2. That is a trace with one hop, hand-rolled, and it is why "follow one
request through the logs" has been possible all term.

### SLOs and error budgets, introduced only

Definitions, then straight to their own service. Propose: *99% of job submissions succeed
within 500 ms, measured over 30 days.* Ask what that permits — about seven hours of failure a
month — and watch the room react. Then ask whether 99.9% would be better, and make them cost
it: what would they have to build, and who would be on call?

> **An error budget is permission to spend reliability on something else.** A team with
> budget left is allowed to ship. A team that has blown it should be fixing things.

For this course, the useful conclusion is that a number chosen without knowing what it costs
is decoration.

---

## Discussion (30 min): the failure timeline

Hand out a short incident timeline — a real public postmortem, or the one in the private
repo's teaching notes. Four questions, in pairs, fifteen minutes, then fifteen together:

1. What was the **first** symptom anyone could have seen, and how long before anyone saw it?
2. Which evidence did the responders have, and which did they wish they had?
3. Where did a retry make it worse?
4. What single piece of instrumentation would have shortened this most?

Then the turn that makes it their problem: **they are about to run their own incident**, in
Lab 5 Part 5, with the logs and metrics they actually have. Question 4 of that part asks
exactly this question about their own evidence, and it is worth a large share of band B3.

---

## Common misconceptions

| Misconception | Surfaces as | Response |
|---|---|---|
| "We have retries, so we're resilient" | Constantly | Retries turn a brief failure into a long one if the timeouts are wrong. |
| "Set a generous timeout to be safe" | Timeout block | Generous timeouts hold your threads hostage to someone else's outage. |
| "A circuit breaker prevents failures" | Breaker block | It *causes* failures, deliberately, to prevent worse ones. |
| "Health check means healthy" | Degradation block | Theirs checks nothing downstream, on purpose. Ask what it would mean if it did. |
| "Log everything, you might need it" | Observability block | 50 GiB free, then billed. And the line you need is now in a haystack you paid for. |
| "The p99 tells us what users see" | Metrics block | It tells you about requests. Users have sessions. |
| "Dead-lettered means handled" | Lab 5 Part 5 | It means the broker stopped trying. Nobody has looked. |
| "99.9% is obviously better than 99%" | SLO block | It is nine times less downtime and many times more work. Cost it first. |

---

## Practical (60 min): Lab 5 Parts 3–6

- **Triage first, for five minutes.** Anyone whose offline tests are not green does those,
  not the cloud. The lab's conceptual marks are in the local half and the deadline is this
  week.
- **The push identity is where the session will go wrong.** Two grants are needed, and the
  second — Pub/Sub's service agent needing token-creator permission — is not obvious. Say
  once, to the room, that the error message names the permission, and that reading it is the
  exercise.
- **Part 5 produces waiting.** Retries take minutes to play out. Have them write up Part 4
  during it rather than refreshing a console.
- **Reserve the last fifteen minutes for teardown, and watch it happen.** `06-teardown.sh`
  then `07-verify-clean.sh`, subscriptions list empty, in the room. This is the last billable
  lab and a retained subscription is the one thing here that quietly eats the trial.
- **Take the proposals** as they leave, or confirm where they are being submitted. Two
  deadlines in one week is how one of them silently slips.

## Links

- Student notes: `weeks/week-11/student-notes.md`
- Lab: `labs/lab-05/README.md` · Rubric: `labs/lab-05/rubric.md`
- Project: `project/brief.md` · `project/milestones.md`
- Incident timeline handout and the model discussion: private repo, `teaching-notes/`
- Solutions and the mistake list: private repo, `lab-solutions/lab-05/`
