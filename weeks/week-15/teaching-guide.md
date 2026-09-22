# Week 15 — Teaching guide: Demonstration and defence

| | |
|---|---|
| **Outcomes** | CLO-7, CLO-8 |
| **Assessment** | **Project due** — demonstration, verified cleanup, reflection |
| **Practical** | The whole session |
| **Prep time** | ~2 h first delivery, ~1 h subsequently |

> **The three hours are used differently from every other week.** No lecture, no quiz, no new
> content. `course/weekly-schedule.md` fixes the shape and this guide is how to run it.

## Session objectives

1. Each student demonstrates a working system and defends the decisions behind it.
2. Each student — **including both members of a pair** — answers an individual question about
   a decision they personally made.
3. The cohort separates what transfers to another provider from what was a commitment to this
   one.
4. **Every remaining resource is destroyed and verified, in the room.**

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| **Demonstrations and defence** | 120 | Up to 12 min per group including questions |
| **Synthesis: transfer and commitment** | 30 | What moves, what does not, and what it would cost |
| **Verified teardown and reflection** | 30 | Destroy everything, prove it, then write |

**180 minutes exactly.** No break block: the demonstrations run in two halves with a natural
pause between them, and the room decides when.

> **The placeholder this file replaced carried the standard 90/30/60 plan**, which was wrong —
> week 15 has never been a lecture. `audit.py` skips files marked "not yet authored", so
> nothing caught it. Corrected here.

---

## Before the session

- **Publish the running order in advance**, and tell everyone that it is fixed. Students who
  know they are seventh do not spend the first hour anxious about being called.
- **Ask for one slide, or none.** The demonstration is of a working system, not of slides. A
  student who cannot show the system running should say so at the start and spend their time
  on the evidence instead — which is a recoverable position, and pretending is not.
- **Check the trial expiry dates** you collected in week 14. If anyone's has lapsed, their
  demonstration is of their evidence and their repository, and that is arranged before the
  session rather than discovered during it.
- **Have the marking sheet per student**, not per group. The individual band is scored per
  student and a pair may receive different marks.

---

## Demonstrations (120 min)

**Twelve minutes per group including questions.** Ten individual projects fit exactly, with
nothing to spare, so the timing has to be real.

Suggested split within the twelve:

| | |
|---|---|
| ~4 min | The system running. Actually running. |
| ~3 min | The architecture and the decision that mattered most |
| ~2 min | One experiment, its result, and its limits |
| ~3 min | Questions, including the individual question |

**Keep time visibly and stop people at twelve.** This is a kindness, not a discipline: the
groups at the end of the session are the ones who suffer when the groups at the start run
over, and they have no way to protest.

### Questions worth asking

Three per group is plenty. Draw from the same three passes week 14 taught, because students
have practised answering them:

- **Where does state live in this, and what happens if the thing holding it is replaced
  mid-request?**
- **What is the most expensive mistake this design allows, and what stops it?**
- **Take one number from your evidence. What would have to be true for it to be wrong?**
- **What did you reject, and under what conditions would it have won?**
- **You depend on \<managed service\>. Roughly how many weeks to move off it, and which part
  dominates?**

Two habits to hold to. **Ask about a decision, not about a fact** — "why did you choose X"
rather than "what does X do". And **let a wrong answer be wrong without correcting it in
front of the room**; note it, and use the mark.

### The individual question (pairs)

Required by A-11 and by the assessment plan: both members answer an individual question about
a decision **they personally made**.

Make this visibly routine rather than an interrogation. Announce at the start of the session
that every member of every pair will be asked one, so nobody reads it as suspicion.

Good form: *"You wrote the contribution record. Tell me about a decision you made that your
partner would have made differently, and why yours is in the submission."* It asks for
something only the person who did the work can answer, and it does not require them to
criticise their partner.

Score the individual band per student, immediately, before the next group starts. It will not
be reconstructible afterwards.

---

## Synthesis (30 min): what transfers, what was a commitment

Not a lecture. Build one table on the board with the whole cohort, from what they have all
just seen.

Two columns: **transfers** and **commitment to this provider**. Ask for entries, and make each
one be defended in a sentence.

Expect, roughly:

