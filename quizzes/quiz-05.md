# Quiz 5 — Stateless execution and measurement

**Covers weeks 7–9**, including Lab 4. Taken in week 10, in the discussion block — the queue
material taught in that session is not assessed here. Outcomes: CLO-5, CLO-6 (introductory).

**12 marks · about 12 minutes · closed book · individual.** Short answers are fine. Where a
question shows numbers, they are **ILLUSTRATIVE — NOT MEASURED**; reason from their shape.

---

## Question 1 — Two instances (4 marks)

The course application is deployed with **two instances** behind one address. Each instance
keeps job records in its own process memory. Documents are stored in a bucket.

```text
                    ┌──────────────┐      ┌──────────────────┐
               ┌──▶ │  instance A  │ ───▶ │                  │
  client ──▶ front  │  jobs: {…}   │      │  bucket          │
               └──▶ │  instance B  │ ───▶ │  (documents)     │
                    │  jobs: {…}   │      │                  │
                    └──────────────┘      └──────────────────┘
```

1. A client uploads a document and submits a job; both requests happen to reach **A**. The
   client then asks for the document and for the job status; both reach **B**. What does the
   client get back for each, and why do the two differ? *(2 marks)*
2. The client's job submission times out and it retries with the **same idempotency key**.
   The retry reaches **B**. What happens, and what does the user see? Why is this worse than
   an error? *(1 mark)*
3. What change fixes both problems? Say what kind of change it is. *(1 mark)*

## Question 2 — Read the curve (3 marks)

One service, one configuration. Offered load is increased step by step; each row is a run.

| Offered load (req/s) | Throughput (req/s) | p50 latency (ms) |
|---|---|---|
| 10 | 10 | 255 |
| 20 | 20 | 258 |
| 40 | 39 | 270 |
| 60 | 47 | 610 |
| 80 | 48 | 1,380 |

*ILLUSTRATIVE — NOT MEASURED*

1. Where is the knee, and what is happening to requests above it that was not happening
   below it? *(2 marks)*
2. Someone proposes running the service permanently at 45 req/s "to get our money's worth".
   Why is that a poor operating point, given that it works? *(1 mark)*

## Question 3 — Three runs that disagree (3 marks)

You measure p50 latency three times under what you believe are identical conditions:
**210 ms, 215 ms, 460 ms.**

1. What do you report? *(1 mark)*
2. Name **two** specific things you would check or change next, and say what each would tell
   you. *(2 marks)*

## Question 4 — Waiting or computing (2 marks)

One instance with **one CPU** is set to handle many requests at once. Ten requests arrive
together. Each needs 250 ms of work.

Estimate how long the last of the ten takes to finish when the 250 ms is spent **(a)**
waiting on a network call, and **(b)** computing. Explain why the answers differ.
