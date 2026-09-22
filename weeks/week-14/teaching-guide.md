# Week 14 — Teaching guide: Synthesis and evidence-based evaluation

| | |
|---|---|
| **Outcomes** | CLO-6, CLO-8, CLO-9 |
| **Assessment** | **Quiz 7** (weeks 11–13; CLO-6, CLO-7, CLO-8, CLO-9) |
| **Practical** | Project experiments · **structured peer review** |
| **Prep time** | ~3 h first delivery, ~1 h subsequently |

> **Restructured 2026-09-22 (D-24).** Architecture synthesis moved here from week 13. It sits
> well beside evaluation: both are about judging a design rather than building one.

## Session objectives

1. Read an architecture and say where state lives, where boundaries are, and what each
   identity may do — without being prompted for those three.
2. Perform a security review and a cost review as routine passes rather than as events.
3. Identify where a managed service has become a dependency, and estimate what leaving would
   actually cost.
4. Say what makes a measurement trustworthy, and name the confounds in one of their own.
5. Present a tradeoff honestly, including the option they rejected and why.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| **Architecture synthesis** | 15 | Reading a system in three passes |
| Security and cost review as habits | 10 | Two checklists they already know the content of |
| **Dependency, and the price of leaving** | 15 | The question nobody asks until it is expensive |
| **Evidence, and presenting a tradeoff** | 20 | What makes a measurement trustworthy |
| Break | 10 | |
| **Quiz 7** | 15 | Weeks 11–13 |
| **Practical (extended): peer review and project experiments** | 95 | Structured review, then their own work |

**180 minutes exactly.** 60 concepts · 15 quiz · 95 practical, plus the break.

> **The practical is deliberately the largest block in the course.** The concepts here are
> mostly assembly of things already taught, and the skill is applying them to somebody else's
> design — which cannot be lectured. `course/weekly-schedule.md` calls this the extended
> practical; this is what that means.

---

## Teaching notes

### Reading an architecture in three passes

They have built one system in six labs. Now they have to read someone else's in ten minutes,
which is what the peer review and the week 15 questions both require.

Teach it as three passes, in this order, and insist on the order:

1. **Where does state live?** Everything else follows from it. A component that holds state is
   a component that cannot be casually replaced, restarted or duplicated — which is Lab 4 in
   one sentence.
2. **Where are the boundaries?** Every place a call crosses a machine, a network or a trust
   boundary is a place where it can be slow, fail, or be refused. Count them.
3. **What may each identity do?** Not "is it secure" — *who is allowed to do what, and where
   did that permission come from?*

Demonstrate it live on the course application, which they know cold. Two minutes, all three
passes, out loud. Then the point: those three questions are most of what a senior engineer
does when handed an unfamiliar diagram, and none of them requires knowing the product names.

### Security and cost review as habits, not events

Short block, because the content is entirely revision. Frame it as two passes they can run on
any design in five minutes.

**Security pass.** Who can reach it? What identity does it run as, and what does that identity
allow? Where do credentials live, and how long do they last? What happens when — not if — one
leaks?

**Cost pass.** What costs money at rest? What costs money per use? What grows without anyone
deciding to grow it? What is the most expensive mistake available here, and what stops it?

Then make it concrete on their own project, and ask for the answer they have all been avoiding:

> **What is the most expensive thing a bug in your project could do overnight?**

Everyone in the room has a bounded answer, because the whole course has been built so they do.
That is worth saying explicitly.

### Dependency, and the price of leaving

This is the block with new content in it, and it is the one that transfers furthest.

Start with a fact they can check: their application moved from local to VM to managed
execution to a queue **without changing behaviour**, because every backend sits behind a
`Protocol`. Ask what that cost them — it is not free, it is a seam they had to design and
maintain.

Then ask what is *not* behind a seam. Firestore's query semantics. Pub/Sub's push envelope
and its delivery guarantees. Cloud Run's scaling model and `$PORT`. The Terraform provider.
IAM's shape.

> **A dependency is not a service you use. It is a service whose assumptions have leaked into
> your design.**

Then price the exit, concretely, for their own application. Get them to estimate — not
discuss — how long it would take to move it to another provider:

| Piece | Effort to move | Why |
|---|---|---|
| Documents in object storage | small | `Storage` protocol, four methods, near-identical elsewhere |
| Job records in Firestore | **medium to large** | Query and consistency semantics differ; `count()` alone is a decision |
| The queue | medium | The interface transfers; envelopes, acks and dead-lettering do not |
| Managed execution | small–medium | The container is portable; scaling, identity and config are not |
| The Terraform configuration | **large** | Resource types are provider-specific; only the *model* transfers |
| The pipeline's identity | medium | OIDC federation is a pattern everyone has, spelled differently |

The conclusion to land, and it is deliberately not anti-cloud:

> **Lock-in is not a yes/no property. It is a number of weeks, and you should know roughly
> what that number is for anything you depend on.**

A team that knows it is four weeks has made a decision. A team that has never asked has made
one too, without noticing.

### Evidence, and presenting a tradeoff

