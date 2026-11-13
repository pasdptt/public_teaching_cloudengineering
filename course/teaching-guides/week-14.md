# Week 14 — Teaching guide: Final examination and peer review

| | |
|---|---|
| **Outcomes** | CLO-2, CLO-5, CLO-6, CLO-7, CLO-9 (exam evidence); CLO-8 (exam question, and the peer review) |
| **Assessment** | **Final exam** — 120 min, 60 marks, cumulative, weighted towards weeks 9–13 (`weeks/week-08/exams.md`) · **Lab 6 due** at the start of the session |
| **Practical** | Structured peer review. **No new material** |
| **Prep time** | Paper and key: ~6 h first delivery, ~2 h subsequently. Session: ~30 min |

> **Restructured 2026-11-05 (D-66).** This week was "Synthesis and evidence-based
> evaluation": a 60-minute lecture, Quiz 7 and an extended practical. The lecture is now
> reading (the student notes are unchanged in substance), Quiz 7 became the final exam's
> practice set, and the peer review kept its 50 minutes. The former lecture notes are kept at
> the end of this guide as background for the peer review and for the week 15 synthesis.

## Session objectives

1. Every student sits the final exam under the same conditions.
2. Every student reads another group's architecture and evidence against four written
   questions, and hears how their own design reads to someone who did not build it.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| **Final examination** | 120 | Written, in the room. Start on time; collect at 120 minutes exactly |
| Break | 10 | |
| **Structured peer review** | 50 | Four written questions, in silence; then discussion; the author may not defend (D-49) |

**180 minutes exactly.** No concept block and no supervised project time — both went when the
calendar was compressed. The project's independent time this week is 105 minutes, alongside
60 of exam revision (`course/workload-budget.md`).

---

## The exam (120 min)

- **The paper is in the instructor repository** (`exam-papers/final.md`), with its key. It does
  not exist yet. Start from the former Quiz 7 key, which already carries the CLO-8 design-defence
  questions (D-56), and from the practice set (private, `exam-papers/final-practice.md`), which students will
  have been handed — so the
  real paper must use **different scenarios** in the same style.
- **Coverage:** weeks 1–13, about three quarters from weeks 9–13. One design-defence question
  for CLO-8, about a decision from the student's own Lab 6 or project proposal.
- **Not examined:** the synthesis reading below. It is preparation for the peer review and the
  project, it was never lectured, and examining it would break the rule that assessments cover
  only what was taught and practised.
- **Lab 6 is due at the start of the session**, so the exam may draw on it.
- **Mark within a week**, before the week 15 defences if at all possible — the exam's CLO-8
  answer and the defence are two views of the same skill and are worth reading together.

---

## Structured peer review (50 min)

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

**Run it straight after the break.** Students will be tired after the exam, which is a reason to
keep the four questions and the silence strict rather than to soften them: writing to a fixed
prompt is easier than open discussion after two hours of writing.

**Ask everyone to bring a printed or on-screen copy of their project-so-far** — architecture,
proposal, any evidence — announced in week 13. The review cannot run on memory.

---

## Background for the peer review and the week 15 synthesis (not lectured)

This was the week 14 concept block. Students now meet it as reading in
`weeks/week-14/student-notes.md`. It is kept here because the peer review's four questions
assume the three-pass reading method, the week 15 synthesis assumes the dependency and
price-of-leaving material, and the project rubric's A3 and C3 bands assume the dependency and
evidence sections. Use it when preparing those, not as a lecture.

#### Reading an architecture in three passes

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

#### Security and cost review as habits, not events

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

#### Dependency, and the price of leaving

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

#### Evidence, and presenting a tradeoff

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

## Common misconceptions

These now surface in the peer review, the project write-up and the week 15 defence rather than
in a lecture.

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
- Exam format: `weeks/week-08/exams.md` · practice set: private, `exam-papers/final-practice.md` —
  hand it out before week 14
- Project: `weeks/week-11/project/brief.md` · `weeks/week-11/project/rubric.md` · `weeks/week-11/project/milestones.md`
- The rehearsals: `weeks/week-09/lab-04/rubric.md` band B4 (confounds), `weeks/week-11/lab-05/rubric.md` band B1
  (proves/does-not-prove) — reuse their language rather than inventing new
- Portability: `course/concept-to-gcp-map.md`
- Final paper, its key, and the peer-review sheet: private repo, `exam-papers/`, `teaching-notes/`
