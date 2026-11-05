# Quiz 6 — Asynchrony, failure and evidence

**Covers weeks 10–12**, including Lab 5, plus two habits you have practised all term:
**cleanup** (since Lab 2) and **the CI workflow** that runs on your pushes (since week 3).
Taken in week 13, in the discussion block. The infrastructure-as-code, environment and cost
material taught in that session is **not** assessed here. Outcomes: CLO-5, CLO-6; CLO-7 and
CLO-9 through those two habits only.

**13 marks · about 12 minutes · closed book · individual.** Short answers are fine. Show your
working for any arithmetic.

---

## Question 1 — Delivered twice (3 marks)

A push subscription delivers a message to the course application, which runs the job and
returns success. The success response is **lost on the network** before the broker receives
it.

1. What does the broker do next, and why can it not do anything better? *(1 mark)*
2. In `run_job`, what check makes this harmless, and what exactly does it test? *(1 mark)*
3. Describe an interleaving in which that check is **not** enough and the work is still done
   twice. *(1 mark)*

## Question 2 — Retries inside retries (3 marks)

- A client waits up to **60 s** for each attempt and makes **up to 3 attempts**.
- For each attempt, the service calls a database with a **10 s** timeout and makes **up to 4
  attempts** before giving up.

The database stops answering entirely.

1. What is the worst-case time before the client gets a final answer? Show the arithmetic.
   *(1 mark)*
2. How many calls does **one** client request cause the database to receive? *(1 mark)*
3. Where should retrying happen instead, and why there? *(1 mark)*

## Question 3 — Budgets and tools (3 marks)

1. A team sets an SLO of **99.5%** of requests succeeding, measured over **30 days**. How much
   total failure time does that permit? Show the arithmetic. *(1 mark)*
2. A single customer reports that **their** job submissions have been slow since yesterday.
   Your dashboard's latency percentiles look normal. Which of logs, metrics or traces do you
   reach for first, what exactly do you search for, and why did the dashboard not show it?
   *(2 marks)*

## Question 4 — The two habits (4 marks)

**(a) Cleanup.** At the end of Lab 5 a student deletes their service. The teardown script
prints no errors, and the student writes "all resources deleted".

1. Name the Lab 5 resource that most plausibly keeps costing money, and explain *why* it
   costs money when nothing is using it. *(1 mark)*
2. What should the submission contain instead of the sentence, and why? *(1 mark)*

**(b) Continuous integration.** The workflow that has run on every push since week 3 tests
on two Python versions with `fail-fast` set to `false`.

1. What information would you lose if `fail-fast` were left on? *(1 mark)*
2. A student writes: "CI passed, so this change is safe." Name **one** specific kind of
   problem this workflow could not have caught. *(1 mark)*
