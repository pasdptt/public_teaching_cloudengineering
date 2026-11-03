# Integrative project — rubric

**35% of the final grade**, marked out of 100 and scaled. The project is the main evidence for
**CLO-8** (defending an architecture) and gives further evidence for CLO-4 to CLO-7 and CLO-9.
Requirements are in [`brief.md`](brief.md). References such as **B1** and **B7** are the brief's
baseline requirements.

| Band | Marks | Marked |
|---|---|---|
| A. Architecture and reasoning | **25** | Per group |
| B. Functional implementation | **20** | Per group |
| C. Experiments and interpretation | **25** | Per group |
| D. Reproducibility, security and cost | **20** | Per group |
| E. Communication and individual understanding | **10** | **Per student** |
| | **100** | |

The bands are fixed by decision D-16. Implementation is 20 marks and evidence and reasoning are
70, deliberately: **a smaller system you understand and have measured scores better than a
larger one you have not.**

Every band uses the same four levels as the labs: **Excellent**, **Good**, **Developing** and
**Limited**.

---

## A · Architecture and reasoning — 25 marks

### A1 · Diagram and decision record (10)

| | Marks | Looks like |
|---|---|---|
| Excellent | 9–10 | The diagram shows where state lives, where each identity acts, and where the asynchronous boundary is. The decision record covers the two or three decisions that mattered. For each it names the **rejected alternative** and the **condition under which it would have won**. At least one decision is a cost decision. |
| Good | 7–8 | Diagram and decisions are correct. Alternatives are named, but the reversal condition is missing or generic. |
| Developing | 4–6 | A diagram of boxes with no state or identity shown, or decisions described without any alternative. |
| Limited | 0–3 | A product list, or a diagram that does not match what was built. |

### A2 · Workload drives the design (5)

| | Marks | Looks like |
|---|---|---|
| Excellent | 5 | B1 is stated with a peak, says where the numbers come from, and is **used**: the instance cap, the SLO and the experiment sizes can each be traced back to it. |
| Good | 3–4 | Workload stated and used for some decisions, not all. |
| Developing | 1–2 | Workload stated and then ignored. |
| Limited | 0 | No workload, or "it should scale". |

### A3 · What leaving would cost (10) — CLO-8

| | Marks | Looks like |
|---|---|---|
| Excellent | 9–10 | What transfers is separated from what is a commitment, **specific to this system**: for example the job store's query and consistency semantics, the push envelope, the Terraform resource types. Gives an estimate in weeks, names the piece that dominates, and says which commitment they would make again and why. |
| Good | 7–8 | Correct and specific. The estimate is missing, or which commitment they would make again is not addressed. |
| Developing | 4–6 | Correct in general ("Terraform is portable but the resources are not") but not tied to what was built. |
| Limited | 0–3 | "Vendor lock-in" as a yes/no answer, or a list of the other provider's product names. |

## B · Functional implementation — 20 marks

### B1 · The baseline, through the Lab 6 path (8)

| | Marks | Looks like |
|---|---|---|
| Excellent | 7–8 | Deployed to `dev` and `prod` by the Lab 6 pipeline from one configuration, with the **same image digest** in both, evidenced by run links or digests. The service is private and the asynchronous path still works. |
| Good | 5–6 | Both environments deployed, but promotion was done by hand, or the digest match is asserted rather than shown. |
| Developing | 2–4 | One environment only, or the image was rebuilt per environment. |
| Limited | 0–1 | Not deployed, or deployed by hand outside the pipeline. |

### B2 · The extension (12)

| | Marks | Looks like |
|---|---|---|
| Excellent | 11–12 | The extension does what the proposal said, or what the smallest version agreed in week 13 said, and that is **shown working**: a test, a command and its output, or the experiment itself. Behaviour at the edges is handled honestly. Option A: the race is actually exercised. Option B: the job record is updated. Option C: CPU work is controllable. Option D: the limit holds across instances. |
| Good | 8–10 | Works in the normal case. One edge case is not handled, and the submission says so. |
| Developing | 4–7 | Works only partly, or works but is not shown working. |
| Limited | 0–3 | Not working, and nothing explains why. |

**Falling back to the smallest version is not a penalty.** If the submission explains what was
cut and why, mark B2 against the smallest version agreed at the design review. If no smallest
version was agreed, mark against the proposal.

**No marks for a rebuilt pipeline or extra services.** Building infrastructure the brief said to
reuse earns nothing in this band, and the time it cost usually shows up as missing evidence in
band C.

**Capped at Developing in B1, whatever else is right:** a service-account **key** used anywhere
in the deployment path. The same rule and the same reason as Lab 6. A student who explains
honestly why they fell back to a key stays at Developing rather than Limited.

## C · Experiments and interpretation — 25 marks

### C1 · Performance experiment (10)

| | Marks | Looks like |
|---|---|---|
| Excellent | 9–10 | A **prediction written beforehand**. The question has a measurable answer. One variable changes, conditions are stated, there are at least three runs, and disagreement between runs is reported. The load is sized from B1. The explanation accounts for the result, including where the prediction was wrong. |
| Good | 7–8 | Sound method and result. One weakness: conditions only partly stated, or the explanation describes the numbers rather than accounting for them. |
| Developing | 4–6 | Numbers without conditions, a single run, or two variables changed at once. |
| Limited | 0–3 | No experiment, or a screenshot of a dashboard in place of a measurement. |

