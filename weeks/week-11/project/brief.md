# Integrative project — brief

**Released in week 11.** Proposal due at the end of week 12 · design review in week 13 · built
in weeks 13–15 · demonstrated, submitted and torn down in week 15. Dates and deliverables per
week are in [`milestones.md`](milestones.md); how it is marked is in [`rubric.md`](rubric.md).

**Worth 30%.** Alone or in a pair, two at most. The minimum project is scoped for **one person**.

---

## What you are doing

You take the application you have built all term and make it meet a **stated workload**
safely, reliably and cheaply. Then you show, with your own measurements, what it does and
what it does not do, and you defend your decisions to someone who asks hard questions.

This is not a new build. By week 13 you will have a stateless service with external state, an
asynchronous path, a Terraform configuration with `dev` and `prod`, and a pipeline that
deploys it without a stored key. The project **uses all of that**. What you add is one
extension, a stated workload, one experiment you run and one you design, and the reasoning.

> **A project that rebuilds the pipeline, rewrites the application, or adds services to look
> impressive has been scoped wrong.** Marks come from evidence and explanation. More services
> and more spend earn nothing. Between two designs that meet the requirement, the cheaper one is
> the better answer, and you should say so.

## The time you have

The project gets the same weekly budget as a lab, and no more
([`course/workload-budget.md`](../../../course/workload-budget.md)):

| When | Minutes | For |
|---|---|---|
| Week 11 | 20 | Read this brief and think about scope |
| Week 12 | 30 | The proposal, which is deliberately short |
| Week 13 | — | Lab 6 takes the whole week. Your design review is in the session |
| Week 14 | 105 | Build and run your experiment, alongside final-exam revision |
| Week 15 | 150 | Finish, write up, rehearse |

That is about **five hours of independent work**, plus the design review and the peer review.
It is enough for the baseline, one small extension and **one** experiment **only because** the
delivery path already exists. If you find yourself building infrastructure, stop and ask.

> **Why one experiment, not two.** When the course's teaching was compressed to twelve weeks
> (to make room for a midterm and a final exam), the project lost about three and a half hours.
> It was simplified by the same amount rather than left to absorb it: you **run** one experiment
> and **design** the other without running it (Part 3, and `planning/decisions.md` D-69).

**Decide your smallest version early.** At the week 13 design review you will write down the
smallest version of your project that would still be worth demonstrating. If week 15 arrives
and things have gone wrong, you fall back to it. Having named it in advance makes falling back
a decision rather than a failure.

---

## Part 1 — The baseline every project meets

Seven requirements. Each is stated as something a marker can check.

### B1. A stated workload

Write down who uses the system and how much. For example: *"A faculty office of 30 staff
submits about 200 documents a working day, with a peak of 40 in the first hour after a
deadline. Status is checked about five times per job."*

That example is **ILLUSTRATIVE — NOT A REQUIREMENT**. Choose your own numbers and say where they
came from. Everything else depends on this paragraph: your cost model is priced against it,
your experiments are sized from it, and your SLO is set for it.

A workload you made up is fine, as long as you say it is made up. A workload you cannot state
has no cost and no pass mark.

### B2. Deployed through the Lab 6 path, to `dev` and `prod`

The system is deployed by the pipeline you built in Lab 6, from the same Terraform
configuration, to both environments. The same image digest runs in both.

List every difference between `dev` and `prod` in a table, with a one-sentence reason for each.
A difference you did not choose is a bug, not a detail. The shared Firestore database is one
such compromise. Say what it risks for *your* extension.

### B3. Security you can state

- The service is **not public**. Only identities you name may invoke it.
- Every principal in the system is listed with what it is allowed to do, and why it needs that
  and nothing more. That includes the deployer account, which by now is very powerful, and what
  you did about it, even if the answer is "nothing, and here is why".
- **No long-lived credential exists anywhere**: no key file, no key in a repository secret.
- Buckets have uniform access and public access prevention.

### B4. A reliability target, with a failure you have watched

State one SLI and an SLO for it, sized to your workload (B1): *"99% of job submissions accepted
within 500 ms, over 30 days"*. Work out the error budget in hours and minutes.

Then use your failure experiment (Part 3) — the one you ran, or the one you designed — to say
whether your system would have met that target during it. If you only designed it, say what
your prediction implies for the error budget, and what result would prove you wrong.

### B5. A cost model tied to the workload

Price your system **at the workload in B1**, and again at ten times that workload, from
published rates ([`operations/cost-model.md`](../../../operations/cost-model.md) §1). Show the
arithmetic and state every assumption.

Then answer the question from the week 14 reading: **what is the most expensive thing a bug in this system
could do overnight, and what bounds it?** Name the actual setting (an instance cap, a retry
limit, a quota), not a hope.

