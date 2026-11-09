# Weekly schedule

Relative weeks 1–15: **twelve teaching weeks** (1–7 and 9–13), a **midterm** in week 8, and
the **final exam and project** in weeks 14–15 (D-66). Real dates come from `planning/calendar-worksheet.md` (Q-01).

Session envelope every week: **~90 min concepts · ~30 min discussion or quiz · 60 min guided
practical**, totalling the 180-minute contact block. Quizzes take discussion time, never extra
time. Most weeks also spend 10 of those minutes on a break, which comes out of the concept
allowance and leaves ~80–90 — so the per-week plans in `weeks/*/teaching-guide.md` are the
authoritative arithmetic, and `planning/audit.py` checks that each one sums to exactly 180.

Threads that run through the whole course rather than sitting in one week: identity and
least privilege, cost awareness, cleanup, and observability. Each is introduced with the
first cloud lab (week 4) and revisited, with a dedicated treatment where the table says so.

Every week links its slides twice: **present on claude.ai** opens the presentable deck, and
**Markdown source** is the file it is generated from, which is the one to edit. The claude.ai
decks are private until shared from each deck's Share menu; how they are built and republished
is in [`course/slides/README.md`](slides/README.md).

---

## Phase 1 — Local foundations (weeks 1–3, no cloud account)

