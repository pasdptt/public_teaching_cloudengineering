---
marp: true
theme: cloudcourse
paginate: true
footer: 'Week 13 · Infrastructure as code, environments, pipelines'
---

<!--
Deck for week 13. Derived from weeks/week-13/teaching-guide.md — that file is authoritative
for the teaching; this is what goes on the wall.

Render:  bash course/slides/render.sh 13
-->

<!-- _class: lead -->

# Infrastructure as code, environments, and delivery pipelines

## Week 13

Cloud Computing: Principles and Practice

<!--
TIMING: 180 min total — 75 concepts · 15 quiz · 40 design review · 40 practical · 10 break.
Guide: weeks/week-13/teaching-guide.md — this week carries what were two weeks. Teach the first move of each section; the notes carry the rest.
If you must cut on the day: cut "what a pipeline cannot catch" to a sentence. NEVER cut the design review, and never cut the "what must not differ" half of environments.
Before you start: labs/lab-02/starter/01-create-vm.sh and infra/main.tf open side by side. A state file you can open live. Every TODO in .github/workflows/deploy.yml read. Quiz 6 printed. Tell the room to start `tofu init` during the design review.
-->

---

## The last teaching week

Ten weeks of creating things by hand, and of a pipeline running on every push.

Today both become things you **describe** rather than do — and you check your project's scope before you build it.

**Lab 6 is due at the start of week 14. Week 14 is the final exam.** There is no slack after it.

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">0:00 – 0:20</span>

# Declarative, state, drift

What each approach records

---

## Two files. What is each one?

| `labs/lab-02/starter/01-create-vm.sh` | `infra/main.tf` |
|---|---|
| A list of **steps** | A description of the **result** |
| Records what you **did** | Records what you **want** |

<!--
Put both on screen side by side. Ask what each one IS before showing this table.
Guide: "Open with their own scripts"
-->

---

<!-- _class: ask -->

## Run the script twice. What happens?
## Run the Terraform twice. What happens?

<!--
The script fails, or worse, makes a second thing. Terraform does nothing: the world already matches. That is idempotency — week 11's word, applied to infrastructure. "Set the balance to 400", not "add 100".
Then the honest cost: you must describe everything; the tool's ordering opinions are sometimes wrong; and you now have a state file to look after.
-->

---

<!-- _class: ask -->

## You delete a resource from the file.
## How does Terraform know to destroy something, rather than do nothing?

<!--
It must remember what it made. That memory is the state file.
-->

---

## State: two consequences

1. **Whoever holds the state holds the truth.** Two people with two local state files each believe they own the infrastructure. That is why the `backend "gcs"` block exists in `versions.tf`.
2. **State contains the values of everything it manages** — in plain text.

<!--
Consequence two: do it live. Open a state file and scroll.
-->

---

<!-- _class: punch -->

## A secret that goes through Terraform is a secret written to the state file.

<!--
Marking a variable `sensitive` hides it from console output. It does not remove it from state. Deliver this with the file open — it is the most practically dangerous thing in the week.
-->

---

<!-- _class: ask -->

## Someone changed the service in the console. `plan` now says it will change it back.
## Which is right — the console or the file?

<!--
Drift: the gap between description and world, usually from a 2 a.m. incident fix, not malice. Neither is automatically right: the file is right if you have DECIDED it is authoritative. That is an organisational commitment; the tool only gives you visibility. They produce drift themselves in the practical.
-->

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">0:20 – 0:40</span>

# Environments, and config versus secrets

What may differ, what must not, and who decides

---

<!-- _class: ask -->

## What may differ between dev and prod?

<!--
Easy, and everyone can do it: instance counts, log levels, retention. Collect a few, quickly. Give the next slide most of the time.
-->

---

<!-- _class: ask -->

## Name three things that must be identical between dev and prod — and what breaks if each drifts apart.

<!--
The assessed skill; give it room. Expect to pull the first one out of them.
The container image (or dev tested something prod never runs) · the region (wrong latency, wrong bill) · the shape of the configuration (a copied main.tf with edits = differences nobody declared).
-->

---

<!-- _class: punch -->

## An undeclared difference is why "it works in dev" happens.

---

<!-- _class: cost -->

## The trap in this course's own configuration