Everything here has been rehearsed — Lab 4's confounds paragraph and Lab 5's
proves/does-not-prove paragraph are both drafts of this. Say so, and make this the block where
it becomes general.

Four properties of a measurement worth believing:

1. **One variable changed**, and the rest stated.
2. **Conditions recorded** — where, when, what version, what else was running.
3. **Repeated**, with the disagreement between runs reported rather than smoothed.
4. **Its limits stated.** What this measurement cannot tell you.

Then the move that separates a good report from a plausible one:

> **Say what your own successful experiment failed to establish.**

Lab 5 did exactly this: publishing the same message five times proves something about *your
service* and nothing about *the broker*. Put that example up, because it is theirs.

Then presenting a tradeoff. The shape is four sentences, and it is worth writing on the board:

1. Here is the decision, and the constraint that forced it.
2. Here is what I chose, and the evidence for it.
3. **Here is what I rejected, and under what conditions it would have won.**
4. Here is what would change my mind.

Sentence 3 is the one students omit, and it is the one that makes the rest credible. A
recommendation with no rejected alternative reads as a preference; the same recommendation
with a properly-argued alternative reads as a decision.

---

## Quiz 7 (15 min)

Covers weeks 11–13: CLO-6, CLO-7, CLO-8, CLO-9. The last quiz, and the only one assessing
CLO-8, so it carries real weight — `course/assessment-plan.md` notes that dropping a lowest
quiz is safe for every other outcome partly because of how this one is built.

**It may assess today's evidence material only through what students have already done** —
the Lab 4 and Lab 5 write-ups — not through the framing given ninety minutes earlier. Same
rule as Quiz 6.

---

## Practical (95 min): peer review, then project work

### Structured peer review (~50 min)

Pair each student or group with another. They exchange whatever exists of the project so far:
the architecture, the proposal, and any evidence collected.

**Twenty minutes reading and writing, in silence.** Reviewers answer four questions in
writing. Nothing else, and no general impressions:

1. **Where does state live in this design, and what happens if the component holding it is
   replaced mid-request?**
2. **What is the most expensive mistake this design allows, and what stops it?**
3. **Take one claim from their evidence. What would have to be true for it to be wrong?**
4. **What is the strongest version of an alternative they rejected?**

**Then twenty minutes talking**, ten each way. The reviewer reads their answers; the author
may ask clarifying questions and **may not defend**. That rule matters and you will have to
enforce it two or three times — the value is in hearing how the design reads to someone who
did not build it, and a defence stops that immediately.

**Last ten minutes, together.** Ask for the most useful thing anyone *received*, not gave.
Three answers, then stop.

The written sheets go to the authors and a copy to the instructor. They are **not graded** —
they are CLO-8 evidence of the reviewer's engagement, and they feed the week 15 defence.

### Project experiments (~45 min)

Supervised work time. Circulate with one question:

> What is the question your experiment answers, and how will you know if the answer is wrong?

Priorities, in order:
- **Anyone with no experiment planned by the end of this session is in trouble**, and week 15
  is one week away. Cut their scope with them, now, using the smallest-version answer recorded
  at the week 13 design review.
- **Anyone still building** should be stopped and asked what evidence they will have. A working
  system with no measurements scores poorly against `project/rubric.md`, and this is the last
  moment to change that.
- **Remind everyone about the trial window and about cleanup.** Week 15 verifies teardown in
  the session, and a trial expiring mid-demonstration is a recoverable disaster only if it is
  known about in advance.

---

## Common misconceptions

| Misconception | Surfaces as | Response |
|---|---|---|
| "The architecture is the diagram" | Synthesis block | The diagram is a claim. Ask where state lives and watch it change. |
| "We're not locked in, we used standard containers" | Dependency block | The container moves. The queue semantics, the IAM model and the Terraform do not. |
| "Lock-in is bad" | Dependency block | It is a cost. Unpriced, it is a risk; priced, it is a decision. |
| "More data means a better result" | Evidence block | Not if the conditions changed. Three runs with notes beat thirty without. |
| "The experiment worked, so the claim holds" | Evidence block | Which claim? Lab 5 proved something about the service and nothing about the broker. |
| "Presenting the alternative weakens my case" | Tradeoff block | It is the only thing that makes it a case rather than a preference. |
| "Peer review means being nice" | Peer review | It means being useful. The four questions are not optional. |
| "Security review is something you do at the end" | Review block | Then it is an audit. As a habit it is five minutes and it is free. |

---

## Links

- Student notes: `weeks/week-14/student-notes.md`
- Project: `project/brief.md` · `project/rubric.md` · `project/milestones.md`
- The rehearsals: `labs/lab-04/rubric.md` band B4 (confounds), `labs/lab-05/rubric.md` band B1
  (proves/does-not-prove) — reuse their language rather than inventing new
- Measurement tools and their stated limits: `application/tools/measure.py`,
  `application/tools/instances.py`
- Portability: `course/concept-to-gcp-map.md`
- Quiz 7 key and the peer-review sheet: private repo, `quiz-keys/`, `teaching-notes/`
