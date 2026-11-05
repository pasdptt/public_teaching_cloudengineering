---
marp: true
theme: cloudcourse
paginate: true
footer: 'Week 4 · Hierarchy, virtual machines, identity'
---

<!--
Deck for week 4. Derived from weeks/week-04/teaching-guide.md — that file is authoritative
for the teaching; this is what goes on the wall.

Render:  bash course/slides/render.sh 04
-->

<!-- _class: lead -->

# Hierarchy, virtual machines, identity

## Week 4

Cloud Computing: Principles and Practice

<!--
TIMING: 180 min total — 90 concepts · 15 quiz · 75 practical (30 activation + 45 Lab 2). No break row in the plan; take one at the quiz.
Guide: weeks/week-04/teaching-guide.md
HIGHEST-RISK SESSION IN THE COURSE. Before you start: trial terms re-fetched (references.md R-01, R-02); fallback handout (cloud-access-and-fallback.md §4) printed; the list of students who flagged eligibility problems in week 1.
-->

---

## Today the cloud stops being a diagram

Weeks 1–3 ran on your laptop. Today you get an account, a project, and a machine you do not own.

Three questions run through every cloud lab from here on:

1. **Where does this live** — and who pays for it?
2. **Who is this code** — and what is it allowed to do?
3. **How do I know it is gone** — when I am finished?

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:00 – 0:15</span>

# Hierarchy

Where things live, and why it matters for the bill

---

## Organisation → folder → project → resource

You will have **one project and no organisation**. The hierarchy still matters, for two reasons.

**Billing attaches to the project.** Every VM, bucket and database belongs to exactly one project, linked to one billing account. "Who pays for this?" is decided when you decide where it lives.

**Policy flows downwards.** A role granted on the project applies to everything in it — including resources that do not exist yet.

---

<!-- _class: punch -->

## Convenient, and the commonest way to grant far more access than you meant.

<!--
Lab 2 Part 4 is the concrete example: the default service account holding Editor on the whole project. Do not resolve it here; the identity block does.
-->

---

## Not "the same as an AWS account"

The nearest thing elsewhere is an account or a subscription. It is close, and it is not the same.

*`course/concept-to-gcp-map.md` exists to stop exactly this kind of false equivalence.*

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:15 – 0:30</span>

# Regions and zones

Two ideas that pull in opposite directions

---

## Blast radius and latency floor

| | What it is | What it means for you |
|---|---|---|
| **Zone** | One failure domain — independent power, cooling | Everything in it can fail **together**. Surviving that costs a second zone. |
| **Region** | A geographic area of zones | A **latency floor**. Nothing makes Iowa closer to Bangkok. |

You measure the floor yourself in Lab 2 Part 5.

---

<!-- _class: ask -->

## Why does a Bangkok class deploy to Iowa?

<!--
Take answers before you give yours. Guide: "Justify the region out loud".
-->

---

## Because cost drove an architecture decision

- The Always Free `e2-micro` exists **only** in `us-west1`, `us-central1` and `us-east1`.
- The same lab in `asia-southeast1` would be a **billed** lab.
- Every latency figure you take compares against itself, so a constant offset changes no conclusion.
- For a real service with Thai users, the answer would be different.

> The decision is recorded, and its downside is known. That is the whole lesson.

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">0:30 – 0:50</span>

# The virtual machine

Week 2's hypervisor, rented

---

## What a cloud VM adds

- **Machine type** — a named bundle of vCPU and memory. `e2-micro` is the only one the free tier covers.
- **Image** — the OS you start from. Lab 2 uses Debian 12.
- **Boot disk** — a **separate resource**, attached to the instance.
- **Metadata service** — an address reachable only from inside the instance. It hands out information, **including credentials**.

---

<!-- _class: cost -->

## The boot disk can outlive the machine

It is a separate resource, so deleting the VM is a question about the disk as well.

`--boot-disk-auto-delete` is what prevents an orphan. Lab 2 asks you to **verify** it worked, not to trust it.

*A disk with no machine bills every hour, and nothing about it looks broken.*

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:50 – 1:05</span>

# Addresses

The most surprising price in the course

---

## Ephemeral and static

**Ephemeral** — assigned when the instance starts, released when it is deleted. Changes every time.

**Static** — reserved by you, kept until you release it, survives the instance entirely.

---

<!-- _class: cost -->

## Which costs more?

| External IPv4 address | Rate | 30 days |
|---|---|---|
| Attached to a **running** VM | $0.005/h | ~$3.60 |
| **Static, attached to nothing** | **$0.01/h** | **~$7.20** |

*Verified 2026-09-21 · `operations/cost-model.md` §2*

<!--
Ask WHY idle costs more before you say anything. Let them get to scarcity, and price as a signal.
-->

---

<!-- _class: punch -->

## An address doing nothing costs twice an address doing work.

---

<!-- _class: cost -->

## "I stopped the VM, so I'm not paying"

Wrong twice.

1. The **boot disk** still bills.
2. A **static** address counts as in use while its VM is merely stopped.

Lab 2 uses an **ephemeral** address and **deletes** the VM rather than stopping it.

You will find that annoying, because the address changes every time. **Notice the annoyance.** It is exactly the pressure that makes people reserve a static address without thinking.