The project must be **free-tier-first**. A design that needs a paid resource is sent back at the
design review. Expected spend is a few cents at most. If you reach $5 you have left something
running.

### B6. A cleanup path that is verified, not claimed

A written teardown order for everything the project creates, including what Terraform does not
know about (registry images, the deployer identity and federation pool, the state bucket
**last**). In week 15 you run it in the room, and the listing output goes in your submission.

### B7. What leaving would cost

Half a page. Which parts of your design would transfer to another provider unchanged, which are
commitments to this one (be specific to what you built), and roughly **how many weeks** a move
would take, with the piece that dominates. This is analysis, not deployment: no second cloud
account is needed or wanted.

---

## Part 2 — Choose one extension

Each option below grows out of something an earlier lab asked you to **describe but not
build**. Choose one. Each is small in code and large in what there is to explain, which is
deliberate.

For each, the question in *italics* is the kind your performance or failure experiment could
answer. You are not required to use it, but your experiment must answer *some* question with a
measurable answer.

### A. Close the race

Weeks 7 and 11 showed you the **check-then-act race** in job submission: two requests with the
same idempotency key can both look, both find nothing, and both create a job. Lab 5 asked you to
describe it and not fix it. Fix it, using the concept week 7 named, and prove the fix.

*How many duplicates does a burst of concurrent same-key submissions create before and after,
and what does the fix cost in latency?*

**Watch out for:** a test that passes because it never actually overlapped two requests. You
need evidence that the race was really exercised.

### B. Make dead letters worth something

In Lab 5, messages that failed repeatedly went to a dead-letter topic, and nothing read it.
Lab 5 asked what you would have to build to make that topic useful. Build the smallest version:
a failed job's **record** should end up saying it failed and why, instead of staying "queued"
forever.

*When a poison message arrives, how long until the user can see that their job failed, and does
anything else slow down meanwhile?*

**Watch out for:** retrying dead letters automatically, which rebuilds the retry storm you were
protecting against.

### C. Work that computes

The application's processing is a `sleep`, so it waits and does not compute, and week 10 warned
you not to generalise from it. Add one operation that genuinely uses the CPU for a controllable
amount of time, and find out how the concurrency setting should change for it.

*For work that computes rather than waits, how do latency and instance count change as
per-instance concurrency goes from 1 upwards, and where is the knee?*

**Watch out for:** comparing a computing workload against a waiting one without holding
everything else fixed. The comparison is the result, so it has to be fair.

### D. Protect the service from its callers

`--max-instances` bounds your bill, but it does nothing about which callers get served when you
reach it. Decide how the system should behave when demand exceeds the capacity you are willing
to pay for, implement that behaviour, and make it **honest**: the caller should be able to tell
"try later" from "you made a mistake".

*Under load beyond your cap, what fraction of callers get a fast, honest refusal instead of a
slow timeout, and what does that do to the callers who are served?*

**Watch out for:** where the limit's state lives. A limit held inside one instance is not a
limit once there are several, and you have seen that bug before.

### E. Your own

You may propose something else. It must fit the same shape:

- It extends the course application and reuses the Lab 6 delivery path.
- It is small enough for one person in the time above.
- It stays inside the free tier.
- It lets you ask a question with a measurable answer.

