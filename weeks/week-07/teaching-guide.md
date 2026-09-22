# Week 7 — Teaching guide: Replication, consistency and choosing a data service

| | |
|---|---|
| **Outcomes** | CLO-4, CLO-5 |
| **Assessment** | **Lab 3 due** at the end of this week |
| **Practical** | Lab 3 Parts 3–5 |
| **Prep time** | ~3.5 h first delivery, ~1 h subsequently |

## Session objectives

1. Explain what replication buys and the problem it creates.
2. Distinguish strong, eventual and read-your-own-writes consistency by observable behaviour.
3. Decide, per operation, whether staleness is acceptable.
4. Identify when a transaction is required, and find a check-then-act race in real code.
5. Select a data service using a checklist that includes idle cost.
6. Explain why the application holding no state is the precondition for weeks 8–11.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| Replication | 10 | What it buys; the disagreement window it creates |
| **Consistency models** | 25 | Three models by observable behaviour, not by definition |
| Per-operation reasoning | 15 | Two reads in *their* application with different requirements |
| Break | 10 | |
| **Transactions and the race** | 20 | **Live: find the check-then-act in `service.py`** |
| Choosing a data service | 15 | The checklist. Idle cost, and why it decided this course. |
| Discussion | 25 | Same workload, three candidate stores, defend one |
| Practical | 60 | Lab 3 Parts 3–5 |

**180 minutes exactly.** 85 concepts · 25 discussion · 60 practical, plus the break.

---

## Teaching notes

### Teach consistency by consequence

Definitions of consistency models are forgettable. Consequences are not. Use their own
application:

- *Job status read one second stale.* Who notices? Nobody — the page says "running" for a
  moment longer.
- *Idempotency-key lookup that misses a just-written key.* What happens? **A second job.** A
  user-visible duplicate.

Same application, same database, two completely different requirements. That is the whole
lesson, and it lands far harder than a definition of linearizability.

### The race is the centrepiece — do it live

Open `application/docapp/service.py` and put `create_job` on screen. Walk them through:

```
    check for existing idempotency key   <-- request A reads: nothing there
                                         <-- request B reads: nothing there
    create a job                         <-- A creates
                                         <-- B creates
```

Ask: *how many jobs, and what was the idempotency key supposed to guarantee?*

Then connect it backwards: this is precisely the race their Lab 1 `FileJobStore` had between
threads, which they fixed with a lock. Ask why a lock does not work now. Land on: a lock is
scoped to one process, and there are about to be several.

**Do not fix it.** Lab 3 does not ask them to. Being able to *see* it is the objective, and
an unfixed known race that the class can articulate is a better teaching artefact than a
correct implementation nobody examined.

### Idle cost decided this course — say so

Put the comparison up: Firestore, no idle charge; Cloud SQL, billed per hour connected or
not. Then say plainly that decision D-20 was made on this basis, and that a relational
database would have been technically reasonable.

Then invite disagreement. Lab 3 asks for a workload where the reasoning fails, and the honest
answer is that a system with complex relational queries and steady traffic is never idle, so
idle cost is irrelevant to it. A student who produces that has understood that the decision
was **contextual**, not a ranking of databases.

---

## Discussion (25 min): defend one

One workload — "a small service storing 50,000 user profiles, read by id on every request,
updated rarely, with an occasional report grouping users by country". Three candidates: a
document store, a relational database, object storage.

Ten minutes in groups, then each defends a choice and takes questions.

The productive disagreement is the report query. Object storage is eliminated fast; the
document-store-versus-relational argument turns on how much that one grouping query matters
and whether it justifies a different data model for the 99% case. Let it stay unresolved —
"it depends, and here is what it depends on" is the correct professional answer and students
are rarely allowed to give it.

---

## Common misconceptions

| Misconception | Surfaces as | Response |
|---|---|---|
| "Eventual consistency means unreliable" | Consistency block | It means a window. Ask how long, and who notices. |
| "We need strong consistency everywhere" | Selection discussion | Per operation. Which of *your* reads would a user notice as stale? |
| "Transactions are a database feature you turn on" | Transactions block | They are a guarantee you need or do not. Show the race first. |
| "The lock fixed it in Lab 1, so we're fine" | After the race demo | One process. Ask what a lock means across three instances. |
| "Firestore is better than Cloud SQL" | After the cost comparison | Better *for this*, on idle cost. Ask for a workload where it loses. |
| "We're on a managed database so backups are handled" | Operational-burden block | Check. Then check retention. Then check whether you can restore. |

---

## Practical (60 min): Lab 3 Parts 3–5

Watch for:

- **A named Firestore database.** This is the one way this lab can quietly cost money — a
  named database qualifies for no free quota and bills from the first operation. Say it out
  loud before they start, and check afterwards.
- **Location format.** Firestore wants a multi-region name like `nam5`, not `us-central1`.
  Expect at least one confused student.
- **`count()` by streaming.** Passes every test. Note who; their own question-4 answer is the
  teaching moment, so do not pre-empt it.
- **Composite index errors.** Almost always an unnecessary `order_by` in
  `find_by_idempotency_key`. The intended implementations need no composite index.
- **Part 4 single runs.** Insist on three.

**Before anyone leaves:** bucket deleted, versioning checked, verification output shown. And
remind them of Part 4's prediction question about deploying in the same region — Lab 4
settles it, and a committed prediction now is worth marks then.

## Links

- Student notes: `weeks/week-07/student-notes.md`
- Lab: `labs/lab-03/README.md` · Rubric: `labs/lab-03/rubric.md`
- The race: `application/docapp/service.py`, `create_job`
- Next week: managed execution — the application that now holds no state gets several copies
