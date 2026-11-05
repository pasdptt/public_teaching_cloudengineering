# Quiz 4 — Storage, consistency, and what a machine commits you to

**Covers weeks 5–7**, including Labs 2 and 3. Taken in week 9, in the discussion block — the
managed-execution material taught in that session is not assessed here. Outcomes: CLO-1,
CLO-2, CLO-4.

**12 marks · about 12 minutes · closed book · individual.** Short answers are fine. Name the
*kind* of storage or the *property*; product names earn nothing extra.

---

## Question 1 — Pick by access pattern (4 marks)

A new feature is added to a web application. It stores two kinds of data:

- **Profile photos.** Uploaded once, displayed many times, never edited — a new photo replaces
  the old one entirely.
- **Recent activity.** For each user, a list of their last 20 actions. Updated on every action
  the user takes, and read back by user id.

For **each**:

1. Choose block, file, object or database storage, and give **one** reason tied to how the
   data is read and written. *(1 mark each)*
2. State **one** thing your choice makes difficult later. *(1 mark each)*

## Question 2 — "Eleven nines" (2 marks)

A teammate argues:

> "Our bucket is quoted at eleven nines of durability. Versioning and backups would be
> paying twice for protection we already have."

Name **two** ways the data could still be lost that the durability figure does not cover, and
for each, say which side of the shared-responsibility boundary it falls on.

## Question 3 — Stale reads and a race (3 marks)

The course application performs these two reads against its job store:

- **R1** — `GET /jobs/{id}`: read a job's status to show the user.
- **R2** — during `POST /jobs`: look up the `Idempotency-Key` to see whether this submission
  has already been accepted.

1. Suppose the job store were **eventually consistent**. For each read, say what a stale
   result would cause, and whether a user would notice. *(1 mark)*
2. Now suppose the store is **strongly consistent**. Two requests with the **same**
   idempotency key arrive at almost the same moment. Describe the interleaving that still
   produces a duplicate job. *(1 mark)*
3. What would be needed to prevent that duplicate? *(1 mark)*

## Question 4 — Choosing a machine (3 marks)

In Lab 2 you ran the application on a virtual machine that you created and operated.

1. Name **two** things you had to do yourself, in Lab 2, for the application to keep serving
   and to stop costing money — things that existed only because the unit of deployment was a
   whole machine. *(1 mark)*
2. An internal tool is used for about **ten minutes a day** by five people. A colleague
   proposes a small VM, "the same as Lab 2". Argue for or against, naming **one concrete cost**
   of the choice for this particular workload — not a generic pro or con. *(2 marks)*