| Transfers | Commitment |
|---|---|
| Object storage's access pattern and its no-append property | The client library, the IAM model, the bucket-level settings |
| At-least-once delivery, acks, dead-lettering, idempotency | The push envelope, the ack semantics, the retry policy's shape |
| Request-scoped execution, cold start, concurrency as a decision | The scaling algorithm, `$PORT`, the identity model |
| Desired-state infrastructure, state, drift | Every resource type in `main.tf` |
| OIDC federation as the way CI authenticates | Pools, providers, and attribute-condition syntax |
| Least privilege; identity as a first-class design object | The specific role names, and what may be scoped where |
| Measuring before believing | — |

Then the two questions that make it worth the thirty minutes:

1. **Look at the right-hand column. Roughly how many weeks?** They each estimated this for
   their own system in week 14. Compare answers across the room and ask why they differ.
2. **Which commitments would you make again?** Not all lock-in is regrettable. Firestore's
   idle cost is why this course could run at all — the commitment bought something. Ask what
   each one bought, and whether it was worth it.

The conclusion to leave them with, which is the course's actual thesis:

> **You have not learned Google Cloud. You have learned what the problems are, and used one
> provider's answers to them.** The problems are the durable part.

---

## Cleanup and reflection (30 min)

### Verified teardown, in the room (~20 min)

**Do this together and watch it happen.** It is the last opportunity, the trial has to be left
tidy, and a student who leaves with a running resource will not come back to it.

Work through `operations/cleanup.md`, and for Lab 6 in the correct order:

1. `terraform destroy` for **each** workspace.
2. Artifact Registry images — the pipeline pushed them and state never knew about them.
3. Deployer service account, WIF pool and provider.
4. **The state bucket, last.**

Then verify independently, and this is the part that is graded:

```bash
gcloud run services list        --project="$PROJECT_ID"
gcloud pubsub subscriptions list --project="$PROJECT_ID"
gcloud pubsub topics list       --project="$PROJECT_ID"
gcloud storage ls               --project="$PROJECT_ID"
gcloud artifacts repositories list --location=us-central1 --project="$PROJECT_ID"
gcloud compute instances list   --project="$PROJECT_ID"
gcloud compute addresses list   --project="$PROJECT_ID"
gcloud iam service-accounts list --project="$PROJECT_ID"
```

Empty output from all of them is what clean means. **Collect the output** — it is part of the
submission.

**For pairs:** revoke the partner's IAM access on the owner's project, and record who did it
and when.

**Do not ask anyone to close their account or upgrade.** The trial lapses on its own without
charge, and the course has never required a paid account.

> If somebody finds something still running, that is a **success**, not an embarrassment.
> Say so out loud. Ask them how it survived — created by clicking, a script that failed
> partway, or a resource type nobody was checking — because the answer is the most useful
> thing anyone will say all session.

### Reflection (~10 min)

Written, individual, short — half a page, handed in before they leave. Four prompts:

1. **What did you believe about cloud computing in week 1 that you no longer believe?**
2. **Which measurement surprised you most, and what did you do about it?**
3. **Name a decision in your project you would now make differently, and why.**
4. **What would you want to learn next, and what makes you say that?**

Not graded, and say so. It is course-improvement evidence and it is worth more when nobody is
performing. Read them before the next offering; question 1 in particular tends to identify
which week did the most work.

---

## After the session

- **Score the individual band the same day.** It does not survive a week.
- **Check every project's billing report** two days later, not on the day: usage lags, and a
  project that looked clean can still show a line. Follow up privately with anyone who has
  one, and record it — it belongs in the pilot evidence, not in a mark.
- **Collect the reflections and the timings.** How long demonstrations actually took, and how
  long the teardown actually took, are the two numbers this course has never had.
- **Record the observed novice completion times** for every lab, from the cohort, in the
  private repository. Every "Observed pilot time" field in this repository says *not yet
  measured*, and this is the session that ends that.

## Links

- Project: `project/brief.md` · `project/rubric.md` · `project/milestones.md`
- Teardown: `operations/cleanup.md` — the order matters and it is graded
- Cost: `operations/cost-model.md` · trial terms: `operations/cloud-access-and-fallback.md`
- Transfer material: `course/concept-to-gcp-map.md`, and week 14's dependency table
- Student notes: `weeks/week-15/student-notes.md`
- Marking sheets, the individual-question bank and pilot-evidence templates: private repo,
  `teaching-notes/`, `pilot-evidence/`
