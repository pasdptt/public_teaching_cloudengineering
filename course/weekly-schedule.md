# Weekly schedule

Relative weeks 1–15. Real dates come from `planning/calendar-worksheet.md` (Q-01).

Session envelope every week: **90 min concepts · 30 min discussion or quiz · 60 min guided
practical**. Quizzes take discussion time, never extra time.

Threads that run through the whole course rather than sitting in one week: identity and
least privilege, cost awareness, cleanup, and observability. Each is introduced with the
first cloud lab (week 4) and revisited, with a dedicated treatment where the table says so.

---

## Phase 1 — Local foundations (weeks 1–3, no cloud account)

### Week 1 · What makes a cloud
**Concepts:** on-demand self-service, resource pooling, elasticity, measured service;
IaaS / PaaS / serverless by *who operates what*; shared responsibility; what "the cloud"
replaced and what problem each property solves. Introduction to the course application.
**Discussion:** given three incidents, who was responsible — provider or customer?
**Practical:** environment check (Python, container runtime, application starts, network
reachable) and first local run of the application. **Ungraded**, but every student must
actually complete it; this is how decision A-04 gets verified.
**Outcomes:** CLO-1. **Assessment:** none.

### Week 2 · Processes, isolation, virtualization, containers
**Concepts:** what a process is and what isolates one from another; virtual machines vs
containers — namespaces, images, layers; just-in-time coverage of ports, HTTP request
anatomy, and how a client finds a server.
**Discussion block:** **Quiz 1** (CLO-1, CLO-2).
**Practical:** start **Lab 1** — run the application in and out of a container, inspect the
boundary, observe what each side can see.
**Outcomes:** CLO-1, CLO-2.

### Week 3 · Distributed application basics
**Concepts:** what changes when a call crosses a machine boundary — latency, partial
failure, the impossibility of distinguishing "slow" from "dead"; where state lives and why
it is the hard part; failure boundaries and blast radius.
**Discussion:** trace a request on paper, then predict what breaks if one component stops.
**Practical:** complete **Lab 1** — trace a request end to end, separate state from
execution, induce and explain a local failure.
**Outcomes:** CLO-2, CLO-3 (foundations), CLO-5 (foundations). **Due:** Lab 1.

---

## Phase 2 — Cloud compute, networking, identity (weeks 4–5)

### Week 4 · Cloud resource hierarchy, VMs and identity
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
**Concepts:** block vs file vs object vs database — the access pattern each assumes;
durability vs availability; what "eleven nines" does and does not promise; why object
storage changed application architecture.
**Discussion block:** **Quiz 3** (CLO-3, CLO-4 foundations).
**Practical:** start **Lab 3** — move stored artefacts out of the VM's local disk into
object storage.
**Outcomes:** CLO-4.

### Week 7 · Replication, consistency and choosing a data service
**Concepts:** replication and what it buys; consistency models in plain terms and the
observable difference between them; transactions and when you need one; how to choose a
data service from the access pattern rather than from familiarity.
**Discussion:** decision exercise — same workload, three candidate stores, defend one.
**Practical:** complete **Lab 3** — externalise application state to the managed data
service and justify the design in a decision record.
**Outcomes:** CLO-4, CLO-5. **Due:** Lab 3.

---

## Phase 4 — Managed execution and scale (weeks 8–9)

### Week 8 · Managed containers and serverless
**Concepts:** what you stop operating when you move from VM to managed container
execution; request-scoped lifecycle; cold start and what causes it; why statelessness is
the price of admission; concurrency settings as a design decision.
**Discussion block:** **Quiz 4** (CLO-1, CLO-2, CLO-4).
**Practical:** start **Lab 4** — containerise and deploy the service to managed execution.
**Outcomes:** CLO-1, CLO-2, CLO-5.

### Week 9 · Horizontal scaling and measurement
**Concepts:** vertical vs horizontal scaling; load distribution; concurrency vs
parallelism; the relationship between latency, throughput and utilisation; autoscaling as
a feedback loop with delay — and why that causes overshoot; how to design a bounded,
honest experiment.
**Discussion:** predict the shape of a latency-vs-load curve, then compare with the data.
**Practical:** complete **Lab 4** — run a bounded load experiment, compare VM and managed
execution on latency, throughput, scaling behaviour and operational responsibility.
**Outcomes:** CLO-2, CLO-5, CLO-6. **Due:** Lab 4.

---

## Phase 5 — Asynchrony, failure, reproducibility (weeks 10–12)

### Week 10 · Queues and event-driven processing
**Concepts:** why slow work leaves the request path; queues and their delivery guarantees;
at-least-once delivery and therefore duplicates; retries, backoff and the retry storm;
idempotency as the property that makes retries safe; dead-letter handling.
**Discussion block:** **Quiz 5** (CLO-5, CLO-6 foundations).
**Practical:** start **Lab 5** — introduce a queue between submission and processing.
**Also this week:** the **project brief is released**.
**Outcomes:** CLO-5.

### Week 11 · Partial failure, resilience and observability
**Concepts:** timeouts, retries and their interaction; circuit breaking conceptually;
graceful degradation; logs vs metrics vs traces and what each answers; service level
objectives and error budgets at an introductory level.
**Discussion:** read a real failure timeline and identify what evidence was missing.
**Practical:** complete **Lab 5** — demonstrate duplicate handling and idempotency, run a
controlled failure experiment, and show the evidence you used to explain it.
**Outcomes:** CLO-5, CLO-6. **Due:** Lab 5 **and** the brief project proposal.
*(Workload note: this is the tightest week in the course. The budget in
`workload-budget.md` reallocates reading time to absorb the proposal.)*

