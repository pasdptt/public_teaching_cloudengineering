# Week 7 — Replication, consistency and choosing a data service

**Lab 3 is due at the end of this week.**

---

## Why replication exists, and what it costs

A single copy of your data has a single point of failure. So systems keep several, on
independent hardware, often in independent failure domains.

That buys durability and availability. It costs you something subtler: **now there is more
than one copy, and for some window of time they can disagree.** Every consistency model is an
answer to "what do readers see while the copies are catching up?"

## Consistency, in plain terms

**Strong consistency.** Once a write is acknowledged, every subsequent read sees it. Simple to
reason about, and it costs latency — the write cannot be acknowledged until enough replicas
agree, and "enough replicas" may be far away.

**Eventual consistency.** A write will propagate, and until it has, a reader may see the old
value. Cheaper and faster, and it makes a class of bug that is hard to reproduce: the write
succeeded, you immediately read it back, and it was not there.

**Read-your-own-writes.** A weaker but very practical guarantee: *you* see your own writes
immediately, others may lag. Often enough, and often much cheaper than full strong
consistency.

The question that matters is not "which is better" but:

> **What would a user actually notice if they read a stale value here?**

For the course application: a job status read one second stale is invisible. A deduplication
lookup that misses a just-written idempotency key creates a **second job** — a user-visible
duplicate. Same application, two different requirements.

## Transactions, and when you need one

A transaction makes several operations atomic: all of them happen, or none does.

You need one when a half-completed change leaves the system **wrong**, not merely
out of date. The classic case is moving value between two records. In the course
application: check for an existing idempotency key, then create a job if there is none. Two
concurrent requests can both check, both find nothing, and both create — and you have the
duplicate that idempotency was supposed to prevent.

Notice this is the same problem your Lab 1 `FileJobStore` had between threads, and you solved
it with a lock. A lock works within one process. Across machines it does not, and a
transaction is the distributed answer.

**You are not asked to fix this in Lab 3**, and the application has the race today. You *are*
asked to be able to see it. Being able to point at the check-then-act in `service.py` and say
"those two operations are not atomic, and here is the user-visible consequence" is exactly
what week 7 is for.

## Choosing a data service

Work down this list. Stop when it is answered:

1. **Access pattern.** By key, by query, by range, by full-text? This eliminates most options.
2. **Consistency requirement**, *per operation* rather than for the whole system. You may
   need strong consistency for one lookup and not care elsewhere.
3. **Transactions**, and across how many records.
4. **Scale and shape** — record count, record size, read/write ratio.
5. **Operational burden.** Who patches it, backs it up, and is woken when it breaks?
6. **Cost, including when idle.** The one beginners skip.

That last one decided this course. Compare:

| | Idle cost | Free quota |
|---|---|---|
| **Firestore** | **none** | 1 GiB, 50,000 reads / 20,000 writes / 20,000 deletes per day |
| Cloud SQL, smallest instance | **billed per hour, connected or not** | none |

A relational database would be a perfectly reasonable choice for this workload on technical
grounds. It was rejected on **idle cost**: one student forgetting to delete an instance would
cost more than every other lab in this course combined (decision D-20).

Lab 3 asks whether you agree, and for a workload where that reasoning would be wrong. There
certainly is one — a system with complex relational queries and steady traffic would not
care about idle cost at all, because it is never idle.

## What you are actually doing in Lab 3

Job records move from a file on one machine to a service that belongs to no machine.

That is not just durability — you had durability in Lab 1. It is that **no instance owns the
state any more.** In Lab 4 there will be several instances, and every one of them will see
the same job records. Without this week, that would be impossible.

After Lab 3 the application holds nothing of its own. Kill it, start it elsewhere, run three
copies: same answers. That property is what the next four weeks are built on.

## Cost reasoning inside your implementation

Two choices in Lab 3 both pass every test and differ in cost:

- `exists()` as a metadata lookup (Class B, 50,000/month free) or as a download that throws
  the bytes away (Class A, 5,000/month free).
- `count()` as an aggregation query, or by streaming every document and counting them. The
  second reads 10,000 documents to count 10,000 jobs, against a quota of 50,000 reads a day.

Neither is caught by a test. Both are the kind of thing that is invisible at lab scale and
obvious on a bill. Noticing it yourself is the skill being assessed.

## This week's work (~180 minutes)

| | |
|---|---|
| Read these notes | 25 min |
| Lab 3 Parts 3–5: Firestore, the experiment, teardown | 155 min |

**Lab 3 is due at the end of this week**, with teardown verification.

## Check yourself

1. What does replication buy, and what new problem does it create?
2. Strong vs eventual consistency, in one sentence each, with a user-visible difference.
3. In the course application, name one read where staleness is invisible and one where it
   produces a duplicate.
4. When do you need a transaction rather than just a careful order of operations?
5. Find the check-then-act race in `service.py`. What is the user-visible consequence?
6. Why was Firestore chosen over a relational database for this course, and for what
   workload would that reasoning be wrong?
7. Two implementations of `count()` pass every test. Why is one much more expensive, and how
   would you have noticed without a bill?

## Next week

Managed container execution and serverless: what you stop operating, why statelessness is the
price of admission, and cold starts. Lab 4 starts — the application you just made stateless
gets deployed somewhere that can run several copies of it.
