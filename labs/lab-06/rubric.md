# Lab 6 — Rubric

**7.5% of the final grade.** Same four bands as every lab. This lab is the primary evidence
for **CLO-9** and a second piece for **CLO-7**.

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
| Excellent | 31–35 | Both environments applied from one configuration and separate tfvars. The `variables.tf` TODO completed with a defensible variable. Pipeline authenticates by **Workload Identity Federation with no key anywhere**, builds a sha-tagged image, applies to `dev` on merge and promotes to `prod` on dispatch. The red run and green run are both evidenced. Both environments destroyed and verified. |
| Good | 24–30 | Both environments and a working pipeline; one TODO left, or promotion done by hand rather than through the workflow. |
| Developing | 14–23 | One environment, or a pipeline that deploys without the test gate wired, or an image rebuilt per environment. |
| Limited | 0–13 | Terraform does not apply, or no pipeline runs. |

**Capped at Developing, whatever else is right:** a service-account **key** used for pipeline
authentication. Part 4 gives the reason, Google's own documentation is quoted, and the
alternative is the taught path. If a student could not get federation working and fell back to
a key, they must say so explicitly and explain the risk — that honesty keeps them at
Developing rather than Limited.

## B · Explanation and evidence — 40 marks

### B1 · Predictions (4)
Four answers, written before running. Question 2 (what happens when you apply prod over dev in
one working directory) is the one that separates students who understand state from students
who have used Terraform. Question 4 — why one dead-letter grant can be named in `depends_on`
and the other cannot — is the one that separates students who read `main.tf` from students who
skimmed it; "it would be a cycle" earns the mark only with the direction of the dependency
stated.

### B2 · Drift (6)
What the plan said after the manual console change, and a real answer to "which is right?".
Full marks need the consequence: two people each believing their own view is authoritative,
and what that does to a deployment.

### B3 · Environment differences (12) — **the heart of the lab**
| | Looks like |
|---|---|
| Excellent | Difference table complete, every difference justified rather than described. **Three things deliberately the same, each with a concrete account of what breaks if it drifts** — and the image is one of them. The shared-Firestore answer identifies a real failure (dev writing prod data) and reaches project-per-environment as the fix. |
| Good | Table complete and justified; the "same" list is present but thin. |
| Developing | Differences listed without justification, or the "same" list is missing. |
| Limited | Describes what the tfvars files contain. |

> A student who lists differences has read the files. A student who can say what must **not**
> differ, and why, has understood what an environment is for. Mark accordingly.

### B4 · Federation and pipeline identity (8)
The fork question answered **specifically** — the attribute condition binding the pool to
their repository — not "because it's secure". Roles justified. Full marks acknowledge that
the pool id and service-account email are *configuration*, safe to publish, while a key would
not be, and can say why that distinction holds.

### B5 · The four pipeline questions (10)
| | Looks like |
|---|---|
| Excellent | `needs: test` removed → untested code deploys, plus the point that a removed gate is worse than an absent one because the belief survives. `latest` → names a specific failure (a mutable tag means the thing you tested and the thing you shipped can differ, and you cannot tell afterwards). Permissions → blast radius of a compromised workflow on a public repository. Smoke test → recognises the bad revision is already live and proposes something concrete with its cost stated. |
| Good | All four answered correctly, one at the level of vocabulary rather than mechanism. |
| Developing | Two or three answered, or answers that restate the question. |
| Limited | Generic statements about CI/CD being good practice. |

## C · Reproducibility, security and resource handling — 15 marks

| | Marks | Looks like |
|---|---|---|
| Excellent | 13–15 | Cost estimated **before** deploying, compared with actuals, difference explained. The per-project vs per-account allowance question answered correctly. Both environments destroyed and verified **independently of Terraform** — including Artifact Registry images, which state does not track, and **both push subscriptions**, which retain billable messages. No key, no secret, no tfvars committed. |
| Good | 10–12 | Verified clean; estimate present but not compared, or registry images overlooked. |
| Developing | 5–9 | Teardown claimed without verification, or one environment left running. |
| Limited | 0–4 | Resources still running, or a credential in the repository. |

**Automatic zero for this band:** a service-account key JSON, a populated `.tfvars`, or a
`terraform.tfstate` committed to the repository. All three are gitignored; committing one
means the ignore rules were actively worked around. A committed key must be **rotated**, not
deleted.

## D · Communication — 10 marks

Clear and honest. This lab produces a lot of output; the submission should be short and
selective. Choosing which three lines of a plan to quote is itself a communication skill.

---

## Standing rules

- An unsuccessful experiment earns full analysis credit when the evidence is real and the
  reasoning sound.
- **Fabricated evidence earns zero.**
- **No marks for spending more.** Two environments is the requirement; a third is not extra
  credit, and it will not fit in the free tier.
- **Cleanup claimed but not verified earns nothing in band C.**
- AI assistance is permitted and must be disclosed. Note that a generated pipeline the student
  cannot explain scores badly here by construction — band B is 40 marks and band A is 35.

## Marking notes

Expected marking time: **25–35 minutes per student**, the longest of any lab. Bands A and C
are mechanical if the student linked their runs.

Read **B3's "deliberately the same" list first.** It is the fastest signal of whether they
understood the lab, and it predicts the quality of their project's deployment section better
than anything else they submit.

Check Artifact Registry usage across the class after this lab. Every pipeline run pushes an
image, the free allowance is 0.5 GiB, and the cleanup TODO is the one most likely to be
skipped.
