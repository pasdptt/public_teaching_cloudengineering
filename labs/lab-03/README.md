# Lab 3 — State and storage

**Weeks 6–7 · 7.5% of the final grade · Individual submission**

| | |
|---|---|
| **Cloud resources** | One Cloud Storage bucket (`us-central1`), the project's free `(default)` Firestore database |
| **Estimated cost** | **$0.00.** Both sit inside Always Free allowances. |
| **Outcomes** | CLO-4 (selecting storage and data services), CLO-5 (stateless design) |
| **Estimated novice time** | ~2 h guided (2 × 60 min) + ~5 h independent over two weeks |
| **Observed pilot time** | *not yet measured* |

---

## Why this lab exists

In Lab 1 you learned that job records died with the process and fixed it by writing them to
a file. In Lab 2 you put the application on a machine you do not own — and that file went
onto *that machine's* disk.

Which is fine, right up until there are two machines. In Lab 4 there will be. Two instances
means two files, which means two different answers to "what is the status of job X", and a
user who gets a different answer depending on which instance served them.

This lab moves state to somewhere that belongs to **no instance**. That is the precondition
for everything in weeks 8–11: you cannot have stateless execution until state has somewhere
else to live.

You will also make a real **selection decision** and have to defend it — which is CLO-4, and
which is the part most likely to matter in your working life.

## Before you start

- [ ] Lab 2 submitted, and its resources torn down and verified.
- [ ] `pip3 install -r application/requirements.txt` (the two cloud client libraries — this
      is the first lab that needs any dependency at all).
- [ ] Your trial has not expired.

---

## Part 1 — Choose, before you build (~45 min)

The application needs two different things stored, and they are not the same kind of thing.

**Documents** are bytes. Written once, read many times, never modified, potentially large,
and nobody queries their contents.

**Job records** are small structured objects. Created, then updated several times as the job
moves `pending → running → succeeded`, looked up by id, listed by recency, and searched by
idempotency key.

**Write a decision record** — half a page, and it is worth real marks. For each of the two:

1. Which storage abstraction fits: block, file, object, or database? Say **why**, using the
   access pattern rather than the service name.
2. What are you giving up by choosing it? Name one thing that becomes hard.
3. What would have to change about the workload to reverse your decision?

**Then account for the two you rejected.** Why not put job records in object storage? Why
not put documents in a database? Both would *work*. A student who can only say "that's not
what it's for" has not made a decision; they have followed a convention.

Finally, consider this table and answer the question underneath it:

| Service | Idle cost | Free quota |
|---|---|---|
| Cloud Storage | none | 5 GB-months, 5,000 Class A + 50,000 Class B ops/month |
| Firestore | **none** | 1 GiB, 50,000 reads / 20,000 writes / 20,000 deletes **per day** |
| Cloud SQL (smallest instance) | **billed per hour whether or not anything connects** | none |

**This course chose Firestore, and idle cost is the reason** (decision D-20). One student
forgetting to delete a Cloud SQL instance would cost more than every other lab in this course
combined. Do you agree with that reasoning? Give a workload for which it would be the wrong
call — because there certainly is one.

## Part 2 — Documents into object storage (~90 min)

Create the bucket:

```bash
gcloud storage buckets create "gs://${PROJECT_ID}-docapp-lab3" \
  --project="$PROJECT_ID" \
  --location=US-CENTRAL1 \
  --uniform-bucket-level-access \
  --public-access-prevention
```

Both of those last two flags are decisions. Look up what each prevents and say, in your
submission, what would be possible without them.

Now implement `GcsStorage` in `application/docapp/gcs_storage.py`. It is a stub with four
methods to write. **The acceptance tests are the specification, and they are the same
contract `LocalStorage` already passes:**

```bash
cd application
DOCAPP_TEST_BUCKET="${PROJECT_ID}-docapp-lab3" python3 -m pytest -m lab03 -q
```

Read `tests/contracts.py` first. Notice that it contains no Cloud Storage-specific rules at
all — that is the point of this lab in one file.

The class docstring asks you four questions. **Answer them in your submission.** Question 3
in particular has a cost consequence most people never notice.

**Checkpoint.** The contract passes, and the application runs against the real bucket:

```bash
DOCAPP_STORAGE=gcs DOCAPP_BUCKET="${PROJECT_ID}-docapp-lab3" python3 -m docapp
```

**Then the interesting bit.** With the application running on object storage, delete the
local `data/` directory entirely. Restart. Fetch a document you created earlier.

**Record what happened and why.** Then answer: in Lab 1 you saw a containerised document
disappear because it was on storage that was itself disposable. What exactly is different
now, and how would you convince a sceptic rather than just asserting it?

## Part 3 — Job records into Firestore (~90 min)

Create the database — **the free `(default)` one**:

```bash
gcloud firestore databases create --location=nam5 --project="$PROJECT_ID"
```

There is **one free Firestore database per project**, and it must be `(default)`. A *named*
database qualifies for no free quota at all and bills from its first operation
(`course/references.md` R-11). Do not create one.

