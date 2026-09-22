# Week 9 — Teaching guide: Horizontal scaling and measurement

| | |
|---|---|
| **Outcomes** | CLO-2, CLO-5, CLO-6 |
| **Assessment** | — (Lab 4 due) |
| **Practical** | Lab 4 Parts 4–7 |
| **Prep time** | ~3.5 h first delivery, ~1 h subsequently |

## Session objectives

1. Distinguish vertical from horizontal scaling by what each one runs out of.
2. Distinguish concurrency from parallelism, and say which one the application's 250 ms
   delay exercises.
3. State the relationship between latency, throughput and utilisation, and explain why
   optimising one can damage another.
4. Explain autoscaling as a feedback loop with delay, and predict overshoot from that.
5. Design a bounded experiment: one variable, stated conditions, repeated runs, and an
   explicit list of what the result cannot tell you.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| Vertical vs horizontal | 15 | What each runs out of, and which one has a ceiling |
| Concurrency vs parallelism | 10 | Waiting overlaps; computing does not |
| **Latency, throughput, utilisation** | 25 | The three-way relationship, drawn |
| Break | 10 | |
| **Autoscaling as delayed feedback** | 20 | Why a sensible rule overshoots |
| Designing a bounded experiment | 10 | One variable, conditions, repeats, caveats |
| **Discussion: predict the curve** | 30 | Draw it, then compare with real data |
| Practical | 60 | Lab 4 Parts 4–7 |

**180 minutes exactly.** 80 concepts · 30 discussion · 60 practical, plus the break.

---

## Teaching notes

### Vertical and horizontal, by what runs out

Vertical: a bigger machine. Horizontal: more machines. The useful distinction is not the
picture, it is the failure:

> Vertical scaling runs out of **machine**. Horizontal scaling runs out of **shared things**
> — the database, the lock, the licence, the one thing in the middle that all the copies
> touch.

Ask which one their application has been ready for since Lab 3, and why it was not ready in
week 2. The answer is the state, and they proved it themselves last week.

### Concurrency versus parallelism, in one exercise

One CPU, ten requests. If each spends 250 ms waiting on a network call, how long for all ten?
If each spends 250 ms computing?

Roughly 250 ms and roughly 2.5 s. Same code shape, same numbers, tenfold difference — because
the first overlaps and the second queues.

> **Concurrency is structure: several things in flight. Parallelism is hardware: several
> things executing.** Concurrency without parallelism is still a win when the work is waiting.

This is also the answer to last week's concurrency-setting argument, and it is why the
application's delay is a `sleep`: it makes the distinction measurable on a laptop.

### Latency, throughput and utilisation — draw it

Draw throughput against offered load. It rises linearly, bends, and flattens. Draw latency on
the same axis: flat, then a knee, then a cliff.

Three things to get across:

1. **They are different questions.** "How fast is one request" and "how many per second" have
   different answers and different fixes.
2. **The knee is where the queue starts.** Before it, arriving work finds a free server.
   After it, work waits — and waiting is latency that is not in your code.
3. **High utilisation is not a goal.** A system at 95% utilisation has no slack, so every
   burst becomes a queue. Ask them where they would rather run, at 50% or 95%, and make them
   say what each choice costs.

Then connect it to something they measured in Lab 1: concurrency 1 gave ~4.8 req/s and
concurrency 4 gave ~19 req/s on the same laptop, with latency essentially unchanged. They
were on the flat, early part of the curve and did not know it. What would have told them?

### Autoscaling: a feedback loop that reacts late

Draw the loop: measure load → decide → start instances → they become useful *later* → measure
again. Then put a delay in the middle and ask what happens to a step increase in traffic.

They will get there: the controller keeps adding while the earlier additions are still
starting, then finds itself over-provisioned and removes too many. Overshoot, and possibly
oscillation.

> **Every autoscaler is a control loop with a delay, and delay is what makes control loops
> oscillate.** This is not a flaw in one product. It is the shape of the problem.

Two consequences worth stating:

- Scaling helps with *sustained* load and cannot help with a spike shorter than its own delay.
- A cold start is part of that delay, which links this block to last week's.

