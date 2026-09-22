# Lab 4 — Rubric

**7.5% of the final grade.** Same four bands as every lab. Primary evidence for **CLO-6**,
with substantial CLO-2 and CLO-5.

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
| Excellent | 31–35 | The service is deployed, refuses unauthenticated callers, runs as a purpose-made service account with roles the student chose and can justify, and serves correctly on the Lab 3 backends: forty concurrent status requests, zero 404s, and five retries of one idempotency key producing one job. Both concurrency configurations were deployed and measured. |
| Good | 24–30 | Deployed and working, but one element is done the easy way rather than the right way — a broad role, or the service left public — and the student did not remark on it. |
| Developing | 14–23 | The service runs but the Part 3 fix is incomplete: still on the in-memory job store, or storage and job store not both external. Or only one concurrency configuration was measured. |
| Limited | 0–13 | Not deployed, or deployed but never successfully called, with no evidence of what was tried. |

**Note for the marker:** deploying with `roles/editor` and *saying so*, with an account of
what it grants and what the least-privilege alternative would have been, belongs in Good,
not Developing. Doing it silently belongs in Developing. Recognising a shortcut is most of
the skill.

**A failed Part 3 reproduction is not an implementation failure.** A student whose 40
concurrent requests never produced a 404, who says so, explains why their client or the
platform did not fan out, and reasons about what that implies for catching this class of bug
in testing, has satisfied this band's intent.

## B · Explanation and evidence — 40 marks

### B1 · The Part 4 experiment (12) — **the heart of the lab**
| | Looks like |
|---|---|
| Excellent | Both configurations, three runs each, conditions stated for every row. Latency and throughput reported separately and the difference between them explained rather than noticed. Instance counts compared against the Part 0 prediction with the discrepancy accounted for. The waiting-vs-computing question answered as a prediction and **labelled as one**. A shipping recommendation with the evidence that would overturn it. |
| Good | Data correct and conditions stated; the latency/throughput distinction present but thin, or the recommendation asserted without a falsifier. |
| Developing | Single runs, or conditions missing, or throughput and latency treated as the same measurement. |
| Limited | No measurements, or figures inconsistent with the described setup. |

### B2 · Statelessness, demonstrated and explained (10)
The Part 3 evidence and the account of it. Full marks need all three:
- **Why the document and the job behave differently.** The answer is where the bytes live,
  not what kind of data they are. A student who says "documents are files and jobs are
  records" has described, not explained.
- **What the duplicate-submission result means operationally** — that the user sees success,
  the operator sees nothing, and silence is the problem.
- **What the local test does not reproduce.** No network, no independent failure, no
  concurrent-write semantics. A student who reads the test's own docstring and then adds
  something to the list is doing the right thing.

### B3 · Cold start (6)
The measurement, the ordered list of what the platform is doing during it, and two changes
that would make it worse plus one that would make it better. Full marks connect the
`--min-instances=1` cost figure to a statement about users rather than about money.

### B4 · The three-way comparison and its limits (12)
| | Looks like |
|---|---|
| Excellent | One table, conditions on every row, time attributed to named components with measured and inferred parts distinguished. **Four or more real confounds named**, with a view on which matters most. The operational-responsibility table completed, including something that got *harder*. A concrete workload for which the VM is still right. |
| Good | Comparison sound, confounds named generically ("different days") rather than specifically. |
| Developing | A clean-looking table with no caveats, or responsibility answered as a list of platform features. |
| Limited | Numbers without interpretation, or a comparison between rows that are not comparable and are not acknowledged as such. |

> **The confounds paragraph is the highest-signal thing in this submission.** These three
> measurements were taken weeks apart, from different places, with code that changed in
> between. A student who reports a tidy table and no caveats has learned to produce a result,
> not to trust one — and that is precisely what week 14 and the project's evidence section
> will ask of them.

> **Fabricated measurements score zero for the whole lab.** An experiment that failed,
> honestly reported and well reasoned, can still reach Excellent.

## C · Reproducibility, security and resource handling — 15 marks

| | Marks | Looks like |
|---|---|---|
| Excellent | 13–15 | Every role granted is named, scoped and justified in one sentence, and none is broader than needed. The service was never made public, or was made public deliberately with the risk stated and reversed afterwards. `07-verify-clean.sh` output included and clean, **including the Artifact Registry images**. The two identities distinguished correctly. Cost estimate compared with actuals, each line traced to its allowance. |
| Good | 10–12 | Verified clean, but one role is broader than necessary without comment, or the registry cleanup is claimed rather than shown. |
| Developing | 5–9 | Teardown claimed without verification, or images left in the registry, or the runtime service account left behind with bucket access. |
| Limited | 0–4 | Resources left running, or a credential in the submission. |

**Automatic zero for this band:**
- A service-account **key JSON** anywhere in the submission or the repository. Nothing in
  this lab needs one, and the lab says so twice.
- An **identity token** pasted into the submission. It is a credential. It expires, which
  makes it feel harmless; treat it as one anyway, and expect the habit to be graded.
- `--min-instances` set above 0 and left that way.

**Not a penalty:** the ~$0.01 of the optional same-day VM comparison, provided it is declared.
Spending a penny deliberately and saying so is the behaviour this course wants.

## D · Communication — 10 marks

Clear, concise, honest. Predictions that were wrong and are owned earn marks here; predictions
quietly edited after the fact are an integrity matter, which is why Part 0 asks for them
unedited. Uncertainty stated as uncertainty earns marks.

---

## Standing rules

- An unsuccessful experiment earns full analysis credit when the evidence is real and the
  reasoning sound.
- **Fabricated evidence earns zero.**
- Screenshots alone are not evidence. The measurement must be reproducible.
- **No marks for spending more** — no larger instance, no second service "for comparison",
  no warm minimum, no raised `--max-instances`. Where two designs meet the requirement, the
  cheaper one is the better answer.
- **Cleanup claimed but not verified earns nothing in band C.**
- AI assistance is permitted and must be disclosed.

## Marking notes

Expected marking time: **25–35 minutes per student**, the longest of any lab so far. Most of
it is band B4, which is prose rather than output.

**Read Part 0 first, before any of the results.** A student whose predictions were wrong and
who explains why has done the more valuable piece of work, and reading the predictions after
the measurements makes it very hard to judge that fairly.

**Then check the roles**, which takes two minutes and is the strongest single signal of
whether the student understood Part 2 or copied it: `gcloud projects get-iam-policy` output
for their service account, in their submission, against the three things the application
actually does.

**After this lab, verify that every student's Artifact Registry is empty.** It is the one
resource in this lab that accrues silently, it is invisible in the Cloud Run console, and
0.5 GiB is about a dozen builds of this image. A student who tore down the service and left
six images has not finished the lab, and finding out in week 12 is too late.

**Expect the Part 3 reproduction to fail for one or two students.** That is a property of the
platform, not of their work. Mark the explanation, not the luck.

Full solutions, the expected role set, and the common-mistake list: private repo,
`lab-solutions/lab-04/`.
