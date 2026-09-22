# Infrastructure as code

Terraform configuration for the course application. Introduced in **Lab 6 (weeks 12–13)**,
and reused by the project in weeks 13–15.

**Status: validated, not applied (2026-09-22).**

- `validate` **passes** against the real `hashicorp/google` provider schema, which resolved
  to **8.3.0** under the `~> 8.0` constraint. Every resource type, argument name and type in
  this directory is therefore checked, not merely reviewed.
- Both example variable files **pass every `validation` block**, and deliberately bad values
  were confirmed to be rejected.
- `fmt` is clean.
- **`plan` and `apply` have NOT been run.** They need a project and credentials, and neither
  was available. Nothing here has ever created a resource.

One caveat, stated precisely because it matters: the validation above was run with
**OpenTofu 1.12.6**, not Terraform. Homebrew no longer distributes Terraform, and OpenTofu is
the drop-in this course already names as its fallback (D-03). The two accept the same HCL and
the same provider, so the check is meaningful — but if you hit a difference on first use, that
is where to look, and please report it.

Validation found one genuine bug that review had missed: a dependency cycle between the
subscription and one of its IAM grants. See the comment on `depends_on` in `main.tf`; the
explanation is now part of the teaching material rather than a defect.

---

## The idea

One configuration. Two environments. The difference between them lives in a variable file,
not in a second copy of the code.

```text
infra/
  versions.tf          provider and version pinning
  variables.tf         everything that may differ, declared
  main.tf              the environment: bucket, queue, identities, service
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

## What is in here, and where it came from

Every resource in `main.tf` is something you created by hand in an earlier lab:

| From | Resource |
|---|---|
| Lab 3 | the documents bucket; the Firestore grant |
| Lab 4 | the Cloud Run service; the runtime service account and its bucket binding |
| Lab 5 | the topic, the dead-letter topic, the push subscription, the push service account, and **the two grants Pub/Sub makes on its own behalf** — the ones you had to discover from an error message |

Nothing here is new. That is the point of the lab: eight weeks of `gcloud` commands, each of
which you could forget, said once in a file that can be reviewed, diffed and deleted.

The two Pub/Sub service-agent grants are worth finding in the file specifically. In Lab 5 they
were the step that defeated half the room. Here they are four lines, and they will be correct
every time.

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
| Pub/Sub topic + subscription | **Yes, both free** | The allowance is message volume, and two idle environments move almost none |
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
- `message_retention_seconds` is bounded at 600–86,400, so a forgotten subscription cannot
  hoard billable messages for a week. Same bound the Lab 5 scripts enforced, now enforced by
  the configuration rather than by a script somebody has to remember to run.
- The service is **private**: the only `run.invoker` binding is for the push identity, on
  that one service. There is no `allUsers` anywhere in this directory.

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