Own proposals are approved or cut down at the design review. **Not accepted:** Kubernetes,
multi-region or multi-provider deployment, canary or blue-green release machinery, a second
cloud project, or anything whose main content is a new service rather than a new behaviour.
These are outside what the course prepares you to do honestly in the time
([`course/learning-outcomes.md`](../../../course/learning-outcomes.md), "Outcomes deliberately
excluded").

---

## Part 3 — One experiment run, one designed

You choose **which** of the two below you run. Choose the one that answers the more important
question about your extension or your workload (B1), and say why in a sentence.

The one you **run** follows the rules you have used since Lab 4: **predict first**, change one
variable, state the conditions, repeat at least three times, report disagreement rather than
averaging it away, and say what the result cannot tell you.

The one you **design** is written to the same standard but not executed: the question, your
prediction and the mechanism behind it, the method exactly as you would run it (commands and
configuration), its bounds (request count, instance cap, expected cost), and **the result that
would make you change a decision**. A design someone else could run from your page, unchanged,
is a good one.

**1. A performance experiment.** Load against the deployed system, sized from your workload
(B1). Answers a question about your extension or about whether the system meets B1.

**2. A controlled failure and recovery experiment.** Break one thing on purpose, in a way you can
undo: make a dependency unreachable, make processing fail, remove a permission. Record what the
system and the user saw, how it recovered, and **what state things were left in**. Say whether
your SLO (B4) would have survived it.

A failure experiment that shows your system behaving badly, explained well, is a good result.
An experiment that did not go as predicted earns full analysis marks when the evidence is real
and the reasoning is sound.

> **Fabricated measurements earn zero for the project and are an academic-integrity matter.**
> That includes numbers you "would have got", numbers from someone else's run presented as
> yours, and numbers produced by an AI tool. There is no partial credit for a plausible
> invention.

Keep the experiments bounded: small request counts, short runs, an instance cap in place. The
point is a defensible answer, not a large one.

---

## What you submit

Everything below is listed in [`course/assessment-plan.md`](../../../course/assessment-plan.md);
this is the same list, in the order a marker reads it. **Where to submit is announced by the
instructor.**

1. **Architecture diagram** and a **short decision record**: the decisions that mattered, what
   you rejected, and the condition under which the rejected option would have won.
2. **Workload statement** (B1).
3. **Extension**: what you built, and what you reused. Link the commits.
4. **`dev`/`prod` differences table** (B2) and **principals table** (B3).
5. **Experiments**: for the one you ran — prediction, method (commands and configuration, not
   narration), measurements with conditions and units, explanation, and stated limits. For the
   one you designed — question, prediction and mechanism, method, bounds, and the result that
   would change a decision.
6. **SLO and error budget** (B4).
7. **Cost model** at 1× and 10× the workload, and the overnight-bug answer (B5).
8. **Migration discussion** (B7).
9. **Resource inventory and verified teardown output** (B6), from week 15.
10. **Contribution record** if you are a pair.
11. **AI-assistance disclosure**, per the course policy.

Evidence means commands and their output. A screenshot may illustrate but is never the evidence
by itself.

**Length.** A marker should be able to read items 1–8 in about twenty minutes. Shorter and
clear beats longer and complete.

## The demonstration (week 15)

Up to **twelve minutes** per group, including questions: the system running, the decision that
mattered most, one experiment, then questions about your **decisions** rather than facts. If
something is broken on the day, say so at the start and spend the time on the evidence. That is
marked far better than a demonstration that avoids the part that does not work. Details:
[`weeks/week-15/student-notes.md`](../../week-15/student-notes.md).

---

## Working in a pair

- **No doubled scope.** A pair meets the same baseline and chooses one extension. What a pair
  buys is depth: a more careful experiment, a harder failure, a better explanation. It does not
  buy a second feature, and none is expected.
- **One student owns the cloud project**, and their trial pays for it. The partner gets
  named-user access with narrowly scoped roles. **No shared passwords, no shared keys, no "use my
  login"**; this is marked under security. Details:
  [`operations/cloud-access-and-fallback.md`](../../../operations/cloud-access-and-fallback.md) §5.
- **Check both trial expiry dates in week 12** and put them in the proposal. If the owner's
  trial ends first, the project stops for both of you.
- **Submit a contribution record** that both of you agree with: who decided what, and who built
  what.
- **Both of you answer an individual question** in the defence, usually about a decision one of
  you made that the other might have made differently. The individual band is marked per
  student, and partners can receive different marks.
- In week 15, the owner **revokes the partner's access**, and the submission says who did it and
  when.

## Without a cloud trial

If you have been on the local fallback path, the project is still fully available, and you are
not disadvantaged in grading. The rubric marks reasoning and evidence, and the local path
produces both.

- Build and demonstrate the extension locally. Options **A, B and D** can be exercised fully
  with the local job store and the local queue. For option **C**, the concurrency question can be
  answered on your own machine, but the autoscaling half cannot.
- Meet B2 with `terraform validate` and `plan`, not `apply`, as in the Lab 6 fallback.
- The cost model (B5) and migration discussion (B7) are identical exercises.
- Where you cannot observe something, say so explicitly. Any instructor-supplied evidence you
  use must be labelled as such, never presented as your own.

Tell the instructor in your proposal which path you are on.

---

## Rules that apply throughout

- **No marks for spending more.** Not for more services, not for a bigger instance, not for more
  credit used.
- **Cleanup is graded, and verified rather than claimed.**
- **Work you cannot explain does not earn marks**, whoever or whatever wrote it. Disclosure of
  AI assistance is required. Using it is not penalised; being unable to defend the result is.
- **Nothing that creates a long-lived credential**, and nothing committed to a public repository
  that you would not want read. A committed secret is fixed only by rotating it.

## Checklist before you submit the proposal (week 12)

- [ ] Which extension, in one sentence
- [ ] A first workload statement (B1)
- [ ] Which experiment you will run and which you will design, the question each answers, and your predictions
- [ ] What you will reuse and what you will build
- [ ] Cloud path or local path; for a pair, the owner and both trial expiry dates

That is the whole proposal. It fits on one page, and it should take thirty minutes, not three
hours. The format is in [`milestones.md`](milestones.md).
