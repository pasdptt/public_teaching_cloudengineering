# Lab 03 — State and storage

**STATUS: not yet authored — scheduled for Stage C.**

Placeholder recording scope and constraints so the lab sequence stays reviewable. It is not
lab content and must not be issued to students.

| | |
|---|---|
| Weeks | 6–7 |
| Task | Move stored artefacts out of the instance into object storage, then externalise application state to one managed data service and justify the design in a decision record. |
| Outcomes | CLO-4, CLO-5 |
| Weight | 7.5% of the final grade |
| Cloud resources | Cloud Storage (`us-central1`) plus **Firestore**, the project's single free `(default)` database. **Estimated cost: $0.00** — both sit inside Always Free allowances. |

**Design note.** The data service is **not yet chosen** (D-14 / Q-03). It is decided by trial compatibility and idle-cost behaviour, not by which is most interesting to teach.

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
  `../cloudengineering-instructor/lab-solutions/lab-03/`

## Lab cycle

> predict → implement → measure → explain

A prediction that turned out wrong, and is explained, is worth more than a right one that
is not. An experiment that failed still earns full analysis credit when the evidence is
real and the reasoning is sound. Fabricated measurements earn zero.
