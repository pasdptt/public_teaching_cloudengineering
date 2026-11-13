---
marp: true
theme: cloudcourse
paginate: true
footer: 'Week 10 · Horizontal scaling and measurement'
---

<!--
Deck for week 10. Derived from course/teaching-guides/week-10.md — that file is authoritative
for the teaching; this is what goes on the wall.

Render:  bash course/slides/render.sh 10
-->

<!-- _class: lead -->

# Horizontal scaling and measurement

## Week 10

Cloud Computing: Principles and Practice

<!--
TIMING: 180 min total — 80 concepts · 30 discussion · 60 practical · 10 break.
Guide: course/teaching-guides/week-10.md
Before you start: read the --help epilogues of application/tools/measure.py and tools/instances.py. Have a real measure.py report from a warm service ready for the discussion's last ten minutes. Lab 4 is due at the end of the week.
-->

---

## Where we are

Last week your service ran on instances you never saw, and the job records broke until they moved to Firestore.

This week: what "scaling" actually buys, why it reacts late, and how to measure it so that the numbers mean something.

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:00 – 0:15</span>

# Vertical and horizontal

By what each one runs out of

---

## Two ways to get more

| | What it is | What runs out |
|---|---|---|
| **Vertical** | a bigger machine | **the machine** — there is a largest one |
| **Horizontal** | more machines | **the shared things** — the database, the lock, the one thing every copy touches |

---

<!-- _class: ask -->

## Your application has been ready for horizontal scaling since Lab 3.
## Why was it not ready in week 2?

<!--
The state. They proved it themselves last week, with the 404s.
-->

---

<!-- _class: block -->

<span class="min">10 minutes</span><span class="clock">0:15 – 0:25</span>

# Concurrency and parallelism

Waiting overlaps; computing does not

---

<!-- _class: ask -->

## One CPU, ten requests, 250 ms each.
## How long if they wait? How long if they compute?

<!--
Roughly 250 ms and roughly 2.5 s. Same code shape, same numbers, tenfold difference — the first overlaps, the second queues.
-->

---

<!-- _class: punch -->

## Concurrency is structure: several things in flight. Parallelism is hardware: several things executing.

<!--
Concurrency without parallelism is still a win when the work is waiting. This is the answer to last week's concurrency-setting argument, and it is why the application's delay is a sleep.
-->

---

<!-- _class: block -->

<span class="min">25 minutes</span><span class="clock">0:25 – 0:50</span>

# Latency, throughput, utilisation

Three questions, one curve

---

## Draw it against offered load

```text
 throughput                      latency
  ^          ___________          ^                  |
  |        /                      |                 /
  |      /                        |               /
  |    /                          |  ___________/
  |  /                            |
  +------------------> load       +------------------> load
             ^ knee                           ^ knee
```

**The knee is where the queue starts.** Before it, arriving work finds a free server. After it, work waits — and that wait is latency that is not in your code.

<!--
Draw both curves on the board, on the same axis. This sketch is the one the discussion asks them to redraw for their own service.
Guide: "Latency, throughput and utilisation — draw it"
-->

---

## Three things to take away

1. **They are different questions.** "How fast is one request?" and "how many per second?" have different answers and different fixes.
2. **The knee is the queue.** Past it, every extra request waits.
3. **High utilisation is not a goal.** At 95% there is no slack, so every burst becomes a queue.

---

<!-- _class: ask -->

## Would you rather run at 50% utilisation or at 95%?
## Say what each one costs.

---

<!-- _class: ask -->

## In Lab 1, concurrency 4 gave about four times the throughput of concurrency 1, at the same latency.
## Where on the curve were you?

<!--
On the flat, early part, and they did not know it. Ask: what would have told them?
Use THEIR numbers if anyone has them. The authoring reference run is in the private repository (lab-solutions/lab-01/teaching-notes.md); it is printed nowhere public, because producing their own numbers is the Lab 1 exercise.
-->

---

<!-- _class: block -->

<span class="min">Break — 10 minutes</span><span class="clock">0:50 – 1:00</span>

# Break

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">1:00 – 1:20</span>

# Autoscaling as delayed feedback

Why a sensible rule overshoots

---

## The loop

```text
measure load  ->  decide  ->  start instances
     ^                              |
     |                              v
     +--------  useful LATER  <-----+
```

<!--
Draw it, then put a delay in the middle and ask what a step increase in traffic does. Let them get there: it keeps adding while earlier additions are still starting, finds itself over-provisioned, removes too many. Overshoot, possibly oscillation.
Guide: "Autoscaling: a feedback loop that reacts late"
-->

---

<!-- _class: punch -->

## Every autoscaler is a control loop with a delay, and delay is what makes control loops oscillate.

---

## Two consequences

