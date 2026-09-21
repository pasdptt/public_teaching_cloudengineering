# Lab 02 — Compute and networking

**STATUS: not yet authored — scheduled for Stage C.**

Placeholder recording scope and constraints so the lab sequence stays reviewable. It is not
lab content and must not be issued to students.

| | |
|---|---|
| Weeks | 4–5 |
| Task | Deploy the service on a small VM, configure narrow access, trace the network path hop by hop, and explain the identity and responsibility boundary at each one. |
| Outcomes | CLO-3 |
| Weight | 7.5% of the final grade |
| Cloud resources | One `e2-micro` in `us-central1` (Always Free), 10 GB standard disk (free), firewall rule, and an **ephemeral** external IP. **Estimated cost ≈ $0.04** — the IP is the only charged item in the entire course. First lab with a graded teardown verification. |

**Design note.** Scripted creation and teardown start here — the script students maintain by hand is what makes Terraform in Lab 6 feel like an answer rather than a new tool.

## Time envelope

2 × 60 min guided + 2 × ~150 min independent = **~7 hours total**

An estimate that exceeds this envelope means the lab is cut down, not shipped with a
warning (`course/workload-budget.md`).

## Required sections when authored

Every lab in this course contains all of these:

- Learning outcomes, prerequisites, and an estimated **novice** completion time — kept
  separate from any observed pilot timing, which stays empty until a pilot happens
- A conceptual diagram **and** a text explanation of the same thing
- A short prediction question answered **before** implementing
- Starter code with student-authored sections clearly marked (`TODO`, never a commented-out
  solution)
- Required steps with checkpoints and the observation expected at each one
- At least one experiment that changes a variable and requires interpretation
- Evidence to submit: commands and configuration, measurements with conditions and units,
  and concise reasoning
- A rubric using the standard bands: 35% implementation · 40% explanation and evidence ·
  15% reproducibility, security and resource handling · 10% communication
- Troubleshooting guidance for the errors this lab actually produces
- Resource inventory, preflight checks, cleanup steps, and **cleanup verification**
- A separate instructor solution and teaching notes → private repository,
  `../cloudengineering-instructor/lab-solutions/lab-02/`

## Lab cycle

> predict → implement → measure → explain

A prediction that turned out wrong, and is explained, is worth more than a right one that
is not. An experiment that failed still earns full analysis credit when the evidence is
real and the reasoning is sound. Fabricated measurements earn zero.
