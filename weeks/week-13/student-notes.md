# Week 13 — Infrastructure as code, environments and delivery pipelines

**Quiz 6 this week.** **Lab 6** — the last lab, and a one-week lab — **is due at the start of
week 14.** The **project design review** is in the session.

This is the last teaching week, and it covers what used to take two. The session can only
give each idea its first pass; **these notes carry the whole argument**, which is why this
week's reading time is 30 minutes rather than 20. Read them before the session if you can.

Week 14 is the **final exam**. There is no slack after Lab 6's deadline, so do not plan on
finishing it in week 14.

---

## Part A — Declarative infrastructure and environments

### Two ways to describe infrastructure

Open `labs/lab-02/starter/01-create-vm.sh`. You wrote something like it eight weeks ago, and
you have been maintaining scripts like it ever since. It is a list of **steps**: create this,
then that, then grant this.

Now open `infra/main.tf`. It is a **description of a result**: there is a bucket with these
properties, a service running this image, an identity with these permissions.

The difference is not syntax. It is what each one records.

| | Imperative (a script) | Declarative (Terraform) |
|---|---|---|
| Records | what you did | what you want |
| Run it twice | fails, or makes a second one | does nothing — the world already matches |
| To change something | write a new script that changes it | edit the description and re-apply |
| To remove it | remember everything you made | delete the description |
| Answer to "what exists?" | read every script and hope | read one file |

**Run it twice** is the row that matters. A declarative description is **idempotent**, and that
is the same word you met in week 11 for exactly the same reason. "Set the balance to 400" is
idempotent; "add 100" is not. A desired-state description is the infrastructure version of the
first sentence.

**What it costs**, because tutorials do not mention this:

- You must describe **everything**, including the small things you would have done by hand
  without thinking.
- The tool decides what order to do things in, and it is occasionally wrong — which is why
  `infra/main.tf` has an explicit `depends_on` with a paragraph explaining it.
- You now have a **state file**, and you have to look after it.

### State, and why it has to exist

Here is the question that forces it. Terraform's job is to make the world match the file. You
delete a resource from the file and run `apply`. How does it know to *destroy* something,
rather than to do nothing?

It cannot, unless it remembers what it made. That memory is the **state file**: a JSON record
of every resource under management and its attributes.

Two consequences follow, and both will bite somebody.

**Whoever holds the state holds the truth.** Two people with two local state files each
believe they own the infrastructure, and nothing tells either of them otherwise. Real teams
keep state in a shared backend with locking — the commented-out `backend "gcs"` block in
`versions.tf` is that fix, left visible on purpose.

**State contains values, not just names.** Every attribute of every resource, in plain text.
So:

> **A secret that passes through Terraform is a secret written to the state file.** Marking a
> variable `sensitive` hides it from console output. It does not remove it from state.

This is why `infra/` contains no secrets at all, and why a real secret would live in Secret
Manager and be referenced by name.

### Drift

**Drift** is the gap between your description and the world.

It appears the moment somebody changes something outside the tool. Usually not carelessly — an
incident at 2 a.m. and a console is the normal story. The change is real, it fixed something,
and now the file is wrong.

In Lab 6 you will produce drift deliberately: change your service's `max-instances` in the
console, then run `terraform plan`. The plan will offer to change it back.

**Which is right?** Not a trick question, and the answer is not "the file":

> Neither is right by default. The file is authoritative **if your team has decided it is**,
> and that is an organisational commitment rather than a property of the tool.

What Terraform gives you is **visibility** of the disagreement. What it cannot give you is an
answer about who was right, and the case where two people each believe theirs is the truth is
not a Terraform problem at all.

### Environments

An **environment** is a place a version of your system runs. You are about to have two.

The rule is short and the second half is the hard one:

> `dev` and `prod` should differ **only in the ways you chose**, be identical in every other
> way, and run **the same artefact**.

#### What may differ

Instance caps. Log levels. Message retention. How aggressively a bucket may be deleted. Each
should be a choice you can defend in one sentence, and each lives in a `.tfvars` file rather
than in a second copy of `main.tf`.

**If you ever copy `main.tf` to make a prod version, stop.** Whatever you change in the copy is
a difference nobody declared, and:

> **An undeclared difference is why "it works in dev" happens.**

#### What must not differ

Harder, and worth more marks. Three that matter:

- **The container image.** Same digest, built once, promoted. Rebuild for prod and dev tested
  something prod will never run.
- **The region.** Different regions mean different latency and a different bill, so your dev
  measurements describe a system you are not shipping.
- **The shape of the configuration.** One file, parameterised. The moment there are two files,
  the differences between them are undocumented by construction.

#### The compromise in your own configuration

`infra/` gives each environment its own bucket, its own topic, its own subscription, its own
service and its own identities. It does **not** give each one its own Firestore database.

It cannot. There is one free `(default)` Firestore database per project, so dev and prod share
your data. A destructive change you test in dev touches the same records prod is serving.