---

<!-- _class: block -->

<span class="min">25 minutes</span><span class="clock">1:05 – 1:30</span>

# Identity

Who is this code?

---

## Principals, roles, service accounts

Every action in a cloud is performed by a **principal** — a human user, or a **service account** representing a workload.

IAM grants **roles** to principals **on resources**. A role is a bundle of permissions.

The surprise: your code on a VM has an identity, and **nobody put a credential on the machine**.

---

<!-- _class: demo -->

## Ask the machine who it is

```bash
curl -sS -H "Metadata-Flavor: Google" \
  http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email
```

Run on the instance. The same service will hand out a **token** for that identity.

<!--
Live if a VM is up; otherwise recorded output, and SAY it is recorded.
Then ask the room: who put a credential on this machine? Nobody.
Guide: "The metadata demo"
-->

---

<!-- _class: ask -->

## No key to leak, rotate or commit.
## So what is the catch?

<!--
Wait for it: anything that can run code on the instance gets that identity.
-->

---

## Anything that runs code there **is** that identity

So "what can this instance's identity do?" is a **security** question, not an administrative one.

And by default the answer is alarming: the default Compute Engine service account typically holds **Editor** on the whole project.

Your application reads and writes **nothing** in Google Cloud. It needs no permissions at all.

<!--
Show the project IAM policy with the default SA holding Editor. Ask what a remote-code-execution bug would have meant. Do not soften it. Lab 2 Part 4 is the fix.
-->

---

<!-- _class: punch -->

## Least privilege is not a hardening step you do later. It is the default you start from.

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">1:30 – 1:45</span>

# Quiz 2

Weeks 1–3

<!--
CLO-1, CLO-2, CLO-3 (introductory). Scenarios: attribute an incident; correct a statement about state durability; a container/VM difference; what survives a restart. Key in the private repository.
-->

---

<!-- _class: block -->

<span class="min">30 minutes</span><span class="clock">1:45 – 2:15</span>

# Practical: activation

Trial, project, `gcloud`, a $1 alert

---

## Before anyone clicks

**$300, 90 days from *your* signup.** A payment method is for identity verification only.

A **temporary authorisation of about $0–$1** may appear on your statement for a few days. It is not a charge.

**You cannot be billed without manually upgrading** to a paid account. This course never asks you to.

**Cannot activate?** You start the documented local path **now, at your desk**, with everyone else. Not later, and not privately.

<!--
Hand out the fallback sheet to everyone, not just the students you expect to need it. The intent is that taking the fallback costs nothing socially.
-->

---

<!-- _class: demo -->

## In this order

1. Activate the Free Trial.
2. Create **one** project. Write down its id.
3. Install `gcloud`, then:

```bash
gcloud init
gcloud config list                 # your project and account
gcloud billing accounts list       # your trial billing account
```

4. **Budget alert at $1.**

<!--
RECORD WHO ACTIVATED AND ON WHAT DATE. Their 90 days starts now and week 15 has to fit inside it. Anyone who activated early in week 1 needs a plan today.
-->

---

<!-- _class: cost -->

## Why $1, when you have $300?

The whole course is expected to cost **under a dollar**. An alert at $1 should never fire — which is exactly what makes it a signal.

An alert at $150 would tell you something had been wrong for weeks.

> **An alert is a notification, not a cap.** It stops nothing.

---

<!-- _class: block -->

<span class="min">45 minutes</span><span class="clock">2:15 – 3:00</span>

# Practical: Lab 2

Parts 1–2

---

<!-- _class: demo -->

## Part 1 — a machine you do not own

```bash
cd labs/lab-02/starter
cp config.env.example config.env     # your project id
./01-create-vm.sh
./02-deploy.sh
```

**Checkpoint:** one `RUNNING` instance, `e2-micro`, in `us-central1`.

```bash
gcloud compute ssh docapp-vm --zone "$ZONE" \
  --command 'curl -sS http://127.0.0.1:8080/healthz'
```

<!--
gcloud compute ssh is slow the first time: it generates and propagates a key. Tell them to wait, not to re-run it five times.
Billing not linked to the project → every create fails on permissions.
-->

---

<!-- _class: ask -->

## It works on the VM.
## It will not work from your laptop.

Write down **why** before you investigate.

<!--
DESIGNED. Do not rescue them. At least two plausible reasons; only one is the actual one. Next week's two-boundaries block depends on them having guessed.
-->

---

## Three constraints that keep this free

| Constraint | Break it and |
|---|---|
| Exactly **one** `e2-micro` | Always Free covers one per **billing account** |
| Region `us-central1` | The allowance exists in three US regions only |
| **Ephemeral** external IP | A reserved unattached address is double the price |

Then **Part 2** — open exactly one door. `03-firewall.sh` asks you to choose the source range.

---

## This week's work — 180 minutes

| | |
|---|---|
| Read the notes; prepare for Quiz 2 | 30 min |
| Trial activation, billing alert, first cleanup verification | 30 min |
| Lab 2 Parts 1–2 | 120 min |

**Delete, do not stop.** Teardown verification is graded from this lab onwards.

---

<!-- _class: lead -->

# Next week

Virtual networking and access boundaries

**Lab 2 due** — with verified teardown