### Week 12 · Declarative infrastructure and cost
**Concepts:** imperative vs declarative provisioning; what Terraform state is and why it
exists; drift; configuration and secret handling — and why a secret in a repository is
permanent; cloud cost models, what actually accrues charges, and how to estimate before
deploying rather than after.
**Discussion block:** **Quiz 6** (CLO-5, CLO-6; CLO-7 via the cleanup thread only — never that day's Terraform or cost material).
**Practical:** **Lab 6** (single week) — complete a supplied Terraform skeleton, recreate
the environment, produce a cost estimate, destroy it, and verify the teardown.
**Outcomes:** CLO-7. **Due:** Lab 6.

---

## Phase 6 — Project (weeks 13–15)

Weeks 13–15 replace new labs with supervised project work. The project reuses the
application and infrastructure already built, so it is not a second implementation effort.

### Week 13 · Architecture synthesis
**Concepts (shorter block, ~60 min):** putting the pieces together — a reference
architecture walkthrough; security review as a habit; cost review as a habit; recognising
where a managed service has become a dependency and what migration would actually cost.
**Practical (extended):** project implementation with an **instructor design review** for
each student or pair. This review is formative — it exists to catch an infeasible or
unmeasurable design while there is time to change it.
**Outcomes:** CLO-8.

### Week 14 · Evidence-based evaluation
**Concepts (~60 min):** what makes a measurement trustworthy; confounds and what a single
run cannot tell you; presenting a tradeoff honestly, including the option you rejected.
**Discussion block:** **Quiz 7** (CLO-6, CLO-7, CLO-8).
**Practical (extended):** run project experiments; structured **peer review** of another
group's architecture and evidence.
**Outcomes:** CLO-6, CLO-8.

### Week 15 · Demonstration and defence
The full three hours are used differently from every other week.

| Block | Time | Activity |
|---|---|---|
| Demonstrations | up to 120 min | Up to 12 min per group including questions. Fits ten individual projects. Both members of a pair answer an individual question. |
| Synthesis | ~30 min | What transfers to another provider; what was a commitment to this one |
| Cleanup and reflection | ~30 min | Verified teardown of every remaining resource, and a short written reflection |

**Due:** final project submission, verified cleanup, reflection.
**Outcomes:** CLO-7, CLO-8.

---

## Summary table

| Wk | Concept focus | Practical | Quiz | Due | CLOs |
|---|---|---|---|---|---|
| 1 | Cloud characteristics, service models, shared responsibility | Environment check + local run | — | — | 1 |
| 2 | Processes, isolation, VMs, containers, HTTP | Lab 1 start | **Q1** | — | 1, 2 |
| 3 | Distributed basics, state, latency, failure | Lab 1 finish | — | **Lab 1** | 2, 3, 5 |
| 4 | Hierarchy, regions/zones, VMs, identity | Trial activation · Lab 2 start | **Q2** | — | 1, 3 |
| 5 | Virtual networking, access boundaries, least privilege | Lab 2 finish | — | **Lab 2** | 3 |
| 6 | Block/file/object/database; durability | Lab 3 start | **Q3** | — | 4 |
| 7 | Replication, consistency, transactions, choosing | Lab 3 finish | — | **Lab 3** | 4, 5 |
| 8 | Managed containers, serverless, statelessness | Lab 4 start | **Q4** | — | 1, 2, 5 |
| 9 | Horizontal scaling, concurrency, latency/throughput | Lab 4 finish + load experiment | — | **Lab 4** | 2, 5, 6 |
| 10 | Queues, retries, duplicates, idempotency | Lab 5 start · **project brief out** | **Q5** | — | 5 |
| 11 | Partial failure, resilience, observability, SLOs | Lab 5 finish + failure experiment | — | **Lab 5**, proposal | 5, 6 |
| 12 | Declarative infra, state, secrets, cost models | Lab 6 (single week) | **Q6** | **Lab 6** | 5, 6, 7 |
| 13 | Architecture synthesis, security & cost review | Project + design review | — | — | 8 |
| 14 | Evidence, tradeoffs, alternatives | Project experiments + peer review | **Q7** | — | 6, 8 |
| 15 | Defence, synthesis, transfer | Demonstrations, cleanup, reflection | — | **Project** | 7, 8 |

---

## Sequencing rationale

**Why cloud access starts in week 4, not week 1.** Two reasons, and both matter. First, a
90-day trial has to reach week 15 — starting it in week 1 guarantees it expires before the
project demonstration. Second, a student who has never traced a request locally cannot
debug one in the cloud; weeks 1–3 build the mental model that makes week 4 legible instead
of magical.

**Why storage (6–7) comes before managed execution (8–9).** Managed execution requires
statelessness. Statelessness is only possible once state has somewhere else to live. Doing
these in the other order would mean teaching Cloud Run to students whose application still
writes to local disk — which is exactly the confusion the sequence is meant to prevent.

**Why the queue (10) comes after scaling (9).** The load experiment in Lab 4 is what makes
the queue feel necessary rather than decorative: students see the synchronous path
saturate, then remove the slow work from it.

**Why infrastructure-as-code is late (12) but introduced early.** Students need something
worth reproducing before reproducibility is meaningful. Scripted creation and teardown
start in Lab 2; Terraform in week 12 replaces a script students have already been
maintaining by hand, so the declarative model answers a problem they have felt.

**Why Lab 6 is a single week.** It reuses components from Labs 2–5 rather than building
anything new, and week 12 must end the billable phase early enough to leave trial slack
for the project.

Any change to this sequence is recorded with its reason in `planning/decisions.md`.
