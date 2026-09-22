# Week 12 — Student notes: Declarative infrastructure and environments

**STATUS: not yet authored — scheduled for Stage C.**

These notes will **teach the content**, not list headings or links.

| | |
|---|---|
| This week covers | Imperative vs declarative provisioning; Terraform state and why it exists; drift; **environment management** — one configuration, two variable files, and the difference between what dev and prod are *allowed* to differ in and what must never differ; configuration vs secrets, and why a committed secret is permanent; cost models and estimating before deploying |
| Practical work | Lab 6 first half — complete the Terraform skeleton, bring up `dev`, produce drift deliberately, add `prod` |
| Assessment | Quiz 6 (CLO-5, CLO-6; CLO-7 and CLO-9 through their threads only — never that day's material) |
| Outcomes | CLO-7, CLO-9 |

> **Restructured 2026-09-22 (D-24).** Lab 6 became a two-week lab covering delivery and
> environments together. This week is its first half.

## To be authored

- The problem that motivates this week's abstraction
- The general mechanism, explained in text alongside any diagram
- Tradeoffs, failure modes and constraints
- How the GCP workbench implements it — generic name first, product name second
- What transfers to another provider, and what does not
- A short self-check before the next quiz
