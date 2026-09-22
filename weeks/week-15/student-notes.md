# Week 15 — Demonstration and defence

**The project is due.** So is **verified cleanup**, and a short reflection. No quiz, no new
material.

The three hours run differently from every other week: demonstrations for two hours, a
synthesis discussion for thirty minutes, and then everyone tears down their remaining cloud
resources together and proves it.

---

## What happens in the session

| Block | Time | What you do |
|---|---|---|
| Demonstrations | up to 120 min | Up to **12 minutes** per group, including questions |
| Synthesis | ~30 min | Build the transfer-vs-commitment table with the room |
| Cleanup and reflection | ~30 min | Destroy everything, verify it, write half a page |

## Your twelve minutes

Twelve minutes is not long and the timing will be kept. A workable split:

| | |
|---|---|
| ~4 min | **The system running.** Actually running, not a screenshot. |
| ~3 min | The architecture, and the decision that mattered most |
| ~2 min | One experiment: what you measured, what you found, what it does not show |
| ~3 min | Questions |

**Practise it once, out loud, with a timer.** Almost everybody overruns on the first try, and
the part that gets cut is always the evidence — which is 25% of the rubric, the same weight as
the architecture.

### If something is broken on the day

Say so at the start and spend the time on your evidence and your reasoning instead. That is a
recoverable position and it is marked far better than a demonstration that quietly avoids the
thing that does not work. A system that broke, diagnosed honestly, is evidence of
understanding; a demonstration that dodges is evidence of nothing.

**If your trial has expired**, tell the instructor before the session, not during it.

## The questions you will be asked

They come from the three passes in week 14, and you have practised answering them in the peer
review. Expect three, drawn from:

- **Where does state live, and what happens if the thing holding it is replaced mid-request?**
- **What is the most expensive mistake this design allows, and what stops it?**
- **Take one number from your evidence. What would have to be true for it to be wrong?**
- **What did you reject, and under what conditions would it have won?**
- **Roughly how many weeks to move off \<the managed service you depend on\>, and which part
  dominates?**

They are about **decisions**, not facts. "Why did you choose this" rather than "what does this
do". "I don't know, but here is how I would find out" is a genuinely good answer; a confident
wrong one is not.

### If you worked in a pair

**Both of you will answer an individual question**, about a decision you personally made. This
is announced for everyone, it is routine, and it is not suspicion — the communication and
individual-understanding band is scored per student and a pair can receive different marks
(A-11).

The form it usually takes: *a decision you made that your partner would have made
differently, and why yours is the one in the submission.* Your contribution record is what
makes that answerable, so make sure it is accurate and that you both agree with it.

## The synthesis discussion

The whole room builds one table: **what transfers** to another provider, and **what was a
commitment** to this one. You will be asked to contribute entries and defend them in a
sentence.

Come with one of each from your own project. Week 14's dependency table is the starting
point, and the two questions at the end are the interesting ones:

1. Looking at the commitment column — **roughly how many weeks?**
2. **Which commitments would you make again?** Not all lock-in is regrettable. Firestore's
   lack of idle cost is why this course could run inside a free tier at all. The commitment
   bought something; the question is whether it was worth it.

## Cleanup — graded, and done in the room

Bring a terminal that is signed in. Everyone tears down together, and for Lab 6 **the order
matters**:

1. `terraform destroy` for **each** workspace, dev and prod.
2. **Artifact Registry images** — the pipeline pushed them and Terraform state never knew.
3. **Deployer service account, WIF pool and provider** — a standing trust relationship.
4. **The state bucket, last.** Delete it earlier and Terraform forgets what it owns while it
   still owns things.

Then verify independently, and keep the output — this is the graded part:

```bash
gcloud run services list           --project="$PROJECT_ID"
gcloud pubsub subscriptions list   --project="$PROJECT_ID"
gcloud pubsub topics list          --project="$PROJECT_ID"
gcloud storage ls                  --project="$PROJECT_ID"
gcloud artifacts repositories list --location=us-central1 --project="$PROJECT_ID"
gcloud compute instances list      --project="$PROJECT_ID"
gcloud compute addresses list      --project="$PROJECT_ID"
gcloud iam service-accounts list   --project="$PROJECT_ID"
```

Empty output from every one of them is what clean means.

**Pairs:** revoke your partner's access on the owner's project, and say in the submission who
did it and when.

> **If you find something still running, that is a good outcome, not an embarrassment.** Say
> what it was and work out how it survived — created by clicking, a script that failed
> partway, or a resource type nobody was checking. That explanation is worth more than a tidy
> project, and it is the last thing this course asks you to notice.

**You do not need to close your account or upgrade anything.** The trial lapses on its own,
without charge. It never required a paid account and it does not now.

## The reflection

Half a page, written in the session, handed in before you leave. **Not graded** — it is used
to improve the course, and it is more useful when nobody is performing.

1. What did you believe about cloud computing in week 1 that you no longer believe?
2. Which measurement surprised you most, and what did you do about it?
3. Name a decision in your project you would now make differently, and why.
4. What would you want to learn next, and what makes you say that?

## What to have ready

- [ ] The system deployed and working, **or** an honest account of what is not
- [ ] Your twelve minutes rehearsed with a timer
- [ ] Architecture diagram and decision record
- [ ] Both experiments, with conditions and stated limits
- [ ] Cost model against a stated workload
- [ ] The migration discussion — what transfers, what does not
- [ ] Contribution record, if you are a pair
- [ ] A signed-in terminal for the teardown
- [ ] AI-assistance disclosure

## This week's work (~180 minutes)

| | |
|---|---|
| Final project work and submission | 150 min |
| Demonstration preparation, cleanup verification, reflection | 30 min |

---

## One last thing

You spent fifteen weeks on one small application: a service that stores a document and counts
the words in it. That was deliberate.

Every week it stayed the same application and the ground moved underneath it — off your
laptop, onto a machine, off that machine's disk, into a thing that scales, behind a queue,
into a file that describes it, behind a pipeline that deploys it. The application never got
more interesting. The questions did.

> **You have not learned Google Cloud. You have learned what the problems are, and used one
> provider's answers to them.**

The problems are the part that is still true in ten years. Where state lives. What a boundary
costs. What an identity may do. Whether you can run it twice. What your measurement does not
show.

The product names will all have changed. Take the questions.
