# Week 12 — Declarative infrastructure and environments

**Quiz 6 this week.** **Lab 6 starts** — it is the last lab, and it spans weeks 12 and 13.

---

## Two ways to describe infrastructure

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
is the same word you met in week 10 for exactly the same reason. "Set the balance to 400" is
idempotent; "add 100" is not. A desired-state description is the infrastructure version of the
first sentence.

**What it costs**, because tutorials do not mention this:

- You must describe **everything**, including the small things you would have done by hand
  without thinking.
- The tool decides what order to do things in, and it is occasionally wrong — which is why
  `infra/main.tf` has an explicit `depends_on` with a paragraph explaining it.
- You now have a **state file**, and you have to look after it.

## State, and why it has to exist

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

## Drift

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

## Environments

An **environment** is a place a version of your system runs. You are about to have two.

The rule is short and the second half is the hard one:

> `dev` and `prod` should differ **only in the ways you chose**, be identical in every other
> way, and run **the same artefact**.

### What may differ

Instance caps. Log levels. Message retention. How aggressively a bucket may be deleted. Each
should be a choice you can defend in one sentence, and each lives in a `.tfvars` file rather
than in a second copy of `main.tf`.

**If you ever copy `main.tf` to make a prod version, stop.** Whatever you change in the copy is
a difference nobody declared, and:

> **An undeclared difference is why "it works in dev" happens.**

### What must not differ

Harder, and worth more marks. Three that matter:

- **The container image.** Same digest, built once, promoted. Rebuild for prod and dev tested
  something prod will never run.
- **The region.** Different regions mean different latency and a different bill, so your dev
  measurements describe a system you are not shipping.
- **The shape of the configuration.** One file, parameterised. The moment there are two files,
  the differences between them are undocumented by construction.

### The compromise in your own configuration

`infra/` gives each environment its own bucket, its own topic, its own subscription, its own
service and its own identities. It does **not** give each one its own Firestore database.

It cannot. There is one free `(default)` Firestore database per project, so dev and prod share
your data. A destructive change you test in dev touches the same records prod is serving.

That is not a bug in the configuration — it is the honest edge of what "two environments in one
project" can mean, and it is why real organisations use **a project per environment**. This
course does not, because a second project inside one billing account does not get a second free
tier. **A cost constraint producing an architectural compromise** is one of the more realistic
things you will meet this term, and Lab 6 asks you to describe it precisely.

## Configuration is not secrets

A project id is configuration. A database password is a secret. The test is not "does it feel
sensitive" but:

> **What happens if this appears in a public repository?**

And then the part people get wrong. You commit a key, notice within a minute, and remove it in
the next commit. Is it gone?

**No.** It is in the history, in every clone, in every fork, and quite possibly in a search
index already. Removing the file changes what `main` looks like and nothing else.

> **The only fix for a committed credential is to rotate it.** The cleanup is cosmetic.

This is why this course has two repositories, and it is the whole reason next week's pipeline
uses federation instead of a key: the best way to avoid leaking a long-lived credential is not
to have one.

## What transfers, and what does not

**Transfers everywhere:** desired state versus steps, the necessity of state, drift and who
arbitrates it, one configuration parameterised per environment, build-once-promote, and the
permanence of a committed secret.

**Does not transfer:** the HCL syntax, the resource type names, workspaces as a mechanism, and
this provider's particular opinions about ordering.

The tool is incidental. Every cloud has one, and the reasoning above is the same in all of
them. Note also that Terraform's licence changed in 2023 and **OpenTofu** is a compatible fork
— `tofu` runs everything in this lab unchanged, and is what `infra/` was validated with. That
a working tool can fork out from under an industry is itself worth noticing.

## This week's work (~180 minutes)

| | |
|---|---|
| Read these notes; prepare for Quiz 6 | 30 min |
| Lab 6 Parts 1–3: read the configuration, bring up `dev`, produce drift, add `prod` | 150 min |

Part 1 is reading, and it is worth the time. Fourteen resources, every one of which you
created by hand in Labs 3–5. Find the two grants Pub/Sub makes on its own behalf — the ones
that cost you an error message and twenty minutes in Lab 5. Here they are four lines, and they
will be right every time.

## Check yourself

1. A script and a Terraform file both create a bucket. What does each one *record*?
2. Run each twice. What happens, and what is the word for the property that differs?
3. Why can Terraform not work without state? Answer with the delete case.
4. Why is `sensitive = true` not protection for a secret?
5. Define drift, give a realistic way it happens, and say who decides which side is right.
6. Name three things that may differ between dev and prod, and three that must not.
7. Why can dev and prod not have separate Firestore databases here, and what would fix it?
8. You committed a key and removed it in the next commit. What is the actual remedy?
9. Two Cloud Run services are free in one project and two `e2-micro` VMs are not. Why? Your
   answer should be about how each allowance is counted.

## Next week

The pipeline. You have a description of an environment and you are still typing `apply` by
hand — next week a merge does it, a broken test stops it, and the whole thing authenticates
without a single long-lived credential existing anywhere.

**Lab 6 is due at the end of week 13, and the project starts.**