- Scaling helps with **sustained** load. It cannot help with a spike shorter than its own delay.
- **A cold start is part of that delay.** Last week's block and this one are the same mechanism.

---

<!-- _class: block -->

<span class="min">10 minutes</span><span class="clock">1:20 – 1:30</span>

# A bounded experiment

One you could defend

---

## Four rules

1. **Change one variable.** Part 4 changes the concurrency setting, and nothing else.
2. **State the conditions.** Where the client was, the processing delay, the time, the code version.
3. **Repeat.** Three runs. If they disagree, **that disagreement is the result.**
4. **Say what it cannot tell you.** Small samples, one location, one workload shape, one day.

---

<!-- _class: ask -->

## Laptop, then a VM, then managed execution — three different weeks.
## What is that comparison worth?

<!--
"Quite a lot, if the caveats are attached, and almost nothing if they are not." That is how the comparison is marked.
-->

---

<!-- _class: block -->

<span class="min">30 minutes</span><span class="clock">1:30 – 2:00</span>

# Discussion

Predict the curve, then look

---

## First ten minutes — no data

For the service **you deployed last week**, draw two curves against offered load:

- latency
- throughput

Mark the knee, and label what causes it.

Then predict how both change when `--max-instances` goes from **4 to 1**.

<!--
Then 10 minutes in pairs: compare drawings and argue. Most disagreements are really about whether the work waits or computes.
-->

---

## Last ten minutes — together

The class's predictions on the board. Then a real `measure.py` report from a warm service.

**Not "who was right".** What would you need to see more of before believing any of it?

<!--
Say plainly: this drawing is the one Part 4 asks them to compare against, and a wrong prediction that is explained scores higher than a right one that is not.
-->

---

<!-- _class: block -->

<span class="min">60 minutes</span><span class="clock">2:00 – 3:00</span>

# Practical

Lab 4 Parts 4–7

---

<!-- _class: cost -->

## The bounds keep this lab free

| | At most |
|---|---|
| Runs per configuration | **3** |
| Requests per run | **40** |
| Client concurrency | **20** |
| `--max-instances` | **4** |

The scripts enforce the last one. **The rest is on you.**

---

<!-- _class: demo -->

## Part 4 — concurrency 80, then 1

```bash
gcloud run services update docapp --region=us-central1 \
  --concurrency=80 --project="$PROJECT_ID"
python3 tools/measure.py --url "$SERVICE_URL" \
  --requests 40 --concurrency 20 --header "Authorization: Bearer $TOKEN"
python3 tools/instances.py --url "$SERVICE_URL" \
  --requests 40 --concurrency 20 --header "Authorization: Bearer $TOKEN"
```

Then `--concurrency=1`, and the same two commands. **Wait for the new revision to serve before you measure.**

<!--
Changing the concurrency setting starts a new revision. Measuring before it is serving compares two different things and looks like noise.
-->

---

<!-- _class: demo -->

## Part 5 — a cold start, on purpose

Leave the service alone for **fifteen minutes**. Write up Part 4 while you wait.

```bash
python3 tools/measure.py --url "$SERVICE_URL" \
  --requests 5 --concurrency 1 --header "Authorization: Bearer $TOKEN" --json
```

Compare `min` and `max`. Run it again at once, and compare the two reports.

<!--
The wait is real and they will try to shorten it. A service that has not gone cold produces a measurement of nothing.
-->

---

## Part 6 — three places, one table

Laptop (Lab 1) · VM in Iowa (Lab 2) · managed execution in Iowa (this lab).

**Conditions on every row.** Then name the confounds specifically — and say which would matter most.

Four real caveats and a ranking score higher than a clean-looking table with none.

---

<!-- _class: demo -->

## Part 7 — teardown and verification

```bash
cd weeks/week-09/lab-04/starter
./06-teardown.sh
./07-verify-clean.sh
```

| Easy to forget | Why |
|---|---|
| **Artifact Registry images** | the one that actually accrues — every build adds to it |
| The service account | costs nothing, grants something |

<!--
BEFORE ANYONE LEAVES: 07-verify-clean.sh run, in the room. Two minutes now, or a support email in week 13. Collect Part 0 predictions if you did not last week.
-->

---

## This week's work — 180 minutes

| | |
|---|---|
| Read the notes | 20 min |
| Lab 4: the experiment, cold starts, the comparison, teardown | 160 min |

**Lab 4 is due at the end of this week**, with teardown verification.

---

<!-- _class: punch -->

## The service scaled, and every request still waited for the work to finish.

<!--
Name what the lab could not do. Removing the work from the request path is week 11.
-->

---

<!-- _class: lead -->

# Next week

Queues and event-driven processing

**Quiz 5** · **Lab 5 starts** · **the project brief is released**
