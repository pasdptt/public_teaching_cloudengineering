# Lab 6 — Delivery, environments and reproducibility

**Weeks 12–13 · 7.5% of the final grade · Individual submission**

| | |
|---|---|
| **Cloud resources** | Per environment: Cloud Run, a bucket, a topic, a dead-letter topic, a push subscription and two service accounts — × 2 for `dev` and `prod`. Shared: Artifact Registry, a Workload Identity Federation pool, a deployer account |
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
- [ ] `terraform` installed (`terraform -version`, 1.5 or newer). **OpenTofu works too** —
      `tofu` is a drop-in for everything this lab does, and is what the configuration was
      validated with. Use either; say which in your submission.

---

# Week 12 — Infrastructure and environments

## Part 1 — Read before you run (~30 min)

Read `infra/` in this order: `versions.tf`, `variables.tf`, `main.tf`, then both
`envs/*.tfvars.example`.

Every resource in `main.tf` is one you created by hand in Labs 3, 4 or 5. **Find each of
them**, and find in particular the two grants Pub/Sub makes on its own behalf — the ones that
cost you twenty minutes and an error message in Lab 5. They are four lines here.

**Predict, in writing, before running anything:**

1. `terraform plan` against a project where nothing exists. How many resources will it create,
   and can you name them without running it? (There are fourteen, plus one `data` block that
   creates nothing — work out why it does not appear in the count. Getting the number wrong
   is fine; not being able to name most of them means read the file again.)
2. You `apply` with `dev.tfvars`, then `apply` again with `prod.tfvars` in the same working
   directory. What happens to the dev resources? (Think about what state is, not about what
   you would like to happen.)
3. `infra/README.md` says this configuration deliberately does not create a Firestore
   database. Why not — and what does that tell you about what "two environments in one
   project" can and cannot mean?
4. The subscription carries an explicit `depends_on`, naming **one** of the two dead-letter
   grants. Read the comment, then answer in your own words why the other one cannot be listed
   there, and why that is correct rather than a limitation.

## Part 2 — Bring up `dev` (~60 min)

```bash
cd infra
cp envs/dev.tfvars.example envs/dev.tfvars      # set project_id
terraform init
terraform plan  -var-file=envs/dev.tfvars -var="image=$SOME_IMAGE"
terraform apply -var-file=envs/dev.tfvars -var="image=$SOME_IMAGE"
```

Use an image you already built in Lab 4.

**Checkpoint.** `terraform output service_url`, then:

```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$(terraform output -raw service_url)/healthz"
```

**The token is not optional.** This service is private, exactly as in Labs 4 and 5 — there is
no `allUsers` binding anywhere in `infra/`. Completing the second `TODO` in `main.tf` is what
lets you and your pipeline in, and the plain `curl` without a token should return 403 until
then.

**Then submit a job and watch it complete**, which exercises the whole graph at once: the
service publishes to the topic, the subscription pushes back to the service, and the job
reaches `succeeded`. If that works, Terraform has just reproduced three labs' worth of
clicking in about ninety seconds.

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
| `message_retention_seconds` | | | | |
| `ack_deadline_seconds` | | | | |
| `max_delivery_attempts` | | | | |
| *your new variable* | | | | |
| **container image** | | | **identical, on purpose** | |

> **One of those three queue differences is defensible, one is arguable, and one is closer to
> a mistake.** Say which is which and why. The `ack_deadline_seconds` row in particular: dev
> uses 10 seconds because it makes redelivery easy to trigger while experimenting. What does
> that do to the fidelity of dev as a test of prod?

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
create a deployer service account, and grant it the roles this pipeline needs. (Detailed
commands: the teaching guide and Google's current documentation. Check the docs rather than
copying a blog — this area changes.)

**Then bootstrap the state bucket**, because the pipeline cannot work without it:

```bash
gcloud storage buckets create "gs://${PROJECT_ID}-tfstate" \
  --project="$PROJECT_ID" --location=US-CENTRAL1 \
  --uniform-bucket-level-access --public-access-prevention
gcloud storage buckets update "gs://${PROJECT_ID}-tfstate" --versioning
```

