# Week 14 — Synthesis and evidence-based evaluation

**Quiz 7 this week** (weeks 11–13) — the last one. **You will peer-review another group's work
in the session**, and your project experiments should be running by the end of it.

---

## Reading an architecture

You have built one system over six labs. This week you have to read someone else's, in ten
minutes, and say something useful about it. That is also what week 15's questions will ask of
you.

There is a method, and the order matters.

### Pass 1 — Where does state live?

Everything else follows from this. A component that holds state cannot be casually replaced,
restarted or duplicated. A component that holds none can be thrown away mid-request and
nobody notices.

That is Lab 4 in one sentence, and it is the first thing to find in any design, including one
drawn by somebody who has never thought about it.

### Pass 2 — Where are the boundaries?

Every point where a call crosses a process, a machine, a network or a trust boundary is a
point where it can be **slow**, **fail**, or be **refused**. Count them. Each one is a place
where week 3's slow-versus-dead problem lives.

### Pass 3 — What may each identity do?

Not "is this secure", which has no answer. **Who is allowed to do what, and where did that
permission come from?**

In your own system there are five or six principals by now: you, the service, the broker's
push account, the pipeline's deployer, and Pub/Sub's own service agent. If you cannot name
what each may do, neither can anyone else.

> Those three questions are most of what an experienced engineer does when handed an
> unfamiliar diagram, and none of them requires knowing any product names.

## Two reviews you should be able to run in five minutes

Neither is new content. Both are worth having as a routine rather than as an event.

**The security pass.** Who can reach it? What identity does it run as, and what does that
allow? Where do credentials live and how long do they last? What happens when — not if — one
leaks?

**The cost pass.** What costs money at rest? What costs per use? What grows without anyone
deciding it should? And:

> **What is the most expensive thing a bug could do overnight?**

You have a bounded answer to that, for your own project, because the whole course was built so
you would. Most people do not.

## Dependency, and what leaving would cost

Your application moved from a laptop to a VM to managed execution, and from local files to
object storage to a database to a queue — **without its behaviour changing**. That was not
luck. Every backend sits behind a `Protocol`, and designing and maintaining those seams was a
real cost you paid up front.

Now ask what is *not* behind a seam:

- Firestore's query and consistency semantics.
- Pub/Sub's push envelope, its ack deadline, its dead-lettering.
- Cloud Run's scaling model, its `$PORT` convention, its identity model.
- The Terraform provider's resource types.
- The shape of IAM itself.

Which gives a better definition than "lock-in":

> **A dependency is not a service you use. It is a service whose assumptions have leaked into
> your design.**

### Price the exit

Not "are we locked in" — that has no useful answer. **How many weeks?**

| Piece | Effort to move | Why |
|---|---|---|
| Documents in object storage | small | Four methods behind a Protocol, near-identical everywhere |
| Job records in Firestore | **medium–large** | Query and consistency semantics differ; `count()` alone was a decision |
| The queue | medium | The interface transfers; envelopes, acks and dead-lettering do not |
| Managed execution | small–medium | The container is portable; scaling, identity and config are not |
| The Terraform configuration | **large** | Resource types are provider-specific; only the model transfers |
| The pipeline's identity | medium | OIDC federation is universal, spelled differently everywhere |

> **Lock-in is not a yes/no property. It is a number of weeks, and you should know roughly
> what that number is for anything you depend on.**

A team that knows it is four weeks has made a decision. A team that has never asked has also
made one, without noticing. This is not an argument against managed services — you have seen
what operating things yourself costs, in Lab 2 and in every teardown since.

## What makes a measurement worth believing

You have done this twice already. Lab 4 asked you to name the confounds in a three-way
comparison; Lab 5 asked what your successful experiment failed to prove. Here is the general
form.

**Four properties:**

1. **One variable changed**, with the rest stated.
2. **Conditions recorded** — where you were, when, what version, what else was running.
3. **Repeated**, with disagreement between runs reported rather than averaged away.
4. **Limits stated.** What this measurement cannot tell you.

And the move that separates a good report from a plausible one:

> **Say what your own successful experiment failed to establish.**

Lab 5 is the example, and it is yours: publishing the same message five times proves your
service is safe against re-delivery, and proves **nothing whatever** about how often Pub/Sub
actually redelivers. Both are true. Only one of them is what the experiment was about.

### Small-sample honesty

Both tools you have used print their own limits in `--help`, and both are worth re-reading
before you write up the project:

- p95 of 20 requests is "the second-slowest one".
- A client and server on the same machine compete for the same CPU.
- One run is one sample of a noisy system.
- `instances.py` gives a **lower bound** on instances, never a count.

Quoting a number without these is how a report becomes confident and wrong.

## Presenting a tradeoff

Four sentences. The third is the one people leave out, and it is the one that makes the rest
credible.

1. **The decision**, and the constraint that forced it.
2. **What I chose**, and the evidence for it.
3. **What I rejected, and under what conditions it would have won.**
4. **What would change my mind.**

A recommendation with no rejected alternative reads as a preference. The same recommendation
with a properly-argued alternative reads as a decision — and the difference is visible to any
reader in about ten seconds.

Your own course has examples you can copy the shape of: Firestore over Cloud SQL was decided
on idle cost, with the workload where that reasoning fails named explicitly; an ephemeral IP
over a static one, with the price table attached; two environments rather than three, with the
reason recorded.

## The peer review, this week, in the session

You will read another group's work and answer four questions **in writing**, in silence, before
anyone talks:

1. Where does state live in this design, and what happens if the component holding it is
   replaced mid-request?
2. What is the most expensive mistake this design allows, and what stops it?
3. Take one claim from their evidence. What would have to be true for it to be **wrong**?
4. What is the strongest version of an alternative they rejected?

Then twenty minutes of discussion, ten each way. **When your work is being reviewed, you may
ask clarifying questions and you may not defend it.** That rule is not politeness — the entire
value is in hearing how your design reads to someone who did not build it, and a defence ends
that immediately.

The sheets are not graded. They are evidence of your engagement, and they are the best
preparation available for week 15, where somebody will ask you these questions out loud.

## This week's work (~180 minutes)

| | |
|---|---|
| Read these notes; prepare for Quiz 7 (weeks 11–13) | 15 min |
| Project: experiments, measurement, write-up | 145 min |
| Peer review of another group's work | 20 min |

**Your experiments should be running by the end of this week.** A working system with no
measurements scores poorly — `project/rubric.md` puts 25% on experiments and interpretation,
the same weight as architecture.

**Check your trial's expiry date now**, and check your resources are what you think they are.
Week 15 verifies teardown in the session.

## Check yourself

1. The three passes for reading an architecture, in order. Why that order?
2. Name every principal in your own system and what each may do.
3. What is the most expensive thing a bug in your project could do overnight?
4. Define a dependency in a way that is more useful than "a service we use".
5. Roughly how many weeks to move your application to another provider? Which piece dominates?
6. Four properties of a measurement worth believing.
7. Take your best result from Lab 4 or Lab 5. What did it fail to establish?
8. The four sentences of an honest tradeoff. Which one do people omit, and why does it matter?
9. Why may you not defend your work during the peer review?

## Next week

Demonstrations and defence. Up to twelve minutes per group including questions; both members
of a pair answer an individual question. Then synthesis — what transfers to another provider
and what was a commitment to this one — and **verified teardown of everything, in the room**,
plus a short written reflection.

**The project is due.** So is the cleanup evidence.
