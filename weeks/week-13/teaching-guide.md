# Week 13 — Teaching guide: Infrastructure as code, environments and delivery pipelines

| | |
|---|---|
| **Outcomes** | CLO-7, CLO-9, CLO-8 (design review) |
| **Assessment** | **Quiz 6** (CLO-5, CLO-6; CLO-7 and CLO-9 **through the threads only** — cleanup since Lab 2, CI since week 3 — never that day's Terraform material) · **Lab 6 due at the start of week 14** |
| **Practical** | Lab 6 (one-week lab, D-67) · **project design review** |
| **Prep time** | ~5 h first delivery, ~2 h subsequently |

> **Restructured 2026-11-05 (D-66, D-67).** The last teaching week. It carries what were two
> weeks — declarative infrastructure and environments, then delivery pipelines — with Lab 6
> cut to one week and the project design review kept. The teaching notes below are the two
> former weeks' notes, kept whole; the session plan says how much of each fits now.

## Session objectives

1. Distinguish imperative from declarative provisioning by what each one *records*, and say
   what state is and why the tool cannot work without it.
2. Define drift, and say who decides which side is right.
3. Argue for a specific difference between `dev` and `prod`, and — harder — for a specific
   sameness.
4. Distinguish configuration from secrets, and say why a committed secret is permanent.
5. Describe a pipeline as a sequence of gates, and explain build-once-promote.
6. Explain why a pipeline needs an identity, why a long-lived key is the wrong one, and what
   a federation attribute condition protects.
7. Check each project's scope before it is built (design review).

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| **Declarative, state, drift** | 20 | Their own Lab 2–5 scripts against `infra/main.tf`; why state must exist; drift framed, produced in the lab |
| **Environments, and config vs secrets** | 20 | What may differ, what must not, and who decides |
| Break | 10 | |
| Gates, and build once | 10 | Their ten weeks of CI, reframed; what a moving tag allows |
| **Pipeline identity and federation** | 20 | Why a key is the wrong answer; OIDC in plain terms; the attribute condition |
| What a pipeline cannot catch | 5 | One example, then point at the notes |
| **Quiz 6** | 15 | CLO-5, CLO-6, and the two threads |
| **Design review** | 40 | Each student or pair, against the project rubric |
| Practical | 40 | Lab 6 Parts 1–3 in the room; Parts 4–6 are independent work |

**180 minutes exactly.** 75 concepts · 15 quiz · 40 design review · 40 practical, plus the
break.

> **What halving the concept time cost, and where it went.** The two former weeks gave these
> topics 185 minutes; they now get 75. Nothing was dropped from the **notes**, which every
> student reads (the week 13 reading budget was raised to 30 minutes to pay for it). What went
> from the **room** was the second pass on each idea: the state file is opened once rather
> than explored, drift is produced in the lab rather than also demonstrated, and federation is
> explained from the supplied bootstrap script rather than built up step by step. If something
> must be cut on the day, cut "what a pipeline cannot catch" to a sentence. Never cut the
> design review — it is the only scheduled scope check before the project is built — and never
> cut the "what must not differ" half of environments, which carries the most marks in Lab 6.

---

## Teaching notes

Each section below was written for a longer block. Teach its first move — the opening
question or demonstration — and leave the rest to the notes. The allocation now:

| Section | Was | Now |
|---|---|---|
| Open with their own scripts · State | 45 | 15 |
| Drift | 15 | 5 |
| Environments · Config versus secrets | 35 | 20 |
| Start with the ten weeks they already have · Build once, promote | 35 | 10 |
| The pipeline needs an identity · Federation | 40 | 20 |
| What a pipeline cannot catch | 15 | 5 |

### Part A — infrastructure and environments

#### Open with their own scripts

Put `labs/lab-02/starter/01-create-vm.sh` on one side of the screen and a slice of
`infra/main.tf` on the other. Ask what each one *is*.

Draw it out: the script is a list of **steps**, and it records what you did. The Terraform
file is a **description of the result**, and it records what you want. Then the question that
matters:

> Run the script twice. What happens? Run the Terraform twice. What happens?

The script fails, or worse, makes a second thing. The Terraform does nothing, because the
world already matches the description. **That is idempotency** — the same word they met in
week 11, applied to infrastructure instead of to messages, and it is worth naming the
connection explicitly. A desired-state description is idempotent for the same reason "set the
balance to 400" is and "add 100" is not.

Then the honest cost of declarative, which tutorials skip: you have to describe everything,
including the things you would have done by hand without thinking; the tool has opinions about
ordering that are sometimes wrong; and you now have a state file to look after.

#### State: why it must exist, and what is in it

Ask the question that makes it necessary:

> Terraform's job is to make the world match the file. You delete a resource from the file.
> How does it know to destroy something, rather than doing nothing?

Let them get there: it must remember what it made. That memory is the **state file**, and it
is a JSON record of every managed resource and its attributes.

Then the two consequences, in order of how much trouble they cause:

**One.** Whoever holds the state holds the truth. Two people with two local state files each
believe they own the infrastructure and neither is told otherwise. That is why real teams put
state in a shared backend with locking, and why the `backend "gcs"` block in `versions.tf` is
commented out with a note rather than absent.

**Two, and do this live.** State contains the *values* of everything it manages. Open one and
scroll. Every output, every attribute, and — if anything sensitive ever passed through
Terraform — that too, in plain text.

> **A secret that goes through Terraform is a secret written to the state file.** Marking a
> variable `sensitive` hides it from the console output. It does not remove it from state.

That single sentence is the most practically dangerous thing in the week and it should be
delivered with the file open.

#### Drift, in one demonstration

Define it as the gap between the description and the world, then say where it comes from:
somebody clicked something. Not malice — an incident at 2 a.m. and a console.

They will produce it deliberately in the practical. What to set up here is the question the
practical asks:

> `terraform plan` now says it will change your service back. Which is right — the console or
> the file?

Let the room argue. The useful answer is that **neither is automatically right**: the file is
right if you have decided the file is authoritative, and that is an organisational commitment,
not a property of the tool. What the tool gives you is *visibility* of the disagreement.

Then push once more: what if two people each believe theirs is the truth? That is not a
Terraform question at all, which is the point.

#### Environments: the second list is the hard one

Start with what may differ, and collect answers — instance counts, log levels, retention.
Easy, and everyone can do it.

Then flip it, and give this plenty of room because it is the assessed skill:

> Name three things that must be **identical** between dev and prod, and say what breaks if
> each drifts apart.

Expect to have to pull the first one out of them. The answers worth reaching: **the container
image** (or dev tested something prod never runs), **the region** (or you have measured the
wrong latency and the wrong bill), and **the shape of the configuration itself** — if prod is a
copy of `main.tf` with edits, then the edits are differences nobody declared.

> **An undeclared difference is why "it works in dev" happens.**

Then the trap this course's own configuration contains, which is better than any invented
example. Dev and prod share **one Firestore database**, because there is one free `(default)`
database per project. The bucket is separated, the topic is separated, the service is
separated — and the data is not. Ask what that means for a student testing a destructive
change in dev.

The real answer is a project per environment. Say so, and then say what stops this course
doing it: a second project means a second free tier only if it is a second *billing account*,
and it is not. **This is a cost constraint producing an architectural compromise**, which is
the most realistic thing in the whole lab.

#### Config versus secrets, briefly

A project id is configuration. A password is a secret. The test is not "is it sensitive" but
**"what happens if this appears in a public repository?"**

Then the part students underestimate:

> You commit a key, notice, and remove it in the next commit. Is it gone?

No. It is in the history, in every clone, in every fork, and quite possibly in a search index
within minutes. **The only fix is to rotate the credential**, and the cleanup is cosmetic.

Tie it back to D-01 — this course has two repositories for exactly this reason — and forward
to Part B, later in this session, where the pipeline needs an identity and the whole design exists to avoid having a
long-lived credential to leak.

### Part B — the delivery pipeline

#### Start with the ten weeks they already have

They have had a pipeline since week 3. Ask, before defining anything:

> Who has been stopped by a red check? What did it stop you doing?

Collect two or three. Then define a pipeline backwards from that experience:

> **A pipeline is a sequence of gates. Each gate is a claim about what cannot get past it.**

Go through theirs and name the claim at each stage: the tests claim the behaviour still
holds; the build claims it produces an artefact; the deploy claims that artefact reached an
environment; the smoke test claims it answered afterwards.

Then the sentence that matters most this week, and it is worth writing on the board:

> **A gate you switched off is worse than no gate, because you still believe you have one.**

Make it concrete with `needs: test`. One line. Delete it and the pipeline still deploys, still
goes green, still looks exactly the same in the Actions tab — and no longer stops anything.

#### Build once, promote

Draw the wrong version first: build for dev, test in dev, then build again for prod. Ask what
could differ between the two builds.

They will say "nothing, it's the same source". Push: a base image that moved, a dependency
resolved a minute later, a transient network failure that produced a partial layer, a build
cache, the clock. **The source was identical and the artefact was not**, and those are two
different claims.

Then the tag question, which is the same idea one level down. `:latest` moves. If dev ran
`docapp:latest` on Tuesday and prod runs `docapp:latest` on Thursday, they may be different
bytes and **nothing recorded which** — so when prod breaks you cannot even establish what is
running. A sha tag cannot lie about that.

#### The pipeline needs an identity, and a key is the wrong one

Ask what the pipeline is, from Google Cloud's point of view. It is just a program calling an
API, so it needs a principal, like anything else.

The obvious route is a service-account key pasted into a repository secret. Put Google's own
words up (R-14): a key "must be treated like a password", and "by default, these credentials
never expire".

Then work through what that means. Make the room supply the list: it is a file, so it can be
copied; it does not expire, so a leak in 2026 is still a leak in 2029; a GitHub secret is
readable by any workflow in the repository, including one added in a pull request if the
settings allow it; and rotating it means finding every place it was pasted.

Then reach back to the config-versus-secrets point from the first half of the session:

> **You cannot leak a credential you do not have.**

#### Federation, in plain terms

Resist the API detail. Three sentences:

1. GitHub will sign a short-lived token asserting *this workflow, in this repository, on this
   commit*.
2. Google Cloud is configured to trust tokens signed by GitHub — **but only when the
   assertion matches a condition you wrote**.
3. It exchanges that for a short-lived access token. Nothing long-lived exists anywhere.

Then the question that checks understanding, and it is Lab 6's:

> `deploy.yml` is in a **public** repository and contains your pool id and your deployer
> account's email. Somebody forks it. What stops them deploying into your project?

Let them squirm briefly. The answer is the **attribute condition**: the trust is bound to
`your-org/your-repo`, and a fork's token asserts a different repository, so the exchange
fails. The pool id is configuration — it names a trust relationship and grants nothing on its
own. A key would have been the opposite.

Then generalise, because this is the transferable part: **OIDC federation is how every CI
system should now authenticate to every cloud.** The product names differ; the pattern does
not.

#### What a pipeline cannot catch

Short, and the honesty matters. Ask what their pipeline would *not* stop.

Draw out: a test that was never written; a change that is correct and a bad idea; a
performance regression nobody measures; a config change that is valid and wrong; anything
about data. And the one that lands hardest, which their own smoke test demonstrates:

> The smoke test fails the **run**. The bad revision is already serving traffic.

A pipeline is a filter, not a guarantee, and the useful follow-up is what you would add —
gradual rollout, automatic rollback — and what each costs. Lab 6 asks them to describe it
rather than build it, deliberately.

---

## Quiz 6 (15 min)

Covers **CLO-5 and CLO-6** — asynchrony, idempotency, failure, evidence — and touches CLO-7
and CLO-9 **only through the threads students have been living with**: cleanup since Lab 2,
and CI since week 3.

**It must not assess today's Terraform material.** That was a real defect found in an earlier
audit and corrected; the principle is that a quiz assesses what students have practised, not
what they heard an hour ago.

---

## Design review (40 min)

Not a lecture block. Each student or pair, in turn, for three to four minutes, against
`project/rubric.md`. Timebox visibly; ten individual projects fit in forty minutes only if
you are strict.

Three questions each, and nothing else:

1. **What is the question your experiment answers?** If it is not a question with a
   measurable answer, fix that now rather than in week 15.
2. **What will you reuse, and what will you build?** The delivery path comes from Lab 6 and
   is not rebuilt (D-28). Anyone planning to build a pipeline is over scope and should be
   told so immediately.
3. **What is the smallest version of this that would still be worth demonstrating?** Write
   that down with them. It is what they fall back to in week 15, and having named it in week
   13 is what makes falling back a decision rather than a failure.

The most common intervention by a distance is **cutting scope**. Expect to do it for most of
the room, and say out loud that it is normal.

---

## Common misconceptions

| Misconception | Surfaces as | Response |
|---|---|---|
| "Terraform is a deployment tool" | Constantly | It makes the world match a description. Deployment is one use. |
| "The state file is a cache" | State block | Delete it and watch it offer to build everything again. It is the only record that the world is yours. |
| "`sensitive = true` protects a secret" | Secrets block | It hides console output. State still has the value. |
| "Drift means someone did something wrong" | Drift block | It usually means someone fixed an incident at 2 a.m. The tool shows the disagreement; it does not settle it. |
| "Dev and prod differ, that's the point" | Environments block | They differ in the few ways you chose. Every other difference is a bug you have not met yet. |
| "We'll use `latest` in dev and pin in prod" | Environments block | Then dev tested something prod will never run. |
| "Two environments means two of everything" | Firestore trap | Not when the free tier is per project. Show them the table. |
| "I removed the key in the next commit" | Secrets block | It is in every clone. Rotate it. |
| "`terraform destroy` means it's gone" | Practical | It means the tool believes so. Verify independently — `operations/cleanup.md`. |

| Misconception | Surfaces as | Response |
|---|---|---|
| "CI/CD is a tool you install" | Constantly | It is a set of claims you decided to enforce. The YAML is the cheap part. |
| "Green build means it works" | Everywhere | It means the checks you wrote passed. Name one it does not include. |
| "The pipeline deploys, so it is a deployment tool" | Gates block | It is a sequence of gates. Deployment is the last one. |
| "We'll use `latest` and pin later" | Build block | Then you cannot say what is running in prod, today, right now. |
| "A key in a GitHub secret is encrypted, so it's fine" | Identity block | It is encrypted at rest and readable by workflows. And it never expires. |
| "Federation is complicated" | Federation block | The setup is fiddly; the idea is three sentences. Do not let the setup obscure them. |
| "The pool id is a secret" | Federation block | It names a trust relationship. The condition is what protects it. |
| "The smoke test protects prod" | Pipeline block | It tells you afterwards. The bad revision is already live. |
| "State is fine, it worked locally" | Practical | A runner is a new machine every time. The second run is where it bites. |

---

## Practical (40 min): Lab 6, one week

Lab 6 is now a one-week lab (D-67): about 40 minutes here and 150 at home, due at the start of
week 14. The federation pool, deployer account and state bucket come from a supplied script,
and the two second-run pipeline bugs are predicted from the supplied fixes rather than found
by failing. Use the 40 minutes for **Parts 1–3**, which are where students most need someone
in the room.

- **Part 1 is reading, and it is worth protecting.** Fourteen resources, and every one of
  them is something they built by hand in Labs 3–5. Have them find the two Pub/Sub
  service-agent grants specifically — in Lab 5 those cost the room twenty minutes and an error
  message, and here they are four lines that will be right every time.
- **`terraform` is no longer in Homebrew** (it is BUSL-licensed now). `brew install opentofu`
  and `tofu` is a drop-in for everything this lab does — it is what the configuration was
  validated with. Say this at the start rather than during ten separate install failures.
- **`init` downloads a provider.** On a room's worth of laptops and one wireless network,
  start it during the design review, before the practical begins.
- **The service is private**, so a plain `curl` returns 403 and several students will report it
  as broken. Say once, to the room, that it is correct and that the invoker `TODO` is the fix.
- **Make everyone produce drift before they leave.** It takes two minutes — change
  `max-instances` in the console, re-run `plan` — and it is the single most memorable thing in
  the week, and the only demonstration of it they will get.
- **Watch for the wrong workspace.** `terraform workspace show` before every apply.
- **Before they leave, point at Part 4's script and its header.** It has not been run against a
  real project (`labs/lab-06/starter/README.md`). The single most common failure in federation
  is a typo in the repository name of the attribute condition; tell them to read it character
  by character before searching.
- **Teardown order is graded and the state bucket goes last.**

Be explicit that most of Parts 4–6 happen outside the session, that Lab 6 is due at the start
of week 14, and that **week 14 is the final exam** — there is no slack after it.

## Links

- Student notes: `weeks/week-13/student-notes.md`
- Lab: `labs/lab-06/README.md` · Rubric: `labs/lab-06/rubric.md` · Bootstrap: `labs/lab-06/starter/`
- Configuration: `infra/` — read `infra/README.md` first, including its validation status
- Pipeline: `.github/workflows/deploy.yml` — read every TODO before the session
- Project: `project/brief.md` · `project/rubric.md` · `project/milestones.md`
- Cost: `operations/cost-model.md` · Cleanup and teardown order: `operations/cleanup.md`
- Quiz 6 key and design-review notes: private repo, `quiz-keys/` and `project-guidance.md`
