# Infrastructure as code

**STATUS: not yet authored — scheduled for Stage C.**

This file is a placeholder so the repository structure is visible and reviewable. It is
not content, and it is not a summary of content that exists elsewhere.

Terraform configurations, provider `hashicorp/google` pinned `~> 8.0` (decision D-03,
reference R-03). Introduced in Lab 6 (week 12), but scripted creation and teardown start in
Lab 2 so that the declarative model answers a problem students have already felt.

Teaching objective is the **declarative model, state and drift** — not Terraform syntax.
Configurations are validated locally (`terraform validate`, `terraform plan`) without
provisioning billable resources during authoring.

See `planning/progress.md` for the authoring order and the current next action.