Then uncomment the `backend "gcs"` block in `infra/versions.tf` and migrate what you already
have:

```bash
cd infra
terraform init -migrate-state \
  -backend-config="bucket=${PROJECT_ID}-tfstate" -backend-config="prefix=docapp"
```

**Three things to answer about this**, and the first is the one people skip:

1. **Why is the state bucket created by hand rather than by Terraform?** There is a real
   answer, it has a name, and it is not "because we were lazy".
2. Week 12 told you local state was fine for one student on one laptop. **What changed?**
   Name the new actor, and say what it does on every run that you do not.
3. You just turned on object versioning for this bucket, which costs money and which Lab 3
   taught you to be suspicious of. **Why is it right here and wrong there?**

> **Do not skip the migration and start clean.** `-migrate-state` moving your existing dev
> environment into the bucket is the interesting part: the resources do not change, the
> record of them moves, and watching that work is what makes state concrete.

**Checkpoint.** The `auth` step in `deploy.yml` succeeds and the run log shows an
authenticated identity. **No secret containing a key exists in your repository settings.**

**The question to answer properly:** `deploy.yml` is committed to a *public* repository, and
after this part it contains your pool id and your service-account email. **What stops someone
forking it and deploying into your project?** Be specific — name the mechanism.

**Also answer:** the deployer service account needs permission to deploy. List the roles you
granted and justify each. If you used Editor, say so and say what you would use instead —
honesty here scores better than a tidy lie.

**And then the uncomfortable question**, which the bottom of `deploy.yml` sets up. Add up
what this account must be able to do: create service accounts, grant project-level IAM,
administer Cloud Run, own two buckets and a Pub/Sub topology, and write to the registry.

By the end of this lab **the pipeline's identity is close to the most powerful principal in
your project**, and it acts on whatever is on the main branch. That is not a flaw in the
design — it is what "the pipeline deploys the infrastructure" means, and every team doing
this lives with it.

Say what you would do about it. Branch protection is one answer. A separate, plan-only
identity for pull requests is another. "Nothing, and here is why that is acceptable in this
context" is also defensible **if you make the argument**.

## Part 5 — Build once, deploy, and watch a gate hold (~60 min)

Complete the `TODO` blocks in `.github/workflows/deploy.yml`. Then:

There are four `TODO` blocks in the deploy job and they are not all the same size. Two of
them — the backend and the workspace — are bugs that will bite you on the *second* run rather
than the first, which is exactly how this class of mistake behaves in real life. Read the
comments before you run anything.

1. **Merge to main.** Watch it test, build, push, apply to `dev`, and smoke-test.
2. **Merge again**, with a trivial change. If you left either of the first two TODOs
   unfixed, this is the run that fails, and **the failure is the lesson** — record what it
   said before you fix it.
3. **Confirm the image tag is the commit sha**, not `latest`.
4. **Break a test on purpose.** Change an assertion in `application/tests/test_processing.py`
   so it fails. Commit. Push.
5. **Watch the gate hold.** The `test` job fails; `deploy` never runs.
6. Fix it. Watch it go green and deploy.
7. **Promote to prod**: run the workflow manually with `environment: prod`.

**Record:** links to (or output from) the red run and the green run, and the image reference
deployed to each environment. **They must be the same image.** If they are not, find out why —
that is a more valuable finding than a clean run.

**Answer these six:**

1. `deploy` declares `needs: test`. Delete that line and describe exactly what becomes
   possible. Why is a removed gate worse than an absent one?
2. Why tag with the commit sha rather than `latest`? Name the specific failure `latest`
   allows that a sha does not.
3. `permissions:` grants `contents: read` and `id-token: write`. Why not just give the
   workflow write access to everything and move on?
4. The smoke test fails the *run*, but the bad revision is already serving traffic. What
   would you add, and what would it cost you? You do not have to build it.
5. The smoke test carries an identity token with an explicit `--audiences`. Why is that
   needed for the pipeline and not when you `curl` the service from your laptop?
