# Lab 5 — Rubric

**7.5% of the final grade.** Same four bands as every lab. Primary evidence for **CLO-5**,
with substantial CLO-6.

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
| Excellent | 31–35 | All fourteen offline `lab05` tests pass. The service is deployed with `DOCAPP_QUEUE=pubsub`, a push subscription delivers to it, and a submitted job goes `pending → succeeded` without intervention. Three identities exist and each is scoped to what it needs — the push account holds `run.invoker` on **the service**, not the project. The dead-letter configuration is in place and demonstrably works. |
| Good | 24–30 | Working end to end, but one shortcut taken silently: a project-level invoker grant, or a dead-letter policy that was never shown to fire. |
| Developing | 14–23 | The envelope decoder passes but the deployed path does not work, and the submission does not establish why. Or it works with the service made public, removing the identity problem rather than solving it. |
| Limited | 0–13 | Jobs never reach a terminal state, with no evidence of what was tried. |

**Note for the marker:** Part 1 is entirely local. A student who did Parts 1 and 2 well and
could not get the cloud path working — and who says precisely where it broke and what they
ruled out — should not fall below Developing. The conceptual content of this lab is in the
local half.

## B · Explanation and evidence — 40 marks

### B1 · Idempotency, and what the evidence supports (12) — **the heart of the lab**
| | Looks like |
|---|---|
| Excellent | Both experiments reported: the local one where duplicates happen on demand, and the cloud one where the same message is published repeatedly. **The difference between them is stated correctly** — publishing twice is not the broker redelivering, and the student says which claim each experiment actually supports and why a cloud-only lab would be weaker evidence. The `run_job` early return is named as the mechanism. The interleaving that defeats it is described concretely: two instances, two messages, neither job terminal yet. |
| Good | Both experiments present, mechanism correctly named, the proves/does-not-prove distinction made but thinly. |
| Developing | Reports that duplicates were handled without identifying the mechanism, or treats publishing five messages as proof that Pub/Sub redelivers. |
| Limited | Describes what was built. |

> The proves/does-not-prove paragraph is the highest-signal thing in this submission, and it
> is the same skill as Lab 4's confounds paragraph one level harder. A student who can say
> what their own successful experiment failed to establish is ready for the project.

### B2 · Asynchrony as a client-visible change (8)
The `pending` response and what follows from it. Full marks need the client's polling loop
sketched, an answer for "still pending after five minutes", and the earliest-return question
answered with what would have been given up. A student who treats this as a status-code
change has missed it.

### B3 · The failure experiment and the missing evidence (12)
| | Looks like |
|---|---|
| Excellent | A timeline with real intervals, and a correct reading of the spacing — that it grows, and why evenly-spaced retries would be worse. **The job-record state and the message state distinguished**, with what a user would see. Dead-lettering argued as a decision with a cost, not described. **One specific unanswerable question named**, with what they would add to answer it. |
| Good | Timeline correct, the records-vs-messages gap noticed, the missing-evidence answer generic. |
| Developing | Reports that it failed and recovered, without intervals or interpretation. |
| Limited | No timeline, or a timeline inconsistent with the configuration described. |

### B4 · The topic with no subscription (8)
What was observed, and the design property it demonstrates: a topic is not storage, and
publishing to one with no subscriber discards the message. Full marks connect it to the
Part 0 prediction and say what this implies for the order in which you create things — which
is a Lab 6 problem in disguise.

> **Fabricated measurements score zero for the whole lab.** An experiment that failed,
> honestly reported and well reasoned, can still reach Excellent.

## C · Reproducibility, security and resource handling — 15 marks

| | Marks | Looks like |
|---|---|---|
| Excellent | 13–15 | **The subscription is gone and shown to be gone.** All three identities named with their scopes, and the push account's grant made on the service rather than the project, with the difference explained. `07-verify-clean.sh` output included and clean, including both topics, both service accounts and the registry. The rebuild-from-source is reported honestly, including anything that turned out to be missing. |
| Good | 10–12 | Verified clean, but the project-vs-service grant distinction is asserted rather than explained, or the registry still holds `v1`. |
| Developing | 5–9 | Teardown claimed without verification, or a topic left behind, or the rebuild gaps not reported. |
| Limited | 0–4 | **A subscription left in place**, or a credential in the submission. |

**Automatic zero for this band:**
- A service-account **key JSON** anywhere. Three identities exist in this lab and none of
  them needs one.
- An identity token pasted into the submission.
- `--min-instances` above 0, or a retention period raised beyond the configured bound.

**The subscription is this band's version of Lab 2's static IP**, and it should be marked
with the same seriousness. It is the only resource in this course that bills for holding
data nobody is collecting any more.

## D · Communication — 10 marks

Clear, concise, honest. The Part 0 predictions must be unedited; this lab's question 3 is one
most students get right, and question 4 is one most get wrong, so an unedited set is easy to
recognise and worth trusting.

---

## Standing rules

- An unsuccessful experiment earns full analysis credit when the evidence is real and the
  reasoning sound.
- **Fabricated evidence earns zero.**
- Screenshots alone are not evidence.
- **No marks for spending more** — no second subscription, no longer retention, no warm
  minimum, no pull subscription with a worker running alongside "to compare".
- **Cleanup claimed but not verified earns nothing in band C.**
- AI assistance is permitted and must be disclosed.

## Marking notes

Expected marking time: **25–35 minutes per student.**

**Band A is cheap to check**: run `pytest -m lab05` against their `pubsub_queue.py`. Fourteen
tests, no cloud account, a few seconds. Do this first — it tells you whether to read the
cloud half sympathetically or sceptically.

**Then read B1's proves/does-not-prove paragraph.** It is the single best predictor of how
the project's evidence section will read, and correcting a student here is much cheaper than
correcting them in week 14.

**Check the push identity's grant specifically.** `gcloud run services get-iam-policy` is the
evidence; a project-level binding is the shortcut. Both work, and only one of them can be
explained.

**After this lab, confirm every student's subscriptions list is empty.** This is the last
billable lab, the trial has to reach week 15, and a retained subscription is the one thing
here that quietly consumes it. Check it in the room, in week 11, not in week 13.

Expect two or three students to be defeated by the push identity's second grant — Pub/Sub's
service agent needing token-creator permission. The error message names it. Whether they read
the error or searched for a tutorial is worth knowing, and is worth a minute of the week 11
session either way.

Full solutions, the expected role set and the common-mistake list: private repo,
`lab-solutions/lab-05/`.
