# Week 3 — Teaching guide: Distributed application basics

| | |
|---|---|
| **Outcomes** | CLO-2, CLO-3 (foundations), CLO-5 (foundations) |
| **Assessment** | **Lab 1 due** at the end of this week |
| **Practical** | Lab 1 Parts 3–5 |
| **Prep time** | ~3.5 h first delivery, ~1 h subsequently |

## Session objectives

1. Name the three outcomes of a remote call, and explain why the third is unavoidable.
2. State why a slow component cannot be distinguished from a dead one, and what follows.
3. Explain a timeout as a chosen trade-off, and the retry dilemma it creates.
4. Define idempotency and point to it in the course application.
5. Distinguish three levels of state durability and place a given design on them.
6. Explain why stateless execution is what makes horizontal scaling possible.
7. Identify failure boundaries and blast radius in a small architecture.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| Crossing the boundary | 20 | Latency table. The chatty-design worked example. |
| **Slow vs dead** | 25 | The core idea. Timeouts as guesses. The retry dilemma. |
| Idempotency | 20 | The escape. **Live demo** in the application. |
| Break | 10 | |
| Where state lives | 25 | Three levels. Tie directly to what they saw in Lab 1 Part 3. |
| Stateless execution | 15 | What it unlocks; what forecloses it |
| Failure boundaries | 15 | Blast radius; the two questions |
| **Discussion** | 30 | Lab 1 Part 3 results compared across the room |
| Practical | 60 | Lab 1 Parts 4–5 |

---

## Teaching notes

### Make the latency real before anything else

Put the table up, then do the arithmetic live: a design with 20 sequential round trips
Bangkok↔Iowa is 4 seconds of pure waiting, before any work. Ask what to change. Steer them
to *fewer, larger* round trips — and note that this is a design decision invisible in the
source code, which is why it survives code review and dies in production.

It also quietly justifies decision D-18 (labs run in `us-central1`). Someone will ask why an
Iowa region for a Bangkok class. The answer: the free tier only exists in those US regions,
and every latency measurement in this course compares against itself, so a constant offset
changes nothing. Say it plainly — it models exactly the kind of cost-versus-architecture
reasoning the course is teaching.

### Slow vs dead is the centre of the week

Spend the time. The sequence that works:

1. "You send a request. Nothing comes back. What happened?" Collect answers. Someone says
   "it's down". Someone says "it's slow". Agree that both are consistent with the evidence.
2. "How long do you wait before deciding?" — there is no right answer, and that is the point.
3. "You've waited. You retry. What have you just risked?" — doing it twice.
4. "You don't retry. What have you risked?" — not doing it at all.
5. Let that sit. Then: "so make doing it twice harmless."

Do not shortcut to the answer. The discomfort in step 4 is what makes idempotency feel like
a relief rather than a technique.

### Demo idempotency in the application they are holding

```bash
curl -i -X POST .../jobs -H 'Idempotency-Key: demo' -d '{...}'   # 201
curl -i -X POST .../jobs -H 'Idempotency-Key: demo' -d '{...}'   # 200, deduplicated: true
curl -sS .../stats                                               # jobs_created: 1
```

Point out that this has been in the application since week 2, seven weeks before there is a
queue to require it. Designed in, not bolted on. That is the habit being taught.

### Three levels of state, using what they saw last week

They have already watched the job record vanish on restart and — if they got through Part 2
— the containerised document vanish with the container. Build the three levels on top of
those observations rather than presenting them abstractly.

**The distinction to insist on:** level 2 is dangerous *because it works*. It passes every
test on a laptop. It is why "we wrote it to disk" is not the same claim as "it is durable",
and it is the problem Lab 3 solves.

---

## Discussion: compare Part 3 results (30 min)

Ask for hands: who predicted the document would survive the restart? Who predicted the job
would? Then who predicted correctly for the *container* case?

The container case is where the room usually splits, and the split is the lesson. Draw out
the difference between "it was in memory" and "it was on storage that was itself
disposable". Students who conflate these will struggle in Lab 3; this is the cheapest moment
to catch it.

Then ask the question the lab does not: *what would you have to change so that the
containerised document survived?* Let them invent volumes and object storage. Weeks 6–7 then
arrive as answers rather than as topics.

---

## Common misconceptions

| Misconception | Surfaces as | Response |
|---|---|---|
| "Just set a long timeout" | In the timeout discussion | Then your caller times out on you. Where does that end? |
| "Retries fix unreliable networks" | Whenever retries come up | Retries fix *lost requests*. They duplicate *successful* ones. Ask which they had. |
| "Idempotency means the code is bug-free" | Occasionally | It means running twice has the same effect as running once. Show the dedup path. |
| "We wrote it to disk, so it's durable" | Constantly, and expensively | Whose disk? What happens to that disk when the container stops? |
| "Stateless means it doesn't store anything" | In the stateless block | It stores plenty — elsewhere. The *instance* holds nothing between requests. |
| "More servers means more reliable" | In the blast-radius block | Only across a failure boundary. Three instances sharing one database still have one. |

---

## Practical block (60 min)

Lab 1 Parts 4 and 5. This is the heaviest independent block of the first three weeks.

Expect on Part 4 (`FileJobStore`):

- **A lock taken twice on the same thread** → the concurrency test hangs. Most common
  failure by a distance. Point at the read-modify-write path rather than giving the answer.
- **`get()` returning `None`** instead of raising `JobNotFound` — a contract violation the
  tests catch, and worth naming as *why* Protocols exist.
- **Re-reading the file on every call.** Passes everything, very slow. Do not fail it; ask
  them about it. Their answer to docstring question 1 is worth more than the code.
- **Forgetting to release the idempotency key on delete.**

On Part 5, watch for single runs. Insist on three. The variation between them *is* the
finding, and a student who reports one run has not yet understood what a measurement is.

**Remind them what the rubric weights.** Band B (explanation and evidence) is 40 marks;
band A (working implementation) is 35. A perfect `FileJobStore` with a thin write-up scores
worse than a rough one with a good analysis. Say this out loud — it is counter to every
instinct they have from other courses.

## Looking ahead — say this before they leave

- **Do not activate a cloud trial before next week's session.** Ninety days must reach week
  15. Repeat it; someone always forgets.
- Anyone expecting an eligibility or payment-method problem should speak to you **this
  week**, so their alternative path starts in the same session as everyone else's.
- Next week costs real money for the first time: about four cents. Say the figure. It sets
  the tone that cost is something this course measures rather than worries about.

## Links

- Student notes: `weeks/week-03/student-notes.md`
- Lab: `labs/lab-01/README.md` · Rubric: `labs/lab-01/rubric.md`
- Instructor notes and reference solution: private repo, `lab-solutions/lab-01/`
- Next week: `operations/cloud-access-and-fallback.md` §6 has the week 4 checklist
