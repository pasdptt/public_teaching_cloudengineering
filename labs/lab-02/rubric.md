# Lab 2 — Rubric

**7.5% of the final grade.** Same four bands as every lab in this course.

| Band | Share |
|---|---|
| A. Working implementation | **35** |
| B. Conceptual explanation and experimental evidence | **40** |
| C. Reproducibility, security and resource handling | **15** |
| D. Communication | **10** |

**This is the first lab where band C is about money.** Cleanup that is claimed but not
verified scores zero in that band, not partial credit.

---

## A · Working implementation — 35 marks

| | Marks | Looks like |
|---|---|---|
| Excellent | 31–35 | All five starter scripts completed and working. The service is reachable from the student's laptop through a **deliberately scoped** firewall rule. A dedicated service account with `roles/logging.logWriter` is attached and the application still runs. `06-verify-clean.sh` has all three survivor checks implemented and passes. |
| Good | 24–30 | Everything works; one `TODO` left at its default or a survivor check missing. |
| Developing | 14–23 | The service was reachable at some point, but the firewall was left at `0.0.0.0/0` with no justification, or the default service account was never replaced. |
| Limited | 0–13 | Never reachable, or the work cannot be reproduced from what was submitted. |

Using a **static** IP, or leaving the VM stopped rather than deleted, caps this band at Good
and must be discussed in band B. It is not a disaster — it is a decision, and the lab is
about knowing you made it.

## B · Explanation and evidence — 40 marks

### B1 · Predictions from Part 2, written first (5)
Three answers with reasons. Being wrong costs nothing; not committing, or editing after the
fact, costs the band.

### B2 · Reachability and the two boundaries (10)
| | Looks like |
|---|---|
| Excellent | Distinguishes **hung** from **refused** and correctly infers where the packet died in each case. Explains `DOCAPP_HOST=0.0.0.0` and the firewall rule as controlling *different* boundaries — what the process accepts versus what the network delivers — and why removing either breaks reachability for different reasons. |
| Good | Correct on both, but explained by naming the settings rather than the boundaries. |
| Developing | Treats the two as interchangeable, or reports "it didn't work" without distinguishing the failure modes. |
| Limited | No account of what was observed. |

### B3 · Path trace and identity (10)
Every hop, with the permitting rule **and** the acting identity. Full marks require engaging
with the metadata-service observation: no credential was placed on that machine, yet code
there has an identity and can obtain a token. A student who notices what that implies for
anyone else able to run code on the instance has understood the thing this part is for.

### B4 · Least privilege (5)
The three Part 4 answers. Full marks need the attacker scenario to be **concrete** — what
Editor on the project would actually have allowed — rather than "they could do bad things".

### B5 · The experiment (10)
| | Looks like |
|---|---|
| Excellent | Table with conditions, three runs per setting, variation acknowledged. **Separates the network component from the processing component arithmetically**, and sanity-checks it against the physical distance. Answers the `us-central1` trade-off with their own numbers and distinguishes what is right for this course from what would be right for a real service. |
| Good | Data correct, decomposition present, trade-off answer thin. |
| Developing | Single run, or reports total latency without separating out the delay they configured. |
| Limited | No measurements, or numbers inconsistent with the setup described. |

> **Fabricated measurements score zero for the whole lab** and are an academic-integrity
> matter. An experiment that failed, reported honestly with sound reasoning about why, can
> still reach Excellent.

## C · Reproducibility, security and resource handling — 15 marks

Now with real consequences.

| | Marks | Looks like |
|---|---|---|
| Excellent | 13–15 | `06-verify-clean.sh` output included and **clean**, with all three survivor checks implemented. Cost estimated **before** deploying and compared against the actual billing figure, with any difference explained. Firewall scoped and justified. No service-account key was ever created. Nothing resembling a credential or a personal path in the submission. |
| Good | 10–12 | Verified clean; estimate present but not compared with actuals, or the firewall justification is thin. |
| Developing | 5–9 | Teardown **claimed** but the verification output is missing or incomplete. |
| Limited | 0–4 | Resources left running, or a credential in the submission. |

**Automatic zero for this band:** a downloaded service-account key JSON appearing anywhere in
the submission or repository. Nothing in this lab requires one, `04-service-account.sh` says
so explicitly, and a committed key is permanent — it must be rotated, not deleted.

## D · Communication — 10 marks

Clear, concise, honest. A reader can reproduce the work from the submission alone.
Uncertainty stated as uncertainty earns marks here rather than losing them.

---

## Standing rules

- An unsuccessful experiment earns full analysis credit when the evidence is real and the
  reasoning sound.
- **Fabricated evidence earns zero.**
- Screenshots alone are not evidence.
- **No marks for spending more** — not a bigger machine type, not a second VM, not a region
  outside the free tier. Where two designs meet the requirement, the cheaper one is better
  and should say so.
- **Cleanup claimed but not verified earns nothing in band C.**
- AI assistance is permitted and must be disclosed.

## Marking notes

Expected marking time: **20–30 minutes per student**. Band A is largely mechanical — read
their scripts, look at the verification output. Spend the time on B2, B3 and B5.

Highest-signal thing to read: **B2's hung-versus-refused distinction.** A student who has that
can debug a cloud network; one who has not will struggle in every remaining lab, and it is
cheap to fix now.

Before marking, check the class billing figures. Any student over $1 for this lab has left
something running — usually a reserved static address or a second VM — and that is a
conversation to have immediately, not at the end of term.
