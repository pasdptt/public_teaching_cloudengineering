# Week 4 — Cloud resource hierarchy, virtual machines and identity

**Quiz 2 this week** (weeks 1–3). **You activate your trial in the session. Lab 2 starts.**

---

## Where things live, and why it matters for the bill

Google Cloud arranges resources in a hierarchy: **organisation → folder → project →
resource**. For this course you have one project and no organisation, so the hierarchy looks
like an irrelevance. It is not, for two reasons.

**Billing attaches to the project.** Every VM, bucket and database belongs to exactly one
project, and that project is linked to one billing account. So "what did this cost?" is
answerable, and "who pays for this?" is a design decision you make when you decide where
something lives. Real organisations use projects as a cost boundary for exactly this reason.

**Policy flows downwards.** A permission granted at the project level applies to everything in
it, including resources that do not exist yet. That is convenient and it is how people
accidentally give far more access than they meant to. You will see a concrete example in
Lab 2 Part 4.

The nearest thing on another provider is an account or a subscription. It is not an exact
match, and pretending otherwise is the kind of false equivalence `course/concept-to-gcp-map.md`
exists to prevent.

## Regions and zones

A **region** is a geographic area. A **zone** is one failure domain inside it — in practice,
a datacentre or a group of them with independent power and cooling.

Two things follow, and they pull in opposite directions:

- **A zone is a blast radius.** Everything in one zone can fail together. Surviving that means
  running in more than one, which costs more and makes your design harder.
- **A region is a latency floor.** Nothing you do makes `us-central1` closer to Bangkok. You
  measure that floor yourself in Lab 2 Part 5.

This course runs in **`us-central1`**, and you should know why, because it is a real
engineering trade rather than an arbitrary default: the Always Free tier exists only in
`us-west1`, `us-central1` and `us-east1`. Running the same lab in `asia-southeast1` would be
a *billed* lab. Every latency measurement you take compares against itself, so a constant
offset changes none of the conclusions — and for a real service serving Thai users, the
answer would be different. Being able to say that out loud is the point.

## The virtual machine

From week 2: a hypervisor presents virtual hardware, a guest OS believes it, and you operate
everything from that OS upwards. A cloud VM adds a few things worth knowing:

- **Machine type** is a named bundle of vCPU and memory. `e2-micro` is the small one, and the
  only one covered by the free tier.
- **Image** decides what OS you start from. Lab 2 uses Debian 12.
- **Boot disk** is a *separate resource* attached to the instance. That separation matters:
  it can outlive the instance, and keep billing. `--boot-disk-auto-delete` is what prevents
  that, and Lab 2 asks you to verify it worked rather than trust it.
- **Metadata service** is a special address, reachable only from inside the instance, that
  hands out information — including credentials. More on that below.

## Addresses, and the most surprising price in the course

A VM needs an address to be reachable from outside. Two kinds:

- **Ephemeral** — assigned when the instance starts, released when it is deleted. Changes
  every time.
- **Static** — reserved by you, kept until you release it, survives the instance entirely.

Now the prices (verified 2026-09-21):

| Situation | Rate | Over 30 days |
|---|---|---|
| Attached to a **running** VM | $0.005/h | ~$3.60 |
| **Static, reserved, attached to nothing** | **$0.01/h** | **~$7.20** |

**An address doing nothing costs twice an address doing work.** That is not a billing quirk;
it is a deliberate signal. IPv4 addresses are genuinely scarce, and the provider charges more
for hoarding one than for using it.

The trap behind it: a **static** address counts as "in use" while its VM is merely *stopped*.
So the sentence "I stopped the VM, I'm not paying" is wrong twice — the disk still bills, and
so does the address.

Lab 2 uses an ephemeral address and **deletes** the VM rather than stopping it. You will find
that annoying, because the address changes every time. Notice the annoyance. It is the exact
pressure that makes people reserve a static address without thinking about the consequence.

## Identity: who is this code?

Every action in a cloud is performed by a **principal** — a human user, or a **service
account** representing a workload. IAM grants **roles** to principals on resources, and a
role is a bundle of permissions.

The part that surprises people: **your code on a VM has an identity without anyone putting a
credential on the machine.** Ask the metadata service and it hands you a token:

```bash
curl -sS -H "Metadata-Flavor: Google" \
  http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email
```

That is excellent design — no key file to leak, rotate or commit — and it has a direct
consequence you should think about: **anything able to run code on that instance gets that
identity.** Which makes the question "what can this instance's identity do?" a security
question, not an administrative one.

And by default the answer is alarming. The default Compute Engine service account typically
holds **Editor** on the whole project. Your application, right now, reads and writes nothing
in Google Cloud. It needs no permissions at all. Lab 2 Part 4 has you replace Editor with a
single role that lets it write logs, and explain what an attacker would have gained from the
difference.

That is **least privilege**: not a hardening step you do later, but the default you start
from.

## Your trial, and your guardrails

In the session you will activate the Free Trial: $300, 90 days from *your* signup. A payment
method is required for identity verification only, and a **temporary authorisation of
roughly $0–$1 may appear on your statement for a few days**. It is not a charge.

**You cannot be billed without manually upgrading to a paid account**, which this course never
asks you to do. When the trial ends, workloads stop.

Then set a **budget alert at $1**. Not $150. Your whole course is expected to cost under a
dollar, so a $1 alert should never fire — which is exactly what makes it a signal. And say
this to yourself once: **an alert is a notification, not a cap.** It stops nothing.

## This week's work (~180 minutes)

| | |
|---|---|
| Read these notes; prepare for Quiz 2 | 30 min |
| Trial activation, billing alert, first cleanup verification | 30 min |
| Lab 2 Parts 1–2 | 120 min |

## Check yourself

1. Why does it matter, practically, that billing attaches to a project?
2. Zones and regions: which is a blast radius and which is a latency floor?
3. Why does this course run in `us-central1`, and what does that cost you?
4. A static IP attached to nothing costs $0.01/h. Why more than one on a running VM?
5. You stop a VM to save money. Name two things that keep billing.
6. Nobody put a credential on your instance, yet its code has an identity. Where from, and
   what is the security consequence?
7. Your application needs no Google Cloud permissions. Why attach a service account with one
   tiny role rather than none at all?

## Next week

Virtual networking properly: subnets, routes, firewall rules as allow-lists, and what a load
balancer does. You finish Lab 2 — including the graded teardown verification.
