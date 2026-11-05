# Integrative project — milestones

What is due when, how long each step should take, and what happens to it. The requirements are
in [`brief.md`](brief.md), and how the final submission is marked is in [`rubric.md`](rubric.md).

**Only the final submission is marked.** The proposal, the design review and the peer review are
not graded separately. They exist so that scope problems are found in week 13, when they are
cheap to fix, and not in week 15, when they are not. Skipping one does not cost marks directly,
but it takes away the check that would have caught a project that cannot be finished.

---

## Timeline

| Week | Milestone | Your time | What happens to it |
|---|---|---|---|
| 11 | **Brief released** in the session | 20 min | Read it. Pick a likely extension. Check your trial expiry date. |
| 12 | **Proposal due** at the end of the week, with Lab 5 | 30 min | The instructor reads it before week 13. Not marked. |
| 13 | **Design review** in the session, 3–4 min each. Lab 6 takes the rest of the week | — | The scope is agreed, and your smallest version is written down |
| 14 | **Final exam**, then **peer review**, in the session. **Your experiment running** by the end of the week | ~105 min | Written feedback from a peer. Not marked. |
| 15 | **Demonstration**, **teardown in the room**, and **final submission** by the end of the week | ~150 min | Marked against the rubric |

The exact dates depend on the semester calendar and are announced by the instructor. Where to
submit is announced too.

Two deadlines share week 12, and it is the tightest week in the course. **If you run out of time
that week, protect Lab 5's teardown first.** An orphaned subscription keeps costing money, and a
late proposal is a conversation with the instructor, not a lost mark.

---

## Week 12 — The proposal

**One page, thirty minutes.** It is a plan, not a design document. You have not yet learned the
infrastructure material from week 13, so you are not expected to describe any of it.

Copy this template and fill it in:

```markdown
# Project proposal — <your name(s)>

**Extension:** A / B / C / D / E — <one sentence saying what you will build>
<If E: two or three sentences on what it is and why it fits the brief's four conditions.>

**Workload (first version):** <who uses it, how much, and the peak. Say where the numbers
come from, even if the answer is "invented".>

**Which one I will run, and why:** <performance or failure — one sentence. The other is designed,
not run (brief Part 3).>

**Performance experiment:**
- Question: <a question with a measurable answer>
- Prediction: <what you expect, and why>

**Failure experiment:**
- What I will break, and how I will undo it: <…>
- Prediction: <what the user will see, and what state things will be left in>

**Reuse and build:** <what comes from Labs 1–6 unchanged, and what is new. The new part
should be short.>

**Cost:** <anything you think might not be free, or "nothing beyond the labs", with the reason>

**Access:** cloud / local fallback.
<Pairs: who owns the cloud project; both trial expiry dates.>
```

**What makes a proposal useful to you:**

- **An experiment question that could come out the other way.** "Does it work?" is not a
  question. "How many duplicates does a burst of 20 concurrent same-key submissions produce?"
  is one.
- **A prediction you commit to.** Being wrong later is worth marks. Not having predicted is not.
- **A short "build" list.** If it is longer than the "reuse" list, the project is probably too
  big.

**Pairs:** check both trial expiry dates now. The project stops when the owner's trial ends, and
it must last until the teardown in week 15.

---

## Week 13 — The design review

Three to four minutes each, in the session, against your proposal. There are three questions
and nothing else:

1. **What question does your experiment answer?** If it has no measurable answer, it gets
   fixed now.
2. **What will you reuse, and what will you build?** The delivery path comes from Lab 6. A plan
   that builds its own pipeline is over scope and is cut on the spot.
3. **What is the smallest version of this that would still be worth demonstrating?**

**Write down the answer to question 3 before you leave**, at the top of your proposal, with the
date. That is your fallback. If week 15 goes badly, you demonstrate the smallest version and
explain what you cut and why. That is a decision, and it is marked as one.

**Most projects are cut down at this review.** That is normal and it is the point of the review.
A cut in week 13 costs nothing; the same cut in week 15 costs the evidence.

The instructor also checks your cost reasoning against the free tier here. A design that needs a
paid resource is sent back for redesign rather than approved with a budget.

**Your time after the review:** none in week 13 — Lab 6 takes the week. Your first project time
is 105 minutes in week 14, alongside final-exam revision. Use it to get the smallest version
deploying through your Lab 6 pipeline and your one experiment running, not to start the
extension's cleverest part.

---

## Week 14 — Final exam, peer review, and your experiment running

The session opens with the **final exam** (120 minutes); the peer review follows the break.
**Bring** whatever exists: your architecture sketch, your proposal with its smallest version, and
any evidence so far. It does not need to be finished; the review is more useful when it is not.

In the session you exchange with another student or pair, write answers to four questions about
their design in silence, then read them your answers. **When your work is being reviewed, you
may ask clarifying questions but you may not defend it.** The point is to hear how your design
reads to someone who did not build it. The sheets are not graded, and they are the best
rehearsal there is for the questions in week 15.

**By the end of week 14, the experiment you chose to run should have run at least once**, and
the other should be designed on paper. A working system with
no measurements scores poorly. Experiments and interpretation are 25% of the mark, the same as
architecture. If you are still building at this point, stop, and measure what you have.

**Check your trial expiry date again**, and check that what is running is what you think is
running.

---

## Week 15 — Demonstration, teardown, submission

**In the session:**

1. **Demonstration**: up to twelve minutes including questions. What to show and what you will
   be asked are in [`weeks/week-15/student-notes.md`](../weeks/week-15/student-notes.md).
   Rehearse it once, out loud, with a timer.
2. **Teardown, in the room**: every resource, in the order from Lab 6 (state bucket last), then
   the listing commands, whose output goes in your submission. Pairs: the owner revokes the
   partner's access.
3. **Reflection**: half a page, not graded.

**By the end of the week:** the final submission. The list of what it contains is in
[`brief.md`](brief.md#what-you-submit), and that list is the contract.

**If your trial has expired or is about to**, tell the instructor **before** the session. If
something is broken on the day, say so at the start of your twelve minutes.

---

## If you fall behind

Cut in this order, and write down what you cut:

1. **The extension**: fall back to the smallest version agreed at the design review.
2. **Experiment size**: fewer steps and fewer repetitions, with the limitation stated. Three runs
   of one condition, honestly reported, is better than a sweep you did not finish.

**Do not cut** the experiment you run, the design of the other, the teardown, or the
explanation. Those are where the marks are. A small extension with one real experiment, one
careful design and a verified teardown scores better than a large extension with none.

If the whole class is squeezed, the instructor will adjust the requirements and record it. Do
not adjust them yourself.