| | dev | prod |
|---|---|---|
| Cloud Run service | separate | separate |
| Bucket | separate | separate |
| Topic and subscription | separate | separate |
| **Firestore** | **shared** | **shared** |

One free `(default)` database per project. **A cost constraint producing an architectural compromise.**

<!--
Ask: what does that mean for a student testing a destructive change in dev? The real answer is a project per environment — and a second project brings a second free tier only with a second billing account.
-->

---

## Configuration, or a secret?

A project id is configuration. A password is a secret.

The test is not "is it sensitive?" but **"what happens if this appears in a public repository?"**

---

<!-- _class: ask -->

## You commit a key, notice, and remove it in the next commit.
## Is it gone?

<!--
No. It is in the history, every clone, every fork, possibly a search index within minutes. The only fix is to ROTATE the credential; the cleanup is cosmetic. This course has two repositories for exactly this reason (D-01).
-->

---

<!-- _class: block -->

<span class="min">Break — 10 minutes</span><span class="clock">0:40 – 0:50</span>

# Break

---

<!-- _class: block -->

<span class="min">10 minutes</span><span class="clock">0:50 – 1:00</span>

# Gates, and build once

The pipeline you have had since week 3

---

<!-- _class: ask -->

## Who has been stopped by a red check?
## What did it stop you doing?

<!--
Collect two or three, then define a pipeline backwards from that experience.
-->

---

## A pipeline is a sequence of gates

| Gate | Its claim |
|---|---|
| Tests | the behaviour still holds |
| Build | it produces an artefact |
| Deploy | that artefact reached an environment |
| Smoke test | it answered afterwards |

**Each gate is a claim about what cannot get past it.**

---

<!-- _class: punch -->

## A gate you switched off is worse than no gate, because you still believe you have one.

<!--
Make it concrete: `needs: test` in deploy.yml. Delete that one line and the pipeline still deploys, still goes green, looks the same in the Actions tab — and stops nothing.
-->

---

## Build once, promote

Build for dev, test in dev, **build again** for prod. What could differ?

A base image that moved · a dependency resolved a minute later · a partial layer · a build cache · the clock.

**The source was identical and the artefact was not.**

`:latest` moves, and nothing records which bytes ran where. **A sha tag cannot lie about that.**

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">1:00 – 1:20</span>

# Pipeline identity and federation

Why a key is the wrong answer

---

## The pipeline is a program calling an API

So it needs a principal. The obvious route: a service-account key, pasted into a repository secret.

Google's own documentation (R-14) says such a key "must be treated like a password" — and **"by default, these credentials never expire."**

---

<!-- _class: ask -->

## What does that key mean in practice?

<!--
Make the room supply the list: it is a file, so it can be copied; it does not expire, so a leak in 2026 is a leak in 2029; a GitHub secret is readable by any workflow in the repository, possibly one added in a pull request; rotating means finding every place it was pasted.
-->

---

<!-- _class: punch -->

## You cannot leak a credential you do not have.

---

## Federation, in three sentences

1. GitHub signs a short-lived token asserting **this workflow, in this repository, on this commit**.
2. Google Cloud trusts tokens signed by GitHub — **only when the assertion matches a condition you wrote**.
3. It exchanges that for a short-lived access token. **Nothing long-lived exists anywhere.**

<!--
Resist the API detail. The setup is fiddly; the idea is these three sentences.
-->

---

<!-- _class: ask -->

## `deploy.yml` is public, with your pool id and deployer email in it. Someone forks it.
## What stops them deploying into your project?

<!--
Let them squirm briefly. The attribute condition: trust is bound to your-org/your-repo, and a fork's token asserts a different repository, so the exchange fails. The pool id is configuration — it grants nothing on its own. A key would have been the opposite.
Generalise: OIDC federation is how every CI system should now authenticate to every cloud.
-->

---

<!-- _class: demo -->

## The condition, in the supplied script

```bash
--attribute-condition="assertion.repository == '${GITHUB_REPO}'"
```

From `labs/lab-06/starter/01-bootstrap-pipeline.sh`.

**The most common federation failure is a typo in that repository name.** Read it character by character before you search for anything.

---

<!-- _class: block -->

<span class="min">5 minutes</span><span class="clock">1:20 – 1:25</span>

# What a pipeline cannot catch

A filter, not a guarantee

---

<!-- _class: punch -->