That is not a bug in the configuration — it is the honest edge of what "two environments in one
project" can mean, and it is why real organisations use **a project per environment**. This
course does not, because a second project inside one billing account does not get a second free
tier. **A cost constraint producing an architectural compromise** is one of the more realistic
things you will meet this term, and Lab 6 asks you to describe it precisely.

### Configuration is not secrets

A project id is configuration. A database password is a secret. The test is not "does it feel
sensitive" but:

> **What happens if this appears in a public repository?**

And then the part people get wrong. You commit a key, notice within a minute, and remove it in
the next commit. Is it gone?

**No.** It is in the history, in every clone, in every fork, and quite possibly in a search
index already. Removing the file changes what `main` looks like and nothing else.

> **The only fix for a committed credential is to rotate it.** The cleanup is cosmetic.

This is why this course has two repositories, and it is the whole reason Part B's pipeline
uses federation instead of a key: the best way to avoid leaking a long-lived credential is not
to have one.

### What transfers, and what does not

**Transfers everywhere:** desired state versus steps, the necessity of state, drift and who
arbitrates it, one configuration parameterised per environment, build-once-promote, and the
permanence of a committed secret.

**Does not transfer:** the HCL syntax, the resource type names, workspaces as a mechanism, and
this provider's particular opinions about ordering.

The tool is incidental. Every cloud has one, and the reasoning above is the same in all of
them. Note also that Terraform's licence changed in 2023 and **OpenTofu** is a compatible fork
— `tofu` runs everything in this lab unchanged, and is what `infra/` was validated with. That
a working tool can fork out from under an industry is itself worth noticing.

---

## Part B — Delivery pipelines

### You have had a pipeline for ten weeks

Since week 3, every push has run your tests. At some point it went red and stopped you. This
week is about what that machinery actually is, and then extending it from "runs the tests" to
"puts the tested thing in front of users".

Start with the definition, because everything follows from it:

> **A pipeline is a sequence of gates. Each gate is a claim about what cannot get past it.**

Name the claims in yours:

| Stage | The claim it makes |
|---|---|
| Tests | The behaviour these tests describe still holds |
| Build | This source produces an artefact |
| Deploy | *That* artefact reached this environment |
| Smoke test | It answered afterwards |

Every one of those is narrower than it sounds, and knowing how much narrower is the actual
skill. "The tests pass" is not "it works"; it is "the checks somebody wrote, at some point,
still pass".

And the rule that matters most:

> **A gate you switched off is worse than no gate, because you still believe you have one.**

In `deploy.yml` the gate is one line: `needs: test`. Delete it and the pipeline still runs,
still goes green, still looks identical in the Actions tab — and no longer stops anything.
That is the dangerous kind of change.

### Build once, promote

The wrong version is obvious once you see it written down: build an image for dev, test it,
then build another one for prod.

"But the source is identical." Is the *artefact*?

Between the two builds, a base image can move, a dependency can resolve differently, a network
hiccup can produce a partial layer, a cache can be warm or cold. **"The source was identical"
and "the artefact was identical" are two different claims**, and only one of them is what you
tested.

So: build once, tag it, and promote **that** — the same bytes — from dev to prod.

#### Why not `:latest`

A tag is a name, and `latest` is a name that moves. If dev ran `docapp:latest` on Tuesday and
prod runs `docapp:latest` on Thursday, they may be different images and **nothing recorded
which**. When prod breaks, you cannot even establish what is running.

Tag with the commit sha. It cannot move, and it points at a commit you can read.

### The pipeline needs an identity

From the cloud's point of view, your pipeline is a program calling an API. It needs a
principal, like your laptop and your service do.

The obvious route is to create a service-account key and paste the JSON into a repository
secret. **Do not.** Google's own documentation says a key "must be treated like a password"
and that "by default, these credentials never expire" (`course/references.md` R-14).

Work through what that means:

- It is a **file**, so it can be copied, and you will not know when it has been.
- It **does not expire**. A leak in 2026 is still a leak in 2029.
- A repository secret is readable by workflows in that repository — including ones added
  later, by someone else.
- **Rotating it** means finding every place anyone ever pasted it.

Which leads to the design principle behind this whole week:

> **You cannot leak a credential you do not have.**

### Workload Identity Federation

Three sentences:

1. GitHub will sign a short-lived token asserting **this workflow, in this repository, on this
   commit**.
2. Google Cloud is configured to trust tokens signed by GitHub — **but only when the assertion
   matches a condition you wrote**.
3. It exchanges that token for a short-lived access token. Nothing long-lived exists anywhere.

The setup is fiddly. The idea is those three sentences, and the idea is what transfers: **OIDC
federation is how a CI system should authenticate to a cloud**, on every provider. The product
names differ; the pattern does not.

#### The question worth being able to answer

`deploy.yml` lives in a **public** repository and, once you finish it, contains your pool id
and your deployer account's email. Somebody forks it.

**What stops them deploying into your project?**

The **attribute condition**. The trust is bound to your repository by name; a fork's token
asserts a different repository, so the exchange is refused. The pool id and the account email
are *configuration* — they name a trust relationship and grant nothing by themselves.

That is precisely the property a key does not have. A key in a public repository is a
compromise the moment it is pushed.

