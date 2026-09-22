# Lab 3 — Rubric

**7.5% of the final grade.** Same four bands as every lab. Primary evidence for **CLO-4**.

| Band | Share |
|---|---|
| A. Working implementation | **35** |
| B. Conceptual explanation and evidence | **40** |
| C. Reproducibility, security and resource handling | **15** |
| D. Communication | **10** |

---

## A · Working implementation — 35 marks

| | Marks | Looks like |
|---|---|---|
| Excellent | 31–35 | Both backends pass the full contract. The application runs end to end on `gcs` + `firestore`, survives deletion of the local `data/` directory, and the idempotency key still works across a restart. Implementations are compact and use the cheap operation where there is a choice. |
| Good | 24–30 | Both pass the contract; one expensive-but-correct choice (e.g. `exists` by download, `count` by streaming) left unremarked. |
| Developing | 14–23 | One backend passes. Or both pass but a contract detail is violated — `get` returning `None`, a delete that is not idempotent. |
| Limited | 0–13 | Neither passes, or the application cannot start on cloud backends. |

**Note for the marker:** an expensive implementation that the student *identified themselves*
in their docstring answers belongs in Excellent, not Good. Noticing is the skill.

## B · Explanation and evidence — 40 marks

### B1 · The decision record (12) — **the heart of the lab**
| | Looks like |
|---|---|
| Excellent | Both choices justified from the **access pattern**, not the service name. Names what each choice makes hard, and a condition that would reverse it. **Engages seriously with both rejected options** — why job records in object storage is bad (no query, no atomic update, read-modify-write races) and why documents in a database is bad (cost per byte, size limits, no streaming). Takes a real position on the Firestore-vs-Cloud SQL reasoning and supplies a workload where it would be wrong. |
| Good | Choices justified, rejected options mentioned but thinly. |
| Developing | Justifies by convention — "object storage is for files" — without an access-pattern argument. |
| Limited | Describes what was built. |

> The rejected-options paragraph is the highest-signal thing in this submission. A student
> who can only defend what they chose has not made a decision.

### B2 · Backend design answers (10)
The four `GcsStorage` and five `FirestoreJobStore` questions. Full marks need:
- **GCS q3** — `exists` as a metadata call vs a download, with the Class A/Class B allowance
  difference understood.
- **Firestore q4** — `count()` via aggregation vs streaming, and what streaming would cost on
  10,000 documents against a 50,000-reads-per-day quota.
- **GCS q4** — why key validation is retained even though an object store would accept `..`.
  The answer is interchangeability, and it is the whole premise of the Protocol seam.

### B3 · Durability demonstrated (6)
The `data/`-deletion demonstration, and a **convincing** account of what is different from
Lab 1's disappearing container document. Full marks distinguish *where* the bytes are from
*whose lifecycle they share* — and convince rather than assert.

### B4 · The experiment (12)
| | Looks like |
|---|---|
| Excellent | Three configurations, three runs each, conditions stated. Latency increase **attributed** to specific added work. Network round-trip separated from service time using their own Lab 2 numbers, with the weakest part of the estimate named. Round trips counted by reading `service.py`. A committed Lab 4 prediction. A defensible judgement on whether the durability is worth the milliseconds. |
| Good | Data correct, attribution present, the judgement thin or hedged. |
| Developing | Single runs, or latency reported without attribution. |
| Limited | No measurements, or figures inconsistent with the setup described. |

> **Fabricated measurements score zero for the whole lab.** An experiment that failed,
> honestly reported and well reasoned, can still reach Excellent.

## C · Reproducibility, security and resource handling — 15 marks

| | Marks | Looks like |
|---|---|---|
| Excellent | 13–15 | Bucket removed and verified, **including the object-versioning check**. An explicit, justified decision about the Firestore database with evidence that keeping it is free. Cost estimate compared against actuals, each line traced to the allowance covering it. Both bucket flags explained. No credentials anywhere. |
| Good | 10–12 | Verified clean; versioning check missing, or the Firestore decision asserted rather than evidenced. |
| Developing | 5–9 | Teardown claimed without verification, or a bucket left behind. |
| Limited | 0–4 | Resources left, or a credential in the submission. |

**Automatic zero for this band:** a service-account key JSON anywhere. Nothing in this lab
needs one — `gcloud auth application-default login` is the local path and an attached
identity is the deployed one.

## D · Communication — 10 marks

Clear, concise, honest. The decision record should read like something a colleague could act
on. Uncertainty stated as uncertainty earns marks here.

---

## Standing rules

- An unsuccessful experiment earns full analysis credit when the evidence is real and the
  reasoning sound.
- **Fabricated evidence earns zero.**
- Screenshots alone are not evidence.
- **No marks for spending more** — no second bucket "for comparison", no named Firestore
  database, no Cloud SQL instance to see what it is like. The brief forbids deploying
  several databases for comparison, and the free tier forbids it more firmly.
- **Cleanup claimed but not verified earns nothing in band C.**
- AI assistance is permitted and must be disclosed.

## Marking notes

Expected marking time: **20–30 minutes per student**. Band A is mechanical — run the contract
tests against their code with your own bucket and project.

Read **B1's rejected-options paragraph first.** It predicts the quality of the project's
architecture section better than anything else in this lab, and it is the cheapest place to
correct a student who is choosing by convention rather than by reasoning.

After this lab, check that no student created a **named** Firestore database. It bills from
the first operation, it looks identical in the console, and it is the one way this lab can
quietly cost money.

Full solutions and the common-mistake list: private repo, `lab-solutions/lab-03/`.
