# Week 13 — Student notes: Delivery pipelines

**STATUS: not yet authored — scheduled for Stage C.**

These notes will **teach the content**, not list headings or links.

| | |
|---|---|
| This week covers | What a pipeline is for — each stage as a **gate**, and what each gate protects against; build once and promote the same artefact; why a pipeline needs an identity and why that identity must not be a long-lived key; **Workload Identity Federation** and OIDC federation as the pattern it belongs to; what a pipeline cannot catch |
| Practical work | Lab 6 second half — keyless authentication, build once, deploy to `dev` on merge, promote to `prod`, break a test and watch the gate hold, then tear down. **Project implementation begins, with an instructor design review.** |
| Assessment | — (Lab 6 due) |
| Outcomes | CLO-9, CLO-7, CLO-8 |

> **Restructured 2026-09-22 (D-24).** This week was previously an architecture-synthesis
> lecture; that content moved to week 14. It now carries the second half of Lab 6 **and** the
> start of the project, which makes it the second-tightest week in the course — see
> `course/workload-budget.md`.

## To be authored

- The problem that motivates this week's abstraction
- The general mechanism, explained in text alongside any diagram
- Tradeoffs, failure modes and constraints
- How the GCP workbench implements it — generic name first, product name second
- What transfers to another provider, and what does not
- A short self-check before the next quiz