### Two bugs that wait for the second run

`deploy.yml` has four `TODO` blocks, and two of them behave in a way worth meeting once:

**Local state in a pipeline.** A runner is a fresh machine every time, so local state is empty
on every run. The first deploy works perfectly. The *second* one tries to create everything
again and fails on resources that already exist. Part A said local state was fine for one
student on one laptop; the pipeline is the second actor that paragraph warned about, and it
arrived whether you invited it or not.

**No workspace selection.** Nothing in the file selects a workspace, so `dev` and `prod` would
share one state file — and a prod deploy would read dev's record and plan accordingly.

Both are invisible on a first run and obvious on a second. **A whole family of bugs behaves
like this**, and Lab 6 asks you to name what they have in common. With one week for the lab,
you are given both fixes rather than made to find them by failing — but you predict, in
writing, what the second run would have done before you apply them.

#### The bootstrap problem

The fix is a state bucket in Cloud Storage. It cannot be created by the Terraform
configuration that stores its state there — Terraform needs somewhere to put state before it
can create anything, including that somewhere.

So it is created by hand, once — in Lab 6 by the supplied bootstrap script, which you read
before you run. That is not a workaround. It has a
name — **bootstrapping** — and every team doing this has exactly one step like it.

### What a pipeline cannot catch

Be honest about the limits, because a pipeline invites you to stop thinking:

- A test nobody wrote.
- A change that is correct and a bad idea.
- A performance regression nobody measures.
- A configuration value that is valid and wrong.
- Anything about your data.

And the one your own pipeline demonstrates:

> The smoke test fails the **run**. The bad revision is already serving traffic.

A pipeline is a filter, not a guarantee. What you would add — gradual rollout, automatic
rollback on an error rate — is a real answer with a real cost, and Lab 6 asks you to describe
it rather than build it.

### One more thing, and it should bother you slightly

Add up what the deployer account must be allowed to do for `deploy.yml` to work: create
service accounts, grant project-level IAM, administer Cloud Run, own two buckets and a Pub/Sub
topology, write to the registry.

**By the end of this lab, the pipeline's identity is close to the most powerful principal in
your project — and it acts on whatever is on the main branch.**

That is not a flaw in this design. It is what "the pipeline deploys the infrastructure" means,
and every team doing it lives with the consequence. Branch protection is one answer. A
separate, plan-only identity for pull requests is another. Deciding it is acceptable is also
an answer, if you can say why.

### What transfers, and what does not

**Transfers everywhere:** gates and their claims; build-once-promote; immutable tags; a
pipeline as a principal; OIDC federation instead of long-lived keys; bootstrapping; the limits
of what a pipeline can catch; and the fact that a delivery identity is a high-privilege one.

**Does not transfer:** the YAML schema, the action names, the flag spellings, and this
provider's pool-and-provider vocabulary.

---

## This week's work (~180 minutes)

| | |
|---|---|
| Read these notes; prepare for Quiz 6 | 30 min |
| Lab 6 Parts 1–3: read the configuration, bring up `dev`, produce drift, add `prod` | ~100 min |
| Lab 6 Parts 4–6: the supplied bootstrap, the pipeline, teardown | ~80 min, partly in the session |

The session gives you 40 minutes of Lab 6 with the instructor in the room; use them for Parts
1–3. **Lab 6 is due at the start of week 14**, including verified teardown. Get the state
bucket order right: it is deleted **last**, after everything it describes.

Part 1 is reading, and it is worth the time. Fifteen resources, every one of which you
created by hand in Labs 3–5. Find the two grants Pub/Sub makes on its own behalf — the ones
that cost you an error message and twenty minutes in Lab 5. Here they are four lines, and they
will be right every time.

## Check yourself

1. A script and a Terraform file both create a bucket. What does each one *record*? Run each
   twice: what happens, and what is the word for the property that differs?
2. Why can Terraform not work without state? Answer with the delete case.
3. Define drift, give a realistic way it happens, and say who decides which side is right.
4. Name three things that may differ between dev and prod, and three that must not.
5. Why can dev and prod not have separate Firestore databases here, and what would fix it?
6. You committed a key and removed it in the next commit. What is the actual remedy?
7. Two Cloud Run services are free in one project and two `e2-micro` VMs are not. Why? Your
   answer should be about how each allowance is counted.
8. Define a pipeline in one sentence, then name the claim each of your four stages makes. Why
   is a removed gate worse than an absent one?
9. Name the specific failure `:latest` allows that a sha tag does not.
10. Explain federation in three sentences, then say what the attribute condition protects.
    Your pool id is in a public repository — why is that all right?
11. A pipeline using local state. Why does run one succeed and run two fail? Why can the state
    bucket not be created by the Terraform that uses it?
12. Name two things your pipeline cannot catch, and what you would do about each.

## Next week

**The final exam** — 120 minutes, cumulative, weighted towards weeks 9–13
([`exams/README.md`](../../exams/README.md)). Then a structured **peer review** of another
group's project, for which this week's design review is the preparation. The week 14 notes
are short and are the method for that review. No new material.
