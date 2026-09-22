# Week 13 — Teaching guide: Delivery pipelines

| | |
|---|---|
| **Outcomes** | CLO-9, CLO-7, CLO-8 (design review) |
| **Assessment** | — (**Lab 6 due**) |
| **Practical** | Lab 6 Parts 4–6 · **project implementation begins, with an instructor design review** |
| **Prep time** | ~4 h first delivery, ~1.5 h subsequently |

> **Restructured 2026-09-22 (D-24).** This week was previously an architecture-synthesis
> lecture; that content moved to week 14. It now carries the second half of Lab 6 **and** the
> start of the project, which makes it the second-tightest week in the course
> (`course/workload-budget.md` splits the independent time 110/50).

## Session objectives

1. Describe a pipeline as a sequence of gates, and say what each one claims.
2. Explain build-once-promote, and name the specific failure a moving tag allows.
3. Explain why a pipeline needs an identity, and why a long-lived key is the wrong one.
4. Describe OIDC federation in plain terms, and say what an attribute condition protects.
5. Name something a pipeline **cannot** catch, and say what you would do instead.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| **Gates, and what each one claims** | 20 | Their own ten weeks of CI, reframed |
| Build once, promote | 15 | The artefact, and what a moving tag allows |
| **Pipeline identity, and the key problem** | 20 | Why a key is the wrong answer |
| **Federation** | 20 | OIDC in plain terms; the attribute condition |
| Break | 10 | |
| What a pipeline cannot catch | 15 | Where the gate stops and judgement starts |
| **Design review** | 40 | Each student or pair, against the project rubric |
| Practical | 40 | Lab 6 Parts 4–6 |

**180 minutes exactly.** 90 concepts · 40 design review · 40 practical, plus the break.

> **This week's shape is different and deliberately so.** The design review is not optional
> and cannot move — it is CLO-8 evidence and it is the only scheduled point where a student's
> project scope is checked before they build it. The practical is 40 minutes rather than 60
> because of it; `course/workload-budget.md` records the trade.

---

## Teaching notes

### Start with the ten weeks they already have

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

### Build once, promote

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

### The pipeline needs an identity, and a key is the wrong one

Ask what the pipeline is, from Google Cloud's point of view. It is just a program calling an
API, so it needs a principal, like anything else.

The obvious route is a service-account key pasted into a repository secret. Put Google's own
words up (R-14): a key "must be treated like a password", and "by default, these credentials
never expire".

Then work through what that means. Make the room supply the list: it is a file, so it can be
copied; it does not expire, so a leak in 2026 is still a leak in 2029; a GitHub secret is
readable by any workflow in the repository, including one added in a pull request if the
settings allow it; and rotating it means finding every place it was pasted.

Then reach back to week 12's ending:

> **You cannot leak a credential you do not have.**

### Federation, in plain terms

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

### What a pipeline cannot catch

Short, and the honesty matters. Ask what their pipeline would *not* stop.

Draw out: a test that was never written; a change that is correct and a bad idea; a
performance regression nobody measures; a config change that is valid and wrong; anything
about data. And the one that lands hardest, which their own smoke test demonstrates:

> The smoke test fails the **run**. The bad revision is already serving traffic.

A pipeline is a filter, not a guarantee, and the useful follow-up is what you would add —
gradual rollout, automatic rollback — and what each costs. Lab 6 asks them to describe it
rather than build it, deliberately.

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

## Practical (40 min): Lab 6 Parts 4–6

- **Two of the four deploy TODOs fail on the second run, not the first** — the backend and the
  workspace. That is deliberate, and it is the most realistic thing in the lab. Tell students
  to merge twice before concluding anything works.
- **The state bucket is created by hand.** Expect "why isn't this in Terraform?" — it is the
  best question of the week, and the answer is bootstrapping: Terraform needs somewhere to put
  state before it can create anything, including that somewhere.
- **`-migrate-state` is worth watching.** Their dev environment moves into the bucket and
  nothing about the resources changes. State becoming concrete is the point.
- **The smoke test needs a token with `--audiences`.** The service is private (D-41). Say once
  to the room that a 403 here means the invoker grant, not a broken deployment.
- **Federation setup will eat the time** if you let it. The single most common failure is a
  typo in the attribute condition's repository name. Tell them to read it character by
  character before searching.
- **Teardown order is graded and the state bucket goes last.** Anyone who deletes it first
  spends the rest of the week doing cleanup from memory in a console, which is at least
  thematically appropriate.

Most of Parts 4–6 will be finished outside the session. Be explicit about that, and about the
deadline being the end of this week.

## Links

- Student notes: `weeks/week-13/student-notes.md`
- Lab: `labs/lab-06/README.md` · Rubric: `labs/lab-06/rubric.md`
- Pipeline: `.github/workflows/deploy.yml` — read every TODO before the session
- Configuration: `infra/` · state and bootstrapping: `infra/versions.tf`
- Project: `project/brief.md` · `project/rubric.md` · `project/milestones.md`
- Teardown order: `operations/cleanup.md`
- Design-review notes and the scope-cutting script: private repo, `teaching-notes/`