### Designing an experiment you can defend

Short block, and it sets up both the lab and week 14. Four rules:

1. **Change one variable.** Their Lab 4 Part 4 changes the concurrency setting only.
2. **State the conditions.** Where the client was, what the delay was, time of day, what
   version of the code.
3. **Repeat.** Three runs. If they disagree, *that disagreement is the result* and belongs in
   the write-up.
4. **Say what it cannot tell you.** Small samples, one location, one workload shape, one day.

Then hold up the comparison they are about to make: laptop in week 3, VM in week 5, managed
execution in week 9. Different weeks, different networks, code that changed in between. Ask
what that table is worth. The answer is "quite a lot, if the caveats are attached, and almost
nothing if they are not" — which is exactly how band B4 is marked.

---

## Discussion (30 min): predict the curve, then look

**First 10 minutes, no data.** Each student draws two curves for the Cloud Run service they
deployed last week: latency against offered load, and throughput against offered load. Mark
where the knee is and label what causes it. Then predict how both change when
`--max-instances` goes from 4 to 1.

**Next 10 minutes, in pairs.** Compare drawings and argue about the differences. Most
disagreements are really about whether the work waits or computes, which is the morning's
material arriving in a form they have to use.

**Last 10 minutes, together.** Collect the class's predictions on the board, then show a real
`measure.py` report from a warm service — theirs, or one produced live. The useful moment is
not "who was right"; it is asking what in the report they would need to see more of before
believing any of it.

Tell them plainly: the drawing they just made is the one Part 4 asks them to compare against,
and a wrong prediction that is explained scores higher than a right one that is not.

---

## Common misconceptions

| Misconception | Surfaces as | Response |
|---|---|---|
| "Scaling means it gets faster" | Constantly | Horizontal scaling adds capacity. One request's latency does not improve; it usually gets slightly worse. |
| "Latency and throughput are the same measurement" | Part 4 write-ups | Ask for a system with high throughput and terrible latency. Batch processing. Then the reverse. |
| "We should aim for high utilisation" | Cost discussions | Then every burst queues. Slack is what you buy with the unused half. |
| "Autoscaling handles spikes" | Autoscaling block | Not spikes shorter than its own reaction time, which includes a cold start. |
| "More instances always means more throughput" | Experiment design | Until the shared thing saturates — and after Lab 3, the shared thing is Firestore. |
| "p95 of 20 requests is a p95" | Every lab | It is "the second-slowest one". The tool prints n for that reason. |
| "The numbers disagree, so the run was bad" | Part 4 | Three runs that disagree is a finding about variance, and it is reportable. |
| "A faster median means the change worked" | Part 4 | Not if the two runs differ in anything else. Name the confound first. |

---

## Practical (60 min): Lab 4 Parts 4–7

- **Bounds first, and out loud.** Three runs, 40 requests, client concurrency ≤ 20,
  `--max-instances` ≤ 4. The scripts enforce the last one; the rest is on them.
- **The fifteen-minute idle wait in Part 5 is real** and students will try to shorten it.
  Point out that the write-up is what the wait is for, and that a service which has not gone
  cold produces a measurement of nothing.
- **Watch for a redeploy between measurement runs.** Changing the concurrency setting starts
  a new revision; measuring before it is serving compares two different things and looks like
  noise.
- **Teardown is graded and Artifact Registry is the one they forget.** Have
  `07-verify-clean.sh` run before anyone leaves, in the room. It is two minutes and it is the
  difference between a clean project and a support email in week 12.
- **Collect Part 0 predictions** if you did not collect them last week.

End by naming what the lab could not do: the service scaled, and every request still waited
for the work to finish. Removing the work from the request path is week 10.

## Links

- Student notes: `weeks/week-09/student-notes.md`
- Lab: `labs/lab-04/README.md` · Rubric: `labs/lab-04/rubric.md`
- Tools: `application/tools/measure.py`, `application/tools/instances.py` — read both
  `--help` epilogues before teaching this session
- Evidence standards, revisited in depth: `weeks/week-14/teaching-guide.md`
- Solutions and the mistake list: private repo, `lab-solutions/lab-04/`
