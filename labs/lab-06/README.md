# Lab 6 — Delivery, environments and reproducibility

**Weeks 12–13 · 7.5% of the final grade · Individual submission**

| | |
|---|---|
| **Cloud resources** | Cloud Run × 2 (`dev`, `prod`), Cloud Storage × 2, Artifact Registry × 1, service accounts, a Workload Identity Federation pool |
| **Estimated cost** | **~$0.02.** Everything sits inside Always Free; GitHub Actions is free on public repositories. |
| **Outcomes** | CLO-9 (delivery and environments), CLO-7 (reproduce and remove) |
| **Estimated novice time** | ~2 h guided (2 × 60 min) + ~4.3 h independent across weeks 12–13 |
| **Observed pilot time** | *not yet measured* |

> **Week 13 also starts the project.** This lab's second half is sized at 110 minutes of
> independent work, not the usual 150, for that reason. If you find yourself over, stop and
> say so — the schedule has a recorded remedy and it is not "work longer".

---

## Why this lab exists

For ten weeks your tests have run on every push. You have probably been stopped by a red
check at least once. This lab asks what that machinery is actually for, and then extends it
from "runs the tests" to "puts the tested thing in front of users".

Two ideas, and they are one subject:

- **A pipeline is a sequence of gates.** Each gate is a claim about what cannot get past it.
  A gate you switched off is worse than no gate, because you still believe you have one.
- **An environment is a place a version of your system runs.** `dev` and `prod` should differ
  in the few ways you chose, be identical in every other way, and run **the same artefact**.
  A difference you did not choose is a bug waiting for a bad day.

By the end you will have deployed to two environments from one configuration, promoted a
single built image between them, broken a test on purpose and watched the gate hold, and torn
it all down.

## Before you start

- [ ] Labs 2–5 complete. This lab reuses their components and builds nothing new.
- [ ] CI has been running on your pushes since week 3 (Lab 1 Part 6).
- [ ] Your trial has not expired. Check the date — if it is close, tell the instructor
      **now**, not in week 15.
- [ ] `terraform` installed (`terraform -version`, 1.5 or newer).

---

# Week 12 — Infrastructure and environments

## Part 1 — Read before you run (~30 min)

Read `infra/` in this order: `versions.tf`, `variables.tf`, `main.tf`, then both
`envs/*.tfvars.example`.

**Predict, in writing, before running anything:**

1. `terraform plan` against a project where nothing exists. How many resources will it create,
   and can you name them without running it?
2. You `apply` with `dev.tfvars`, then `apply` again with `prod.tfvars` in the same working
   directory. What happens to the dev resources? (Think about what state is, not about what
   you would like to happen.)
3. `infra/README.md` says this configuration deliberately does not create a Firestore
   database. Why not — and what does that tell you about what "two environments in one
   project" can and cannot mean?

## Part 2 — Bring up `dev` (~60 min)

```bash
cd infra
cp envs/dev.tfvars.example envs/dev.tfvars      # set project_id
terraform init
terraform plan  -var-file=envs/dev.tfvars -var="image=$SOME_IMAGE"
terraform apply -var-file=envs/dev.tfvars -var="image=$SOME_IMAGE"
```

Use an image you already built in Lab 4.

**Checkpoint.** `terraform output service_url`, then `curl $URL/healthz`.

**Read the plan before applying.** Then answer: the plan said *create*. What would it have to
say for you to stop and investigate rather than type yes?

**Now break something on purpose.** In the console, change the deployed service's
`max-instances` by hand. Run `terraform plan` again.

**Record:** what the plan says now. That gap between the world and your configuration is
**drift**, and you have just produced it deliberately. Answer: which is right — the console or
the file? What decides that, and what would happen if two people each believed theirs was?

## Part 3 — Add `prod`, and account for every difference (~60 min)

```bash
terraform workspace new prod
cp envs/prod.tfvars.example envs/prod.tfvars
terraform apply -var-file=envs/prod.tfvars -var="image=$SAME_IMAGE_AS_DEV"
```

Note `$SAME_IMAGE_AS_DEV`. Not a rebuild. The **same** artefact.

**Checkpoint.** Both services respond. `terraform workspace list` shows two.

**Complete the `TODO` in `variables.tf`:** add a variable capturing something that *should*
differ between the environments, and give it different values in each tfvars file.

**Produce a difference table** for your submission:

| Setting | dev | prod | Deliberate? | Why |
|---|---|---|---|---|
| `max_instances` | | | | |
| `processing_delay_ms` | | | | |
| `log_level` | | | | |
| `force_destroy` on the bucket | | | | |
| *your new variable* | | | | |
| **container image** | | | **identical, on purpose** | |

**Then the harder half:** list three things that are deliberately the **same**, and say what
would break if each drifted apart. Full marks in this lab are in that second list. Anyone can
list differences; knowing what must not differ is the actual skill.

**Answer:** you now have two environments in one project, sharing one Firestore database.
Describe concretely what could go wrong, and what you would change to fix it properly.

---

# Week 13 — The delivery pipeline

## Part 4 — Give the pipeline an identity, without a key (~60 min)

Your pipeline needs to deploy, so it needs permissions. The obvious route is to create a
service-account key and paste the JSON into a GitHub secret. **Do not.** Google's own
documentation says such a key "must be treated like a password" and that "by default, these
credentials never expire" (`course/references.md` R-14).

Instead: **Workload Identity Federation.** GitHub mints a short-lived OIDC token asserting
"this is workflow X, in repository Y, on commit Z". Google Cloud is configured to trust that
assertion — for *your* repository specifically — and exchanges it for a short-lived access
token. **No long-lived credential exists anywhere.**

