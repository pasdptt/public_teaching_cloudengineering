# Week 5 — Virtual networking and access boundaries

**Lab 2 is due at the end of this week**, including its graded teardown verification.

---

## The network is software now

Your VM is on a **VPC network** — a software-defined network you configure with API calls
rather than cables. Inside it:

- A **subnet** is a range of private addresses in one region.
- A **route** decides where packets for a destination go.
- A **firewall rule** decides whether a packet is allowed at all.

One structural quirk worth knowing, because it genuinely differs elsewhere: **a GCP VPC is
global, with regional subnets.** On several other providers the VPC itself is regional. It is
not a better or worse design, but it is a real difference, and it is the kind of thing that
makes "AWS VPC ≈ GCP VPC" a sentence that will eventually hurt you.

## Firewall rules are allow-lists

The default is **deny**. Nothing reaches your instance from outside until a rule says it may.

A rule has: a direction (ingress or egress), an action, a protocol and port, a **source
range**, and a **target** — which instances it applies to. In Lab 2 the rule targets instances
tagged `docapp`, not the whole network. That scoping is the difference between opening a door
and opening a door in every wall.

The source range is the decision that matters:

- `0.0.0.0/0` — the entire internet. Fastest way to make a lab work. A standing invitation.
- `203.0.113.4/32` — one address, yours. Narrow, and it breaks when your address changes,
  which on a home or campus network it will.

Neither is "correct". Lab 2 asks you to pick one, justify it, and then say what you would
choose for a service real users had to reach — because that is a genuinely different question
and noticing it is the skill.

## Two boundaries, not one

This catches everyone once, and Lab 2 is built around making you meet it deliberately.

For a request to arrive, **two separate things** must both be true:

1. **The network must deliver the packet.** That is the firewall rule.
2. **The process must be listening on an address that can receive it.** That is
   `DOCAPP_HOST` — `127.0.0.1` accepts only from the machine itself; `0.0.0.0` accepts on
   every interface.

Get the firewall right and bind to loopback: the packet arrives and nothing is listening.
Bind to `0.0.0.0` with no firewall rule: nothing listening is not the problem, because the
packet never arrives.

**The symptoms differ, and that is your best diagnostic:**

| Symptom | Meaning | Likely cause |
|---|---|---|
| **Connection refused**, immediately | Something answered, and said no | The packet arrived. Nothing is listening on that port. |
| **Hangs**, then times out | Nothing answered at all | The packet was *dropped*. A firewall silently discarded it. |

A firewall that dropped your packet does not send you a polite explanation — it says nothing,
which is why the symptom is a hang. Learn this pair and most cloud network debugging becomes
a two-minute job instead of an afternoon.

## Public and private

An instance can have a private address only, and still reach the internet outbound through a
gateway. It simply cannot be reached *inbound*. For anything that does not need to serve
public traffic — a database, a worker — that is the right default, and it removes a whole
category of problem rather than defending against it.

## What a load balancer actually does

You will not configure one until Lab 4, but the idea belongs here.

A load balancer is a stable front door with a health-checked pool of backends behind it. Three
things it gives you:

- **One address** that does not change when the instances behind it do.
- **Distribution** across healthy backends.
- **Health checking** — an instance that fails its check stops receiving traffic.

That last one is the interesting one, and it connects straight back to week 3: the balancer
cannot tell a *slow* backend from a *dead* one either. It has the same problem you do, and it
solves it the same way — a timeout, which is a guess.

## Identity at the boundary

Week 4 introduced service accounts. The networking version of the same idea: a request
crossing a boundary carries an identity, and something at that boundary decides whether that
identity may proceed.

In Lab 2 you trace one request and name, at every hop, **what permitted it** and **who it was
acting as**. Those two questions are the whole of access control, and they scale from one VM
to any architecture you will meet.

## Finishing Lab 2: the part that is graded

Lab 2 ends with teardown **and verification**. From this lab onwards, "I deleted it" is not
worth marks; the verification output is.

Delete rather than stop. A stopped VM keeps its disk, and a static address keeps billing
whether or not the instance runs. Then run the verification and **read** it — the `TODO` in
`06-verify-clean.sh` asks you to add checks for the three resource classes that survive a
deleted VM. Working out which three is part of the exercise, and
`operations/cost-model.md` §6 is where to look.

Check the billing report the next day too. Usage takes time to appear, and a project that
looked clean on Friday and shows charges on Sunday has taught you something real about how
metering works.

## This week's work (~180 minutes)

| | |
|---|---|
| Read these notes | 25 min |
| Lab 2 Parts 3–6 and the write-up, including teardown verification | 155 min |

## Check yourself

1. What is the default for inbound traffic to a new VPC, and what changes it?
2. `curl` hangs and times out. Refused immediately. What does each tell you?
3. Explain why both `DOCAPP_HOST` and a firewall rule are needed, in terms of boundaries.
4. Your firewall rule targets tag `docapp` rather than the whole network. What does that buy?
5. Why is a private-only instance a good default for a database?
6. A load balancer removes an unhealthy backend. What problem from week 3 does it still have?
7. You ran the teardown script and it printed no errors. Why is that not enough?

## Next week

Storage: block, file, object and database, and what access pattern each one assumes. Lab 3
starts, and your application's state finally leaves the machine it runs on.