## The smoke test fails the run. The bad revision is already serving traffic.

<!--
The first cut if time is short: say this sentence and point at the notes. Also missed: a test never written; a correct change that is a bad idea; an unmeasured performance regression; a valid, wrong config change; anything about data.
-->

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">1:25 – 1:40</span>

# Quiz 6

Asynchrony, failure, evidence — and two habits

<!--
CLO-5 and CLO-6; CLO-7 and CLO-9 only through the threads they have lived with: cleanup since Lab 2, CI since week 3.
It MUST NOT assess today's Terraform material — a real defect found in an earlier audit. Key in the private repository.
-->

---

<!-- _class: block -->

<span class="min">40 minutes</span><span class="clock">1:40 – 2:20</span>

# Design review

Each project, against the rubric

<!--
Three to four minutes each, strictly timeboxed. Ten projects fit in forty minutes only if you are strict. Ask the room to start `tofu init` now, before the practical — it downloads a provider over one wireless network.
-->

---

## Three questions, and nothing else

1. **What question does your experiment answer?** If it has no measurable answer, fix it now — not in week 15.
2. **What will you reuse, and what will you build?** The delivery path comes from Lab 6 and is **not rebuilt**.
3. **What is the smallest version still worth demonstrating?** Write it down. That is your week 15 fallback.

<!--
The most common intervention by a distance is cutting scope. Say out loud that it is normal. Anyone planning to build a pipeline is over scope (D-28) — tell them immediately.
-->

---

<!-- _class: punch -->

## Having named the smallest version now is what makes falling back to it a decision rather than a failure.

---

<!-- _class: block -->

<span class="min">40 minutes</span><span class="clock">2:20 – 3:00</span>

# Practical

Lab 6 Parts 1–3 in the room

---

## Before you type anything

- **`terraform` is no longer in Homebrew.** `brew install opentofu`, and `tofu` is a drop-in for everything in this lab — it is what the configuration was validated with.
- **Part 1 is reading.** Fourteen resources, each one you built by hand in Labs 3–5. Find the two Pub/Sub service-agent grants: in Lab 5 they cost twenty minutes and an error message.

---

<!-- _class: demo -->

## Part 2 — bring up `dev`

```bash
cd infra
cp envs/dev.tfvars.example envs/dev.tfvars      # set project_id
terraform init
terraform plan  -var-file=envs/dev.tfvars -var="image=$SOME_IMAGE"
terraform apply -var-file=envs/dev.tfvars -var="image=$SOME_IMAGE"
```

Use an image you built in Lab 4. A plain `curl` returns **403** — correct. The invoker `TODO` is the fix.

<!--
`tofu` in place of `terraform` throughout. Watch for the wrong workspace: `terraform workspace show` before every apply.
-->

---

<!-- _class: demo -->

## Produce drift before you leave

1. In the console, change the service's **`max-instances`** by hand.
2. Run `terraform plan` again.
3. Record what it says — and decide which side is right.

Two minutes. The only demonstration of drift you will get.

<!--
Make EVERYONE do this before they leave.
-->

---

<!-- _class: demo -->

## Part 3 — add `prod`, with the same artefact

```bash
terraform workspace new prod
cp envs/prod.tfvars.example envs/prod.tfvars
terraform apply -var-file=envs/prod.tfvars -var="image=$SAME_IMAGE_AS_DEV"
```

**Not a rebuild. The same image.** Then the difference table — and the harder list: three things that are deliberately the **same**.

---

## At home — Parts 4–6

- **Part 4:** read `01-bootstrap-pipeline.sh` and its header before running it. It has **not yet been run against a real project**; if a command fails, the error and Google's current documentation decide.
- **Part 5:** build once, deploy, watch a gate hold.
- **Part 6:** teardown, in order. **The state bucket goes last** — and is graded.

---

## This week's work — 180 minutes

| | |
|---|---|
| Read the notes — they carry what the room could not | 30 min |
| Lab 6, in one week | 150 min |

**Lab 6 is due at the start of week 14.**

---

<!-- _class: lead -->

# Next week

**Final exam** — 120 minutes · **peer review** of another project

Lab 6 due at the start of the session

<!--
Point at weeks/week-14/student-notes.md for the exam format and how to prepare. Remind them the peer review runs on their proposal and any evidence collected — it cannot run on memory.
-->