Set up a pool and a provider with an attribute condition restricting it to your repository,
create a deployer service account, and grant it the narrow roles this pipeline needs.
(Detailed commands: the teaching guide and Google's current documentation. Check the docs
rather than copying a blog — this area changes.)

**Checkpoint.** The `auth` step in `deploy.yml` succeeds and the run log shows an
authenticated identity. **No secret containing a key exists in your repository settings.**

**The question to answer properly:** `deploy.yml` is committed to a *public* repository, and
after this part it contains your pool id and your service-account email. **What stops someone
forking it and deploying into your project?** Be specific — name the mechanism.

**Also answer:** the deployer service account needs permission to deploy. List the roles you
granted and justify each. If you used Editor, say so and say what you would use instead —
honesty here scores better than a tidy lie.

## Part 5 — Build once, deploy, and watch a gate hold (~60 min)

Complete the `TODO` blocks in `.github/workflows/deploy.yml`. Then:

1. **Merge to main.** Watch it test, build, push, apply to `dev`, and smoke-test.
2. **Confirm the image tag is the commit sha**, not `latest`.
3. **Break a test on purpose.** Change an assertion in `application/tests/test_processing.py`
   so it fails. Commit. Push.
4. **Watch the gate hold.** The `test` job fails; `deploy` never runs.
5. Fix it. Watch it go green and deploy.
6. **Promote to prod**: run the workflow manually with `environment: prod`.

**Record:** links to (or output from) the red run and the green run, and the image reference
deployed to each environment. **They must be the same image.** If they are not, find out why —
that is a more valuable finding than a clean run.

**Answer these four:**

1. `deploy` declares `needs: test`. Delete that line and describe exactly what becomes
   possible. Why is a removed gate worse than an absent one?
2. Why tag with the commit sha rather than `latest`? Name the specific failure `latest`
   allows that a sha does not.
3. `permissions:` grants `contents: read` and `id-token: write`. Why not just give the
   workflow write access to everything and move on?
4. The smoke test fails the *run*, but the bad revision is already serving traffic. What
   would you add, and what would it cost you? You do not have to build it.

## Part 6 — Cost, teardown, and proof (~40 min) · **graded**

**Estimate before you look.** Using `operations/cost-model.md` §1 and the official pricing
pages, produce an estimate for this lab: every resource, its quantity, the free-tier
allowance that covers it, and what would take you outside it. Then compare against the actual
billing figure and explain the difference.

Answer the question `infra/README.md` raises: **why can two Cloud Run services and two buckets
coexist for free in one project, while two `e2-micro` VMs or two Firestore databases cannot?**
Your answer should be about how each allowance is *counted* — and it is the most portable
piece of cost reasoning in this course.

Then take it all down:

```bash
terraform workspace select prod && terraform destroy -var-file=envs/prod.tfvars -var="image=$IMAGE"
terraform workspace select dev  && terraform destroy -var-file=envs/dev.tfvars  -var="image=$IMAGE"
```

Then verify **independently of Terraform**, using `operations/cleanup.md`. State saying a
thing is gone is a claim by the tool that deleted it, and Artifact Registry images are not in
that state at all — the pipeline pushed them.

**Include the verification output.** Claiming cleanup is not verifying it.

---

## What to submit

`lab06-<your-name>.md`, plus your completed `infra/` and `.github/workflows/deploy.yml`.

1. **Predictions** from Part 1, written first.
2. **Drift** — what the plan said after your console change, and your answer on which is right.
3. **The difference table**, plus three things deliberately the same and what breaks if they
   drift.
4. **Federation** — what stops a fork deploying into your project; the roles you granted and
   why.
5. **The pipeline** — red run, green run, and the image references for both environments.
6. **Your four answers** from Part 5.
7. **Cost estimate vs actual**, and the per-project/per-account allowance answer.
8. **Teardown verification output.**
9. **AI-assistance disclosure.**

## Resource inventory

| Resource | Per environment? | Removed by | Watch |
|---|---|---|---|
| Cloud Run service | yes | `terraform destroy` | — |
| Cloud Storage bucket | yes | `terraform destroy` | `force_destroy` is false in prod, on purpose |
| Runtime service account | yes | `terraform destroy` | — |
| Artifact Registry images | **no — shared** | manual | **Not in Terraform state.** Every pipeline run adds one; the allowance is 0.5 GiB |
| WIF pool and provider | no | manual | No charge, but it is a standing trust relationship |
| Deployer service account | no | manual | Delete it, or its permissions outlive the course |

## Troubleshooting

**`Error: Invalid provider configuration` on init** — check `project_id` in your tfvars.

**The `auth` step fails with a permission or audience error** — the attribute condition on
your provider does not match your repository, or the deployer service account is not bound to
the pool's principal. Re-read the condition character by character; it is almost always a
typo in the repository name.

**`terraform apply` says it will destroy resources you did not expect** — you are in the wrong
workspace. `terraform workspace show`. **Read every plan.** This is the failure mode the
habit exists to prevent.

**Cloud Run deploys but returns 403** — the `run.invoker` binding. Part 3 of Lab 6's
`main.tf` makes it public; check it applied.

**Bucket destroy fails: "bucket is not empty"** — `force_destroy` is false in prod, on
purpose. Empty it deliberately, and notice the guard did its job.

**The pipeline pushed an image but Terraform deployed an older one** — the image variable is
not reaching `apply`. Check the `-var="image=..."` line and that the build step's output is
being read.

**Anything else** — class issue log first.