### Week 1 · What makes a cloud
**Slides:** [present on claude.ai](https://claude.ai/artifact/Bc9LrKS3qQUSmKod4jhWJW) · [Markdown source](../weeks/week-01/slides.md)

**Concepts:** on-demand self-service, resource pooling, elasticity, measured service;
IaaS / PaaS / serverless by *who operates what*; shared responsibility; what "the cloud"
replaced and what problem each property solves. Introduction to the course application.
**Discussion:** given three incidents, who was responsible — provider or customer?
**Practical:** environment check (Python, container runtime, application starts, network
reachable) and first local run of the application. **Ungraded**, but every student must
actually complete it; this is how decision A-04 gets verified.
**Outcomes:** CLO-1. **Assessment:** none.

### Week 2 · Processes, isolation, virtualization, containers
**Slides:** [present on claude.ai](https://claude.ai/artifact/Kmfv5f7AJWXtaSmDkSHVQr) · [Markdown source](../weeks/week-02/slides.md)

**Concepts:** what a process is and what isolates one from another; virtual machines vs
containers — namespaces, images, layers; just-in-time coverage of ports, HTTP request
anatomy, and how a client finds a server.
**Discussion block:** **Quiz 1** (CLO-1, CLO-2).
**Practical:** start **Lab 1** — run the application in and out of a container, inspect the
boundary, observe what each side can see.
**Outcomes:** CLO-1, CLO-2.

### Week 3 · Distributed application basics
**Slides:** [present on claude.ai](https://claude.ai/artifact/S6bTkK7r4R1d1gvJoG4MGU) · [Markdown source](../weeks/week-03/slides.md)

**Concepts:** what changes when a call crosses a machine boundary — latency, partial
failure, the impossibility of distinguishing "slow" from "dead"; where state lives and why
it is the hard part; failure boundaries and blast radius.
**Discussion:** trace a request on paper, then predict what breaks if one component stops.
**Practical:** complete **Lab 1** — trace a request end to end, separate state from
execution, induce and explain a local failure, and **set up continuous integration** so the
test suite runs on every push (Lab 1 Part 6).
**Outcomes:** CLO-2, CLO-3 (foundations), CLO-5 (foundations), CLO-9 (thread begins).
**Due:** Lab 1.

> **The CI thread starts here (D-23).** Fifteen minutes of the discussion block, and about
> twenty minutes of student time. From now on every push runs the tests, and every later lab
> submits through a repository whose checks are green. Students live with a pipeline for ten
> weeks before week 13 teaches them what one is — the same pattern as meeting idempotency in
> week 2 and the queue that needs it in week 11.

---

## Phase 2 — Cloud compute, networking, identity (weeks 4–5)

### Week 4 · Cloud resource hierarchy, VMs and identity
**Slides:** [present on claude.ai](https://claude.ai/artifact/8T9hqZG8EMCS84ZpdizsH5) · [Markdown source](../weeks/week-04/slides.md)

**Concepts:** organisation/project/resource hierarchy and why billing attaches where it
does; regions and zones as failure and latency domains; the virtual machine abstraction;
identity — principals, roles, policies, service accounts; least privilege as a default,
not a hardening step.
**Discussion block:** **Quiz 2** (CLO-1, CLO-2, CLO-3 foundations).
**Practical:** **activate the GCP trial** (guided, with the eligibility and payment-method
check done openly), then start **Lab 2**. Students who cannot activate start the documented
fallback path in the same session — not later, and not in private.
**Outcomes:** CLO-1, CLO-3. **Cost/cleanup thread starts here and never stops.**

### Week 5 · Virtual networking and access boundaries
**Slides:** [present on claude.ai](https://claude.ai/artifact/AsdYRw31iwvXMdU3yeaPUd) · [Markdown source](../weeks/week-05/slides.md)

**Concepts:** virtual networks, subnets, routes; firewall rules as allow-lists; public vs
private addressing; what a load balancer actually does; least privilege applied to a
service identity rather than a human.
**Discussion:** architecture exercise — narrow an over-permissive design.
**Practical:** complete **Lab 2** — deploy the service on a small VM, restrict access,
trace the network path, explain each hop's permitting rule and acting identity, then tear
down and verify.
**Outcomes:** CLO-3. **Due:** Lab 2.

---

## Phase 3 — State and data (weeks 6–7)

### Week 6 · Storage abstractions
**Slides:** [present on claude.ai](https://claude.ai/artifact/7XQupUBwbESPSXDj2Hug3B) · [Markdown source](../weeks/week-06/slides.md)

**Concepts:** block vs file vs object vs database — the access pattern each assumes;
durability vs availability; what "eleven nines" does and does not promise; why object
storage changed application architecture.
**Discussion block:** **Quiz 3** (CLO-3, CLO-4 foundations).
**Practical:** start **Lab 3** — move stored artefacts out of the VM's local disk into
object storage.
**Outcomes:** CLO-4.

### Week 7 · Replication, consistency and choosing a data service
**Slides:** [present on claude.ai](https://claude.ai/artifact/Cb7kBoLPQRimc6FEpCyYHG) · [Markdown source](../weeks/week-07/slides.md)

**Concepts:** replication and what it buys; consistency models in plain terms and the
observable difference between them; transactions and when you need one; how to choose a
data service from the access pattern rather than from familiarity.
**Discussion:** decision exercise — same workload, three candidate stores, defend one.
**Practical:** complete **Lab 3** — externalise application state to the managed data
service and justify the design in a decision record.
**Outcomes:** CLO-4, CLO-5. **Due:** Lab 3.

---

## Mid-semester exam (week 8)

### Week 8 · Midterm examination
**Slides:** [present on claude.ai](https://claude.ai/artifact/L4KayoWqrhQsRuyHmUDeq2) · [Markdown source](../weeks/week-08/slides.md)

No new material. The midterm sits at the natural seam in the course: everything before it
runs on one machine or one VM with its state moved out, and everything after it is managed
execution, scale, asynchrony and delivery.

| Block | Time | Activity |
|---|---|---|
| Midterm examination | 120 min | Written, in the room. Weeks 1–7: CLO-1 … CLO-4, and CLO-5 foundations. Format in `exams/README.md` |
| Break | 10 min | |
| Trial and cost check | 20 min | Everyone opens their billing page and states their remaining credit and days. Anyone with a running resource from Labs 2–3 finds out why |
| Lab clinic | 30 min | Outstanding Lab 3 problems and Lab 4 pre-flight (container builds locally). No new content |

**Due:** nothing besides the exam. Lab 3 was due in week 7, and Lab 4 starts in week 9.
**Outcomes:** CLO-1 … CLO-4 (exam evidence).

> **Why week 8.** It is the only point where a full exam can sit between labs without cutting
> one in half: Lab 3 has just closed and Lab 4 has not started. The trial check rides along
> because week 8 is roughly one third of the way through the 90-day window, which is the last
> comfortable moment to find a student whose credit is draining.

---

## Phase 4 — Managed execution and scale (weeks 9–10)

### Week 9 · Managed containers and serverless
**Slides:** [present on claude.ai](https://claude.ai/artifact/V8rbrxY6wWjzJFq1NUS7Zf) · [Markdown source](../weeks/week-09/slides.md)

**Concepts:** what you stop operating when you move from VM to managed container
execution; request-scoped lifecycle; cold start and what causes it; why statelessness is
the price of admission; concurrency settings as a design decision.
**Discussion block:** **Quiz 4** (CLO-1, CLO-2, CLO-4).
**Practical:** start **Lab 4** — containerise and deploy the service to managed execution.
**Outcomes:** CLO-1, CLO-2, CLO-5.

### Week 10 · Horizontal scaling and measurement
**Slides:** [present on claude.ai](https://claude.ai/artifact/E1xW4c83h31pjPBYtXUv3m) · [Markdown source](../weeks/week-10/slides.md)

**Concepts:** vertical vs horizontal scaling; load distribution; concurrency vs
parallelism; the relationship between latency, throughput and utilisation; autoscaling as
a feedback loop with delay — and why that causes overshoot; how to design a bounded,
honest experiment.
**Discussion:** predict the shape of a latency-vs-load curve, then compare with the data.
**Practical:** complete **Lab 4** — run a bounded load experiment, compare VM and managed
execution on latency, throughput, scaling behaviour and operational responsibility.
**Outcomes:** CLO-2, CLO-5, CLO-6. **Due:** Lab 4.

---

## Phase 5 — Asynchrony, failure, delivery (weeks 11–13)

### Week 11 · Queues and event-driven processing
**Slides:** [present on claude.ai](https://claude.ai/artifact/VAGuskEQxSoeHzJzHDiW27) · [Markdown source](../weeks/week-11/slides.md)

**Concepts:** why slow work leaves the request path; queues and their delivery guarantees;
at-least-once delivery and therefore duplicates; retries, backoff and the retry storm;
idempotency as the property that makes retries safe; dead-letter handling.
**Discussion block:** **Quiz 5** (CLO-5, CLO-6 foundations).
**Practical:** start **Lab 5** — introduce a queue between submission and processing.
**Also this week:** the **project brief is released**.
**Outcomes:** CLO-5.

### Week 12 · Partial failure, resilience and observability
**Slides:** [present on claude.ai](https://claude.ai/artifact/HwiGyDnvAywGjA9fEwnqKt) · [Markdown source](../weeks/week-12/slides.md)

**Concepts:** timeouts, retries and their interaction; circuit breaking conceptually;
graceful degradation; logs vs metrics vs traces and what each answers; service level
objectives and error budgets at an introductory level.
**Discussion:** read a real failure timeline and identify what evidence was missing.
**Practical:** complete **Lab 5** — demonstrate duplicate handling and idempotency, run a
controlled failure experiment, and show the evidence you used to explain it.
**Outcomes:** CLO-5, CLO-6. **Due:** Lab 5 **and** the brief project proposal.
*(Workload note: this is the tightest week in the course. The budget in
`workload-budget.md` reallocates reading time to absorb the proposal.)*

### Week 13 · Infrastructure as code, environments and delivery pipelines
**Slides:** [present on claude.ai](https://claude.ai/artifact/3pVwsxchnKFpMtJ5KGjubM) · [Markdown source](../weeks/week-13/slides.md)

The last teaching week, and the densest. It carries what used to be two weeks (D-66).

**Concepts (75 min):** imperative vs declarative provisioning and what Terraform state is;
drift; **environment management** — one configuration, two variable files, what `dev` and
`prod` may differ in and what they must never differ in; configuration vs secrets. Then the
**pipeline**: each stage as a gate and what it protects against; build once, promote the same
artefact; why a pipeline needs an identity and why that identity must not be a long-lived key;
**Workload Identity Federation**; what a pipeline cannot catch.
**Discussion block:** **Quiz 6** (CLO-5, CLO-6; CLO-7 and CLO-9 via the threads students have
been living with — cleanup since Lab 2, CI since week 3 — never that day's Terraform material).
**Design review (40 min):** each student or pair, against the project rubric — the only point
at which a project's scope is checked before it is built.
**Practical (40 min):** **Lab 6**, a one-week lab with the pipeline's identity and state bucket
bootstrapped by a supplied script — bring up `dev`, add `prod` and account for every
difference, deploy through the pipeline, watch a gate hold, tear down and verify.
**Outcomes:** CLO-7, CLO-9, CLO-8 (design review). **Due:** Lab 6, by the start of week 14.

> **What the compression cost.** The concept time for infrastructure, environments and
> pipelines halved, from 150 minutes to 75. What was cut is depth of demonstration, not
> topics: drift is produced in the lab rather than demonstrated twice, and the federation
> walk-through relies on the supplied bootstrap script. The student notes carry the full
> explanation and the reading budget was raised to pay for it.

---

## End of semester — final exam and project (weeks 14–15)

### Week 14 · Final examination and peer review
**Slides:** [present on claude.ai](https://claude.ai/artifact/ChvS4FJvjkx92WtPkGkzEf) · [Markdown source](../weeks/week-14/slides.md)

No new material.

| Block | Time | Activity |
|---|---|---|
| Final examination | 120 min | Written, in the room. Cumulative, weighted towards weeks 9–13: CLO-2, CLO-5, CLO-6, CLO-7, CLO-9, and one design-defence question for CLO-8. Format in `exams/README.md` |
| Break | 10 min | |
| Structured peer review | 50 min | Four written questions on another group's architecture and evidence, answered in silence; the author may not defend (D-49) |

**Reading:** the synthesis notes — reading an architecture in three passes, security and cost
review as habits, the price of leaving, and what makes a measurement worth believing. They are
not lectured and not examined. They are the method for the peer review, the standard for the
project's write-up of its experiments, and the frame for its migration discussion.
**Outcomes:** CLO-2, CLO-5 … CLO-9 (exam evidence), CLO-8 (peer review, ungraded).

### Week 15 · Demonstration and defence
**Slides:** [present on claude.ai](https://claude.ai/artifact/FS6cCeNf7JN8Kj1ZZW6ecU) · [Markdown source](../weeks/week-15/slides.md)

The full three hours are used differently from every other week.

| Block | Time | Activity |
|---|---|---|
| Demonstrations | up to 120 min | Up to 12 min per group including questions. Fits ten individual projects. Both members of a pair answer an individual question. |
| Synthesis | ~30 min | What transfers to another provider; what was a commitment to this one — the dependency and lock-in material, applied to their own systems |
| Cleanup and reflection | ~30 min | Verified teardown of every remaining resource, and a short written reflection |

**Due:** final project submission, verified cleanup, reflection.
**Outcomes:** CLO-7, CLO-8.

---

## Summary table

| Wk | Concept focus | Practical | Quiz / exam | Due | CLOs | Slides |
|---|---|---|---|---|---|---|
| 1 | Cloud characteristics, service models, shared responsibility | Environment check + local run | — | — | 1 | [deck](https://claude.ai/artifact/Bc9LrKS3qQUSmKod4jhWJW) · [md](../weeks/week-01/slides.md) |
| 2 | Processes, isolation, VMs, containers, HTTP | Lab 1 start | **Q1** | — | 1, 2 | [deck](https://claude.ai/artifact/Kmfv5f7AJWXtaSmDkSHVQr) · [md](../weeks/week-02/slides.md) |
| 3 | Distributed basics, state, latency, failure | Lab 1 finish + **CI set up** | — | **Lab 1** | 2, 3, 5, 9 | [deck](https://claude.ai/artifact/S6bTkK7r4R1d1gvJoG4MGU) · [md](../weeks/week-03/slides.md) |
| 4 | Hierarchy, regions/zones, VMs, identity | Trial activation · Lab 2 start | **Q2** | — | 1, 3 | [deck](https://claude.ai/artifact/8T9hqZG8EMCS84ZpdizsH5) · [md](../weeks/week-04/slides.md) |
| 5 | Virtual networking, access boundaries, least privilege | Lab 2 finish | — | **Lab 2** | 3 | [deck](https://claude.ai/artifact/AsdYRw31iwvXMdU3yeaPUd) · [md](../weeks/week-05/slides.md) |
| 6 | Block/file/object/database; durability | Lab 3 start | **Q3** | — | 4 | [deck](https://claude.ai/artifact/7XQupUBwbESPSXDj2Hug3B) · [md](../weeks/week-06/slides.md) |
| 7 | Replication, consistency, transactions, choosing | Lab 3 finish | — | **Lab 3** | 4, 5 | [deck](https://claude.ai/artifact/Cb7kBoLPQRimc6FEpCyYHG) · [md](../weeks/week-07/slides.md) |
| 8 | *No new material* | Trial check · lab clinic | **Midterm** | — | 1–4 | [deck](https://claude.ai/artifact/L4KayoWqrhQsRuyHmUDeq2) · [md](../weeks/week-08/slides.md) |
| 9 | Managed containers, serverless, statelessness | Lab 4 start | **Q4** | — | 1, 2, 5 | [deck](https://claude.ai/artifact/V8rbrxY6wWjzJFq1NUS7Zf) · [md](../weeks/week-09/slides.md) |
| 10 | Horizontal scaling, concurrency, latency/throughput | Lab 4 finish + load experiment | — | **Lab 4** | 2, 5, 6 | [deck](https://claude.ai/artifact/E1xW4c83h31pjPBYtXUv3m) · [md](../weeks/week-10/slides.md) |
| 11 | Queues, retries, duplicates, idempotency | Lab 5 start · **project brief out** | **Q5** | — | 5 | [deck](https://claude.ai/artifact/VAGuskEQxSoeHzJzHDiW27) · [md](../weeks/week-11/slides.md) |
| 12 | Partial failure, resilience, observability, SLOs | Lab 5 finish + failure experiment | — | **Lab 5**, proposal | 5, 6 | [deck](https://claude.ai/artifact/HwiGyDnvAywGjA9fEwnqKt) · [md](../weeks/week-12/slides.md) |
| 13 | **IaC, environments, delivery pipelines**, keyless identity | Lab 6 (one week) · design review | **Q6** | — | 7, 8, 9 | [deck](https://claude.ai/artifact/3pVwsxchnKFpMtJ5KGjubM) · [md](../weeks/week-13/slides.md) |
| 14 | *No new material* | Peer review | **Final** | **Lab 6** | 2, 5–9 | [deck](https://claude.ai/artifact/ChvS4FJvjkx92WtPkGkzEf) · [md](../weeks/week-14/slides.md) |
| 15 | Defence, synthesis, transfer | Demonstrations, cleanup, reflection | — | **Project** | 7, 8 | [deck](https://claude.ai/artifact/FS6cCeNf7JN8Kj1ZZW6ecU) · [md](../weeks/week-15/slides.md) |

**Twelve teaching weeks** (1–7 and 9–13), **one mid-semester exam week** (8), and **two weeks
at the end** for the final exam and the project (14–15). See D-66.

---

## Sequencing rationale

**Why cloud access starts in week 4, not week 1.** Two reasons, and both matter. First, a
90-day trial has to reach week 15 — starting it in week 1 guarantees it expires before the
project demonstration. Second, a student who has never traced a request locally cannot
debug one in the cloud; weeks 1–3 build the mental model that makes week 4 legible instead
of magical.

**Why the midterm sits in week 8.** It falls between two labs rather than inside one, and at
the seam between "one machine with its state moved out" (weeks 1–7) and "managed, scaled,
asynchronous and delivered" (weeks 9–13). Every outcome it examines has already been practised
in a completed lab.

**Why storage (6–7) comes before managed execution (9–10).** Managed execution requires
statelessness. Statelessness is only possible once state has somewhere else to live. Doing
these in the other order would mean teaching Cloud Run to students whose application still
writes to local disk — which is exactly the confusion the sequence is meant to prevent.

**Why the queue (11) comes after scaling (10).** The load experiment in Lab 4 is what makes
the queue feel necessary rather than decorative: students see the synchronous path
saturate, then remove the slow work from it.

**Why CI arrives in week 3 but pipelines are taught in week 13.** A pipeline is a small
amount of YAML and a large amount of judgement. The YAML is cheap, so students get it in
week 3 and live with it: they watch tests run on every push for ten weeks, and at some point
a red check stops them shipping something broken. Week 13 then teaches gates to people who
have already been stopped by one. Teaching it the other way round produces students who can
draw a pipeline and have never been saved by one.

**Why delivery and environments are one lab, not two.** A pipeline that cannot target a named
environment is a script; an environment you cannot deploy to is a diagram. Separating them
would let students pass both halves without ever connecting them — which is precisely the gap
Lab 6 exists to close. Compressing it to one week kept that pairing and cut the bootstrap
work instead: the federation pool, deployer identity and state bucket come from a supplied
script, and the two second-run bugs are predicted rather than debugged (D-67).

**Why infrastructure-as-code is late (13) but introduced early.** Students need something
worth reproducing before reproducibility is meaningful. Scripted creation and teardown
start in Lab 2; Terraform in week 13 replaces a script students have already been
maintaining by hand, so the declarative model answers a problem they have felt.

**Why synthesis is no longer a lecture.** The former week 14 lecture had four parts, and
every one of them assembled material taught earlier. The three-pass reading method is now
used, not taught, in the week 14 peer review. The evidence standard extends what weeks 10 and
12 already teach about bounded experiments, and is applied in the project write-up. Dependency
and lock-in became the week 15 synthesis, applied to each student's own system rather than a
generic one. All four survive as week 14 reading; none of it is examined.

Any change to this sequence is recorded with its reason in `planning/decisions.md`.