Implement `FirestoreJobStore`. Same deal: stub, five design questions in the docstring,
acceptance tests that are the same contract `MemoryJobStore` passes.

```bash
DOCAPP_TEST_PROJECT="$PROJECT_ID" python3 -m pytest -m lab03 -q
```

**Question 4 is the one to think hardest about.** `count()` has a cheap implementation and
an expensive one, both of which pass every test. Work out which you wrote and what it would
cost on a collection of 10,000 jobs.

**Checkpoint.** Both backends together, end to end:

```bash
DOCAPP_STORAGE=gcs DOCAPP_BUCKET="${PROJECT_ID}-docapp-lab3" \
DOCAPP_JOBSTORE=firestore DOCAPP_PROJECT_ID="$PROJECT_ID" \
python3 -m docapp
```

Create a document and a job. Stop the process. **Delete `data/` again.** Start it. Everything
is still there.

## Part 4 — The experiment (~60 min)

**Change one variable. Measure. Explain.**

You now have three storage configurations for the same application. Measure all three with
the same tool and the same settings:

```bash
# A: everything local
DOCAPP_STORAGE=local DOCAPP_JOBSTORE=memory python3 -m docapp
python3 tools/measure.py --requests 12 --concurrency 1

# B: documents in Cloud Storage, job records in memory
# C: documents in Cloud Storage, job records in Firestore
```

Three runs each. Record a table with conditions stated.

**Explain, in about 250 words:**

1. How much latency did each move add? Attribute it — what is the application doing now that
   it was not doing before?
2. You are in Bangkok and the services are in Iowa. Using your Lab 2 numbers, how much of
   the increase is network round-trip and how much is the service itself? Show the
   arithmetic, and say where your estimate is weakest.
3. One job now involves several round trips to Iowa. Count them by reading `service.py`.
   Would the same code run faster if it were deployed in `us-central1` too? You will find
   out in Lab 4 — commit to a prediction now.
4. The durability you gained is not free. State the cost you measured, in milliseconds, and
   say whether you would pay it for this application. That is a judgement, not a
   calculation, and it should be defensible either way.

## Part 5 — Teardown and verification (~25 min) · **graded**

```bash
gcloud storage rm -r "gs://${PROJECT_ID}-docapp-lab3"
gcloud storage ls --project="$PROJECT_ID"
gcloud firestore databases list --project="$PROJECT_ID"
```

**Two things that are different this time**, and both are on the graded list:

- **Object versions.** If versioning is on, deleting the visible object leaves a version
  behind that still occupies storage. Check, and say how you checked.
- **The Firestore database.** You may keep it — an empty Firestore database costs nothing,
  which is exactly why it was chosen. But **empty the collection**, and say in your
  submission which you did and why. "It's free so I left it" is an acceptable answer *if you
  can show it is free*.

Include the verification output.

---

## What to submit

`lab03-<your-name>.md`, plus your two implementations.

1. **The decision record** from Part 1, including the two rejected options and your view on
   the Firestore-vs-Cloud SQL reasoning.
2. **Your `GcsStorage`**, plus the four docstring answers, plus what the two bucket flags
   prevent.
3. **Your `FirestoreJobStore`**, plus the five docstring answers.
4. **The `data/`-deletion demonstration** and your "convince a sceptic" answer.
5. **The experiment** — table and ~250-word explanation, with your Lab 4 prediction.
6. **Teardown verification**, including the versioning check and your Firestore decision.
7. **Cost estimate vs actual**, with the free-tier allowance that covers each line.
8. **AI-assistance disclosure.**

## Resource inventory

| Resource | Removed by | Watch |
|---|---|---|
| Cloud Storage bucket + objects | `gcloud storage rm -r` | **Object versions**, if versioning is on |
| Firestore `(default)` database | may be kept — empty it | Named databases bill; `(default)` does not |
| Firestore documents | delete the collection | 20,000 deletes/day free — plenty |

## Troubleshooting

**`403 Forbidden` from Cloud Storage** — your local credentials, not the bucket. Run
`gcloud auth application-default login`. Note that this is a *different* credential from
`gcloud auth login`, and understanding why is worth five minutes.

**`404 Not Found` creating the Firestore database** — the location format. Firestore uses
multi-region names like `nam5`, not `us-central1`. Check current documentation.

**`the (default) database already exists`** — good. Use it.

**`FAILED_PRECONDITION: The query requires an index`** — your query needs a composite index.
Before creating one, ask whether you need the `order_by` you added. The intended
implementations need no composite index at all.

**Tests skip rather than run** — the environment variables are not set. That is the guard
working: these tests touch real resources and never run by accident.

**`NotImplementedError: GcsStorage is your Lab 3 exercise`** — you set `DOCAPP_STORAGE=gcs`
before doing Part 2. Use `local` until then.

**Everything is much slower than Lab 2** — yes. That is Part 4, and it is the finding.
