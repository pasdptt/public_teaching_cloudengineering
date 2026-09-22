# Week 13 — Delivery pipelines

**Lab 6 is due at the end of this week.** **The project starts**, with a design review in the
session. No quiz.

This is the second-tightest week in the course. Your independent time is split 110 minutes for
Lab 6 and 50 for starting the project — see `course/workload-budget.md`, which records what
was traded for what.

---

## You have had a pipeline for ten weeks

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

## Build once, promote

The wrong version is obvious once you see it written down: build an image for dev, test it,
then build another one for prod.

"But the source is identical." Is the *artefact*?

Between the two builds, a base image can move, a dependency can resolve differently, a network
hiccup can produce a partial layer, a cache can be warm or cold. **"The source was identical"
and "the artefact was identical" are two different claims**, and only one of them is what you
tested.

So: build once, tag it, and promote **that** — the same bytes — from dev to prod.

### Why not `:latest`

A tag is a name, and `latest` is a name that moves. If dev ran `docapp:latest` on Tuesday and
prod runs `docapp:latest` on Thursday, they may be different images and **nothing recorded
which**. When prod breaks, you cannot even establish what is running.

Tag with the commit sha. It cannot move, and it points at a commit you can read.

## The pipeline needs an identity

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

## Workload Identity Federation

Three sentences:

1. GitHub will sign a short-lived token asserting **this workflow, in this repository, on this
   commit**.
2. Google Cloud is configured to trust tokens signed by GitHub — **but only when the assertion
   matches a condition you wrote**.
3. It exchanges that token for a short-lived access token. Nothing long-lived exists anywhere.

The setup is fiddly. The idea is those three sentences, and the idea is what transfers: **OIDC
federation is how a CI system should authenticate to a cloud**, on every provider. The product
names differ; the pattern does not.

### The question worth being able to answer

`deploy.yml` lives in a **public** repository and, once you finish it, contains your pool id
and your deployer account's email. Somebody forks it.

**What stops them deploying into your project?**

The **attribute condition**. The trust is bound to your repository by name; a fork's token
asserts a different repository, so the exchange is refused. The pool id and the account email
are *configuration* — they name a trust relationship and grant nothing by themselves.

That is precisely the property a key does not have. A key in a public repository is a
compromise the moment it is pushed.

## Two bugs that wait for the second run

`deploy.yml` has four `TODO` blocks, and two of them behave in a way worth meeting once:

**Local state in a pipeline.** A runner is a fresh machine every time, so local state is empty
on every run. The first deploy works perfectly. The *second* one tries to create everything
again and fails on resources that already exist. Week 12 said local state was fine for one
student on one laptop; the pipeline is the second actor that paragraph warned about, and it
arrived whether you invited it or not.

**No workspace selection.** Nothing in the file selects a workspace, so `dev` and `prod` would
share one state file — and a prod deploy would read dev's record and plan accordingly.

Both are invisible on a first run and obvious on a second. **A whole family of bugs behaves
like this**, and Lab 6 asks you to name what they have in common.

### The bootstrap problem

The fix is a state bucket in Cloud Storage. It cannot be created by the Terraform
configuration that stores its state there — Terraform needs somewhere to put state before it
can create anything, including that somewhere.

So you create it by hand, once, with a `gcloud` command. That is not a workaround. It has a
name — **bootstrapping** — and every team doing this has exactly one step like it.

## What a pipeline cannot catch

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

## One more thing, and it should bother you slightly

Add up what the deployer account must be allowed to do for `deploy.yml` to work: create
service accounts, grant project-level IAM, administer Cloud Run, own two buckets and a Pub/Sub
topology, write to the registry.

**By the end of this lab, the pipeline's identity is close to the most powerful principal in
your project — and it acts on whatever is on the main branch.**

That is not a flaw in this design. It is what "the pipeline deploys the infrastructure" means,
and every team doing it lives with the consequence. Branch protection is one answer. A
separate, plan-only identity for pull requests is another. Deciding it is acceptable is also
an answer, if you can say why.

## What transfers, and what does not

**Transfers everywhere:** gates and their claims; build-once-promote; immutable tags; a
pipeline as a principal; OIDC federation instead of long-lived keys; bootstrapping; the limits
of what a pipeline can catch; and the fact that a delivery identity is a high-privilege one.

**Does not transfer:** the YAML schema, the action names, the flag spellings, and this
provider's pool-and-provider vocabulary.

## This week's work (~180 minutes)

| | |
|---|---|
| Read these notes | 20 min |
| Lab 6 Parts 4–6: federation, the pipeline, teardown | 110 min |
| Project: implementation begins after your design review | 50 min |

**Lab 6 is due at the end of this week**, including verified teardown. Get the state bucket
order right: it is deleted **last**, after everything it describes.

## Check yourself

1. Define a pipeline in one sentence, then name the claim each of your four stages makes.
2. Why is a removed gate worse than an absent one?
3. "The source was identical." Why is that not the same as "the artefact was identical"?
4. Name the specific failure `:latest` allows that a sha tag does not.
5. Give three properties of a service-account key that make it the wrong credential for CI.
6. Explain federation in three sentences, then say what the attribute condition protects.
7. Your pool id is in a public repository. Why is that all right?
8. A pipeline using local state. Why does run one succeed and run two fail?
9. Why can the state bucket not be created by the Terraform that uses it?
10. Name two things your pipeline cannot catch, and what you would do about each.

## Next week

Putting it together: architecture synthesis, security and cost review as habits, and what it
would actually cost to leave a managed service you have come to depend on. Then the other
half — what makes a measurement trustworthy, and how to present a tradeoff honestly,
including the option you rejected.

**Quiz 7 next week**, and you will peer-review another group's architecture and evidence.
