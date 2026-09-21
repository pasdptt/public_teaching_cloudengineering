# Learning outcomes

Eight course learning outcomes (CLOs). Each is written so that a marker can tell, from a
student's submitted artefact, whether it was met — and each is mapped to where it is
taught and where the evidence comes from.

The same outcomes and the same standard apply to every student, undergraduate and
graduate alike (decision A-09).

---

## The outcomes

### CLO-1 — Cloud characteristics and service models
**By the end of the course, a student can** describe on-demand self-service, resource
pooling, elasticity, measured service and broad network access; distinguish IaaS, PaaS,
container-as-a-service and serverless by *what the provider operates*; and, given a
described incident, state which side of the shared-responsibility boundary it falls on and
why.

*Evidence looks like:* a correct, reasoned attribution of responsibility for a specific
failure — not a recited definition or a copied responsibility matrix.

### CLO-2 — Comparing execution models
**…can** compare virtual machines, containers and managed/serverless execution along
isolation boundary, start-up and lifecycle, degree of control, and operational
responsibility; and justify which is appropriate for a stated workload, naming what is
given up.

*Evidence looks like:* a recommendation that names a concrete cost of the choice (e.g.
cold-start latency, loss of host access, or an idle-capacity bill), not a list of generic pros and cons.

### CLO-3 — Tracing a request across network and identity boundaries
**…can** trace a request through a deployed application — client, DNS, external address,
load distribution, firewall or ingress rule, service, backing store — and state, at each
hop, what rule permits it and which identity it acts as; and can predict the effect of
removing one rule before testing it.

*Evidence looks like:* a prediction recorded **before** a change, the observed result
after, and an explanation of any difference.

### CLO-4 — Selecting storage and data services
**…can** choose between block, file, object and database storage for a stated access
pattern, justifying the choice using durability, consistency model, latency, access
pattern and cost; and can state what the choice makes difficult later.

*Evidence looks like:* a decision record with the rejected alternatives and the condition
that would reverse the decision.

### CLO-5 — Designing a small cloud-native application
**…can** design and implement a small application that keeps execution stateless, holds
state in an external service, moves slow work to an asynchronous path, and scales
horizontally — and can explain what each of those four properties buys.

*Evidence looks like:* working code plus an explanation of why a request handler holds no
state, demonstrated by a behaviour that would break if it did.

### CLO-6 — Measuring behaviour and explaining it with evidence
**…can** design and run a bounded load experiment and a controlled failure experiment;
report latency, throughput and error behaviour with the experimental conditions stated;
identify the limiting resource; and distinguish what the measurement shows from what it
does not.

*Evidence looks like:* measurements with units, sample size and conditions, and at least
one honest statement of a limitation. An experiment that did not behave as predicted still
earns full analysis credit when the reasoning is sound. Fabricated data earns zero.

### CLO-7 — Reproducing and removing an environment
**…can** recreate a small environment from a script and a declarative configuration, verify
it works, then destroy it and **verify** that nothing billable remains — explaining what
the declarative tool tracks in state and why a resource can survive a deleted VM.

*Evidence looks like:* a resource inventory before and after, and a teardown verification
that names resources that outlive compute (disks, addresses, buckets, images, logs).

### CLO-8 — Defending an architecture
**…can** present an architecture against stated requirements and defend it under
questioning on security, reliability, cost and provider dependence; identify which design
ideas transfer to another provider and which are commitments to this one; and describe
what a migration would actually involve.

*Evidence looks like:* an individual oral answer about a decision the student made,
including a change they would make with more time or budget.

---

## Outcome → instruction → assessment map

Every outcome is taught before it is assessed, and every outcome has at least one piece of
graded evidence.

| CLO | Taught in weeks | Practised in | Assessed by | Primary evidence |
|---|---|---|---|---|
| CLO-1 Characteristics & service models | 1, 4, 8 | Lab 1, Lab 4 | Quiz 1, Quiz 4, Project defence | Responsibility attribution for a specific incident |
| CLO-2 Execution models | 2, 8, 9 | Lab 1, Lab 4 | Quiz 1, Quiz 2, Quiz 4, Lab 4 | VM-vs-managed comparison backed by Lab 4 measurements |
| CLO-3 Network & identity tracing | 3, 4, 5 | Lab 2 | Quiz 2, Quiz 3, Lab 2 | Recorded prediction + observed result for a rule change |
| CLO-4 Storage & data selection | 6, 7 | Lab 3 | Quiz 3, Quiz 4, Lab 3, Project | Decision record with rejected alternatives |
| CLO-5 Cloud-native design | 8, 9, 10 | Lab 4, Lab 5 | Quiz 5, Lab 4, Lab 5, Project | Stateless handler + external state + queue, working |
| CLO-6 Measurement & explanation | 9, 11, 14 | Lab 4, Lab 5 | Quiz 5, Quiz 6, Quiz 7, Lab 4, Lab 5, Project | Load experiment and failure experiment with conditions |
| CLO-7 Reproducibility & teardown | 12 (cleanup thread from wk 4) | Lab 6 (and cleanup from Lab 2 on) | Quiz 6 (cleanup thread), Quiz 7, Lab 6, Project | Teardown verification showing nothing billable remains |
| CLO-8 Architecture defence | 13, 14, 15 | Weeks 13–15 | Project defence, Quiz 7 | Individual oral answer under questioning |

Cost reasoning, identity/least privilege and cleanup are **not** separate outcomes; they
are threaded through CLO-3, CLO-4, CLO-7 and CLO-8 and are assessed in every cloud lab
rubric's reproducibility/security/resource-handling band.

---

## Coverage check

| Check | Result |
|---|---|
| Every CLO has at least one graded artefact | ✅ all eight |
| Every CLO is taught before first assessment | ✅ see week numbers above |
| Every quiz maps only to outcomes already taught | ✅ verified in `assessment-plan.md` |
| Every CLO is assessed by something other than a quiz | ✅ each has a lab or project artefact |
| No CLO depends on resources the course cannot guarantee | ✅ CLO-3 … CLO-7 have documented local fallbacks (`operations/cloud-access-and-fallback.md`) |

---

## Outcomes deliberately excluded

These would not be honestly assessable in 15 weeks with ~180 min/week of independent work
and no TA, so they are not claimed:

- Operating a Kubernetes cluster.
- Designing for multi-region or multi-cloud availability.
- Production-grade security engineering or threat modelling.
- Capacity planning or cost optimisation at organisational scale.
- Building data pipelines or ML platforms.

Students are told explicitly what the course does *not* qualify them to do. A course that
overclaims is a worse preparation than one that is honest about its scope.
