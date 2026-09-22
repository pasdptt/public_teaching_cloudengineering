# Week 6 — Teaching guide: Storage abstractions

| | |
|---|---|
| **Outcomes** | CLO-4 |
| **Assessment** | **Quiz 3** (weeks 3–5) |
| **Practical** | Lab 3 Parts 1–2 |
| **Prep time** | ~3.5 h first delivery, ~1 h subsequently |

## Session objectives

1. Distinguish block, file, object and database storage **by access pattern**, not by product.
2. Explain why object storage has no partial write or append, and what follows for design.
3. Distinguish durability from availability, and name what a durability figure does not cover.
4. Justify a storage choice for a stated workload, including the rejected options.
5. Explain the three components of storage cost and where operations dominate.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| Four abstractions | 25 | Each by access pattern. Block → their Lab 2 boot disk. |
| **Object storage properly** | 25 | No partial write, no append. Why that changed architecture. |
| Durability vs availability | 15 | What eleven nines does and does not claim |
| Break | 10 | |
| Access control on storage | 10 | Uniform access, public access prevention. Week 1's boundary, made concrete. |
| Storage cost | 10 | Storage, operations, egress. **Class A vs Class B asymmetry.** |
| **Quiz 3** | 15 | Weeks 3–5 |
| Discussion | 10 | The Lab 3 selection decision, argued aloud before anyone writes it |
| Practical | 60 | Lab 3 Parts 1–2 |

**180 minutes exactly.** 85 concepts · 15 quiz · 10 discussion · 60 practical, plus the break.

---

## Teaching notes

### Make them choose before you tell them

Open with the two things the application stores — documents and job records — and ask the
room where each should go, before any of the four abstractions have been named. Collect
answers. Then introduce the abstractions as the vocabulary for the argument they have
already started having.

The reason this works: by the time you name object storage, they have already articulated
"the documents never change after they're written", which *is* the justification. Given the
vocabulary first, students reach for the product name and skip the reasoning.

### The no-append property is the one that matters

Students accept "object storage is for files" and miss the consequence. Push on it:

> You have a 1 GB log file in a bucket. Append one line. What happens?

The answer — you upload the whole GB again — usually lands as a surprise. Then the payoff:
*this is why nobody puts a database on object storage, and why append-only workloads use
many small objects instead.*

### Be precise about durability

"Eleven nines" invites a false sense of safety. Ask what it protects against, then walk the
list it does not cover: your own bad `for` loop, a stolen credential, a deleted account.
Land on:

> **Replication protects against the media. Versioning and backups protect against you.**

Then connect it to money: versioning on means deleted objects still cost, which is on Lab 3's
graded teardown.

### The Class A / Class B asymmetry

Put the numbers up — 5,000 Class A, 50,000 Class B per month free. Ask what a tenfold
difference implies about relative cost, and therefore which operations to be careful with.

Then flag, without solving it, that Lab 3's `exists()` can be written either way and both
pass the tests. Do not tell them which is which; question 3 in the stub docstring asks them.

---

## Discussion (10 min): argue the selection out loud

Put the two workloads on screen with their access patterns. Two teams: one argues job records
belong in object storage, the other that documents belong in a database. Both are wrong, and
being made to argue a bad case is the fastest way to find the reasons.

Expect to draw out: no query, no atomic update and a read-modify-write race for job records in
a bucket; per-byte cost, record size limits and no streaming for documents in a database.

Those are exactly the paragraphs band B1 of the rubric wants, so tell them to write down what
their opponents said.

---

## Common misconceptions

| Misconception | Surfaces as | Response |
|---|---|---|
| "Object storage is just a network filesystem" | Constantly | Append one line to a 1 GB object. What happens? |
| "Eleven nines means my data is safe" | Durability block | Safe from disks. Not from you. |
| "Durability and availability are the same" | Quiz answers | One is "does it still exist", the other "can I reach it now". |
| "Storage cost is per gigabyte" | Cost block | Three components. Many tiny objects can cost more in operations than in storage. |
| "A bucket is private by default so we're fine" | Access-control block | Default-private and *cannot-be-made-public* are different guarantees. The second survives the next person. |
| "We'll pick the database later" | Selection discussion | Then you will pick it by familiarity. The access pattern is known now. |

---

## Practical (60 min): Lab 3 Parts 1–2

- **Part 1 is writing, not typing.** Some students will want to skip to the code. The
  decision record is 12 of the 40 explanation marks — the single largest item in the rubric.
- **`gcloud auth application-default login`** is the first real stumble. It is a *different*
  credential from `gcloud auth login`, and the difference is worth explaining once to the
  whole room rather than five times individually.
- **Bucket naming** is globally unique. The `${PROJECT_ID}-` prefix in the lab exists for
  that reason; someone will drop it and be confused.
- **Watch for `exists()` by download.** It passes. Note who did it and raise it next week
  rather than correcting it now — their own answer to question 3 is worth more.

End by reminding them: the contract tests are the same ones `LocalStorage` passes. If their
Cloud Storage backend passes them, they have proved the backends are interchangeable — which
is the whole lab in one sentence.

## Links

- Student notes: `weeks/week-06/student-notes.md`
- Lab: `labs/lab-03/README.md` · Rubric: `labs/lab-03/rubric.md`
- Contract: `application/tests/contracts.py`
- Solutions and mistake list: private repo, `lab-solutions/lab-03/`