### C2 · Failure and recovery experiment (10)

| | Marks | Looks like |
|---|---|---|
| Excellent | 9–10 | One controlled, reversible fault, with a prediction. Records **what the user saw, how the system recovered, and what state the job records and messages were left in**, and notices where those two differ. Says whether the B4 SLO would have survived, with the arithmetic. |
| Good | 7–8 | A real fault, well recorded. The state left behind or the SLO judgement is thin. |
| Developing | 4–6 | A fault was induced, but only "it broke, then it worked" is recorded. |
| Limited | 0–3 | No failure experiment, or one that was not controlled. Example: deleting production data to see what happens. |

### C3 · What the evidence does not show (5)

| | Marks | Looks like |
|---|---|---|
| Excellent | 5 | For each experiment, says specifically what the result **failed to establish**, in the sense of week 14. Names the sample-size, co-location and lower-bound limits that apply. |
| Good | 3–4 | Limits stated, partly generic. |
| Developing | 1–2 | "More testing is needed." |
| Limited | 0 | No limits stated, or claims the result generalises. |

**An experiment that went wrong, explained well, earns full marks.** "I predicted X, observed Y,
and here is why my model was wrong" is an Excellent C1.

## D · Reproducibility, security and cost — 20 marks

| | Marks | Criterion | Excellent looks like |
|---|---|---|---|
| D1 | 4 | `dev`/`prod` differences (B2) | Every difference is justified, the deliberately-the-same list includes the image, and the shared-Firestore risk is stated **for this extension** |
| D2 | 5 | Principals and credentials (B3) | Every principal is listed with its permissions and why. The deployer's breadth is acknowledged and answered. No long-lived credential exists. For pairs: who owns the project, the partner's named-user roles, and no shared login |
| D3 | 6 | Cost model (B5) | Priced at 1× and 10× the workload from published rates, with assumptions stated. Says what grows with use and what does not. The overnight-bug answer names a **setting** and the bill it bounds |
| D4 | 5 | Verified teardown (B6) | Teardown order followed and **listing output** included, covering what Terraform does not track (registry images, deployer identity and federation pool, state bucket last). For pairs: who revoked the partner's access, and when |

For each row, Good means correct but thin, Developing means present but unjustified, and Limited
means missing. Scale the row's marks the same way as the other bands.

**Automatic zero for band D:** a service-account key JSON, a populated `.tfvars`, or a
`terraform.tfstate` committed to the repository, or a shared password between partners. A
committed key must be **rotated**, not deleted.

**Cleanup claimed but not verified earns nothing in D4.** A resource found still running in week
15, *explained*, is not penalised further. That is the outcome week 15 asks students to look for.

## E · Communication and individual understanding — 10 marks, per student

| | Marks | Looks like |
|---|---|---|
| Excellent | 9–10 | The written submission is short and selective. The twelve minutes are kept, and the evidence is shown rather than cut. **Questions are answered about decisions, not facts.** The individual question is answered from the student's own reasoning, including what they would change with more time or budget. "I don't know, but here is how I would find out" counts in their favour. |
| Good | 7–8 | Clear and honest, with one weak answer, or the evidence rushed in the demonstration. |
| Developing | 4–6 | Can describe the system but not defend its decisions, or the written material buries its results. |
| Limited | 0–3 | Cannot explain their own work, or a demonstration that avoids the part that is broken. |

**In a pair, E is marked separately for each student**, mainly from their individual question
and their part of the contribution record. Partners can receive different E marks. Bands A–D are
normally shared, unless the contribution record shows a part one partner did not touch and could
not explain.

**Saying at the start that something is broken is not marked down.** Hiding it is.

---

## Standing rules

- **Fabricated evidence earns zero for the whole project** and is an academic-integrity matter.
  That includes invented numbers, someone else's run presented as one's own, and generated data.
- **An unsuccessful experiment earns full analysis credit** when the evidence is real and the
  reasoning is sound.
- **No marks for spending more.** Not for extra services, environments, instances or credit used.
- **Work the student cannot explain does not earn marks**, whoever or whatever wrote it. AI
  assistance is permitted and must be disclosed. A missing disclosure is handled under the course
  policy, not as a deduction here.
- **The local fallback path is marked against the same descriptors.** Wherever a criterion needs
  a cloud observation the student could not make, mark the reasoning and any clearly labelled
  instructor-supplied evidence instead. A student on that path is not disadvantaged.

## Marking notes

Expected marking time: **30–45 minutes per group**, including the defence notes. This estimate
is from `course/workload-budget.md` and has not been measured.

**Read in this order:** C3, then A3, then the rest. C3 and A3 are the fastest signals of whether
the student understood what they built, and they predict the defence better than anything else in
the submission.

**Write E during or straight after the demonstration**, not from memory at the weekend. Note the
individual question asked and a phrase from the answer.

**Check the week 13 smallest version before marking B2.** It is written at the top of the
proposal, and it is the bar.
