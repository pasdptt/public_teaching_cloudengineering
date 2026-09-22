# Infrastructure as code

Terraform configuration for the course application. Introduced in **Lab 6 (weeks 12–13)**,
and reused by the project in weeks 13–15.

**Status: HCL parses cleanly (verified 2026-09-22 with a parser). `terraform validate` and
`terraform plan` have NOT been run** — no Terraform binary and no project were available
during authoring, so provider schemas and argument names are **reviewed, not verified**.
Expect to correct a field name or two on first use, and report it so this file improves.

---

## The idea

One configuration. Two environments. The difference between them lives in a variable file,
not in a second copy of the code.

```text
infra/
  versions.tf          provider and version pinning
  variables.tf         everything that may differ, declared
  main.tf              the environment: bucket, identity, service
  outputs.tf           what you need after an apply
  envs/dev.tfvars      dev's values
  envs/prod.tfvars     prod's values
```

If you ever find yourself copying `main.tf` to make a prod version, stop. Whatever you change
in the copy is a difference nobody declared — and **an undeclared difference is why "it works
in dev" happens.**

## Using it

```bash
cd infra
cp envs/dev.tfvars.example envs/dev.tfvars     # then set project_id
cp envs/prod.tfvars.example envs/prod.tfvars

terraform init

# dev
terraform plan  -var-file=envs/dev.tfvars -var="image=$IMAGE"
terraform apply -var-file=envs/dev.tfvars -var="image=$IMAGE"

# and to remove it
terraform destroy -var-file=envs/dev.tfvars -var="image=$IMAGE"
```

**Always read the plan.** A plan you skipped is not a safety measure, and the habit of
running `apply` directly is how people destroy things they meant to keep.

## State, and the trap in this setup

Terraform records what it created in a **state file**. That file is how it knows, next time,
what already exists and what changed.

This course keeps state **local**, which is fine for one student on one laptop and wrong for
a team: two people applying against separate local state files will each believe they own the
infrastructure, and neither will be told otherwise. The commented `backend "gcs"` block in
`versions.tf` is the fix; Lab 6 asks you what it would change.

**One local state file also means one environment at a time**, because a second `apply` with
a different tfvars overwrites the first environment's record. Two honest options:

- `terraform workspace new prod` — separate state, same configuration. Enough for this course.
- A separate state prefix per environment in a shared backend. What you would really do.

Lab 6 uses workspaces and asks you to explain the difference.

## What this configuration deliberately does not do

**It does not create a Firestore database.** There is one free Firestore database per
project, and it must be the `(default)` one (R-11). So `dev` and `prod` in a single project
*cannot* have separate databases — they would share one, which means dev can write to prod's
data, which means the environments are not really separate.

That is not a gap in the configuration. It is the honest edge of what "environments in one
project" can mean, and it is the reason real organisations use **a project per environment**.
Lab 6 asks you to explain the difference this makes, and what you would change to get it.

Notice which resources *can* coexist for free and which cannot:

| Resource | Two environments in one project? | Why |
|---|---|---|
| Cloud Run service | **Yes, both free** | No idle cost with `min_instance_count = 0`; the allowance is per billing account and you will not approach it |
| Cloud Storage bucket | **Yes, both free** | Two small buckets sit inside the 5 GB-month allowance |
| Artifact Registry | **Yes, shared** | One repository serves both; the image is built once and promoted |
| **Firestore** | **No** | One free `(default)` database per project |
| **`e2-micro` VM** | **No** | One free instance per month per billing account |

That table is a better lesson about environment design than any diagram: **the free tier is
per-project for some resources and per-account for others, and that determines what you can
separate cheaply.**

## Cost

Both environments together: **~$0.02** per lab run. Everything above sits inside an Always
Free allowance; the only charge is fractions of a cent if anything with an address lingers.

The guard rails are in the code, not in a warning:

- `region` is validated against the three free-tier regions — an apply outside them fails.
- `max_instances` is capped at 10.
- `min_instance_count` is 0, so an idle service costs nothing.
- `environment` accepts only `dev` or `prod`.

`terraform destroy` for **each** environment, then verify independently. State saying a
resource is gone is not the same as it being gone — see `operations/cleanup.md`.

## Secrets

There are none here, deliberately. `project_id` is configuration, not a credential. The
pipeline authenticates with Workload Identity Federation and **no service-account key is ever
created** (R-14).

If the application later needs a real secret, it goes in Secret Manager and is referenced by
name — never a value in a `.tfvars` file, and never in state. **Terraform state contains the
values of everything it manages**, so a secret passed through Terraform is a secret written to
that file in plain text. Lab 6 makes this point with the state file open.
