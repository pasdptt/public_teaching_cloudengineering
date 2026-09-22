# Week 9 — Horizontal scaling and measurement

**Lab 4 is due this week.** No quiz.

---

## Two ways to make a system bigger

**Vertical:** a bigger machine. More CPU, more memory, same single thing. Easy — often just a
restart — and it has a hard ceiling, because there is a largest machine.

**Horizontal:** more machines. No ceiling in principle, and that "in principle" is doing real
work in that sentence.

The honest distinction is not the picture, it is what each one runs out of:

> Vertical scaling runs out of **machine**. Horizontal scaling runs out of **the shared
> thing** — the database, the lock, the licence, the one component every copy touches.

Your application became horizontally scalable in Lab 3, when its state moved out of the
process. Before that, more copies meant more *disagreement*, not more capacity — which is
exactly what Lab 4 Part 3 showed you. The shared thing is now Firestore, and it has limits of
its own.

## Concurrency is not parallelism

One CPU. Ten requests. Each spends 250 ms.

- If the 250 ms is spent **waiting** — on a network call, a disk, a timer — all ten finish in
  roughly 250 ms. Waiting overlaps.
- If it is spent **computing**, they finish in roughly 2.5 seconds. The CPU does one thing at
  a time, and the others queue.

Same shape of code, same number, tenfold difference.

> **Concurrency is structure: several things in flight. Parallelism is hardware: several
> things executing.**

This is why last week's concurrency setting has no universal right answer, and why you can
predict the answer for a specific service if you know which kind of work it does. The course
application's 250 ms is a `sleep` — it waits. Keep that in mind when you interpret Part 4,
and be careful about generalising your result to software that computes.

## Latency, throughput, utilisation

Three measurements, constantly confused.

- **Latency** — how long one request takes. A property of a request.
- **Throughput** — how many requests per second complete. A property of a system.
- **Utilisation** — what fraction of capacity is busy.

Push load up and the shape is always the same. Throughput rises, then bends, then flattens:
the system is saturated and cannot do more. Latency is flat, then has a **knee**, then climbs
steeply.

The knee is the interesting part, and it is where **queueing** starts. Below it, work arrives
and finds something free. Above it, work waits — and that waiting is latency that exists in
none of your code. You cannot profile it, because nothing is running.

Three consequences worth carrying:

1. **Improving one can damage another.** Batching raises throughput and raises latency. More
   instances raise throughput and leave one request's latency unchanged or slightly worse.
2. **High utilisation is not a goal.** A system at 95% has no slack, so every burst becomes a
   queue. The unused half is what you are buying when you run at 50%.
3. **Where you are on the curve decides what your measurement means.** In Lab 1 you measured
   about 4.8 req/s at concurrency 1 and about 19 req/s at concurrency 4, with latency barely
   moving. You were on the flat early part and could not have known it from one point.

## Autoscaling is a feedback loop, and it reacts late

The loop: measure the load → decide how many instances are wanted → start them → **they
become useful some time later** → measure again.

That "some time later" is the whole story. A new instance is not useful when the decision is
made; it is useful when it has been scheduled, pulled, started and has accepted a connection
— the cold start from last week, now on the critical path of the *control system* rather than
of one request.

So when traffic steps up, the controller adds instances, and while they are starting the load
still looks too high, so it adds more. Then they all arrive at once, the load per instance
drops far below target, and it removes too many. **Overshoot**, and sometimes oscillation.

> **Every autoscaler is a control loop with delay, and delay is what makes control loops
> oscillate.** That is not a defect in one product; it is the shape of the problem.

Two things follow directly:

- Autoscaling helps with **sustained** load changes. It cannot help with a spike shorter than
  its own reaction time.
- Bounds matter. `--max-instances` is not a performance setting, it is the blast radius of a
  mistake — yours, or a client's retry loop.

## How to run an experiment whose answer you can defend

This is a skill, it is assessed in every remaining piece of work in this course, and it is
mostly four rules.

**1. Change one variable.** In Lab 4 Part 4 that is the concurrency setting. If you also
redeploy a new image, move to a café, or edit the processing delay, you have measured
something with no name.

**2. State the conditions.** Where the client was, the network, the processing delay, the
instance bounds, the time of day, which revision was serving. An unlabelled number is not
evidence; it is a souvenir.

**3. Repeat.** Three runs minimum. **If the three disagree, that disagreement is your
result** — report it rather than picking the prettiest.

**4. Write down what it cannot tell you.** Small samples, one client location, one workload
shape, one day, one provider. This is not modesty. It is the difference between a measurement
and an anecdote, and it is worth real marks.

### The comparison you are about to make, and why it is fragile

Part 6 puts three rows in one table: your laptop in week 3, a VM in week 5, managed execution
this week. Different weeks, different networks, possibly different code, certainly a different
mood.

That table is still worth making — it is the only way to see the shape of the difference —
**but only with its caveats attached**. Name the specific confounds, not "conditions varied",
and say which one you think mattered most. A tidy table with no caveats scores lower than a
messier one that knows what it does not know.

`measure.py --help` ends with a section called "Honest limitations". Read it before you write
your interpretation. It is short, it is about your measurement specifically, and several of
the marks in Part 6 are sitting in it.

## This week's work (~180 minutes)

| | |
|---|---|
| Read these notes | 20 min |
| Lab 4 Parts 4–7: the experiment, the cold start, the comparison, teardown | 160 min |

Reading is deliberately light this week. The experiment and the write-up are the learning,
and the write-up is the larger half.

**Lab 4 is due at the end of this week, including verified teardown.** Check Artifact
Registry specifically — it is the resource that keeps costing after everything visible is
gone.

## Check yourself

1. Vertical and horizontal scaling: what does each run out of?
2. Ten requests, one CPU, 250 ms each. How long if they wait? If they compute? Why?
3. Draw latency against offered load. Mark the knee. What starts happening there?
4. Give a system with high throughput and bad latency, and one with the reverse.
5. Why is 95% utilisation a worse place to run than 50%, given that both work?
6. Explain autoscaling overshoot from the delay, without using the word "bug".
7. Your three runs give 210 ms, 215 ms and 460 ms. What do you report, and what do you do
   next?
8. Name three confounds in the laptop-vs-VM-vs-Cloud-Run comparison, and say which one you
   would remove first if you could only remove one.

## Next week

The application still makes every user wait for the processing to finish. Scaling did not fix
that; it just bought more places to wait. Week 10 takes the slow work out of the request path
with a queue — and introduces the problem that arrives with it, which is that a queue will
happily deliver the same message twice.

**The project brief is released next week.**