6. **Local state in a pipeline.** Describe what the second run did before you fixed it, and
   why the first run looked fine. This is the general shape of a whole family of bugs —
   name what they have in common.

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

**Then the things Terraform does not know about**, in this order and not another:

| Order | Resource | Why here |
|---|---|---|
| 1 | Both environments (above) | While state still exists to describe them |
| 2 | Artifact Registry images | The pipeline pushed them; they were never in state |
| 3 | Deployer service account, WIF pool and provider | A standing trust relationship and a broad identity |
| 4 | **The state bucket, last** | Delete it earlier and Terraform forgets what it owns while it still owns things |

> **Row 4 is the one to get right, and it is a good final lesson.** The state bucket is not a
> resource of the system; it is the record *of* the system. Destroy the record first and you
> are left doing cleanup by hand, from memory, in a console — which is exactly the condition
> Lab 6 spent two weeks arguing against.

Then verify **independently of Terraform**, using `operations/cleanup.md`. State saying a
thing is gone is a claim by the tool that deleted it, and the registry images and the state
bucket were never in that state at all.

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
5. **The pipeline** — red run, green run, the second-run failure if you had one, and the
   image references for both environments.
6. **Your six answers** from Part 5, plus the three state-bucket answers from Part 4.
7. **Cost estimate vs actual**, and the per-project/per-account allowance answer.
8. **Teardown verification output.**
9. **AI-assistance disclosure.**

## Resource inventory

| Resource | Per environment? | Removed by | Watch |
|---|---|---|---|
| Cloud Run service | yes | `terraform destroy` | — |
| Cloud Storage bucket | yes | `terraform destroy` | `force_destroy` is false in prod, on purpose |
| Topic + dead-letter topic | yes | `terraform destroy` | — |
| **Push subscription** | yes | `terraform destroy` | **Retains messages and bills for them.** Two of them now |
| Runtime service account | yes | `terraform destroy` | — |
| Push service account | yes | `terraform destroy` | Two identities per environment, four in total |
| Artifact Registry images | **no — shared** | manual | **Not in Terraform state.** Every pipeline run adds one; the allowance is 0.5 GiB |
| WIF pool and provider | no | manual | No charge, but it is a standing trust relationship |
| Deployer service account | no | manual | Delete it, or its permissions outlive the course — and they are broad |
| **Terraform state bucket** | **no — shared** | manual, **last** | Delete it before the environments and Terraform forgets what it owns. Versioning is on, so check for old versions |

## Troubleshooting

**`Error: Invalid provider configuration` on init** — check `project_id` in your tfvars.

**The `auth` step fails with a permission or audience error** — the attribute condition on
your provider does not match your repository, or the deployer service account is not bound to
the pool's principal. Re-read the condition character by character; it is almost always a
typo in the repository name.

**`terraform apply` says it will destroy resources you did not expect** — you are in the wrong
workspace. `terraform workspace show`. **Read every plan.** This is the failure mode the
habit exists to prevent.

**Cloud Run returns 403 when you curl it** — correct, until you complete the invoker `TODO`
in `main.tf`. The service is private by design. Carry an identity token, as in Labs 4 and 5.

**Jobs stay `pending` after an apply** — the push path. Check `terraform output
subscription_name` exists, then check the subscription's push endpoint ends in
`/tasks/process`. If the endpoint is right, it is the invoker binding for the push account —
which Terraform does create, so look for an apply that partially failed.

**`Error: Cycle:` on plan** — you have added a `depends_on` that points at something which
depends back on the resource declaring it. Part 1's fourth prediction is about exactly this;
the existing `depends_on` in `main.tf` shows the shape of the fix.

**Bucket destroy fails: "bucket is not empty"** — `force_destroy` is false in prod, on
purpose. Empty it deliberately, and notice the guard did its job.

**The pipeline pushed an image but Terraform deployed an older one** — the image variable is
not reaching `apply`. Check the `-var="image=..."` line and that the build step's output is
being read.

**Anything else** — class issue log first.
