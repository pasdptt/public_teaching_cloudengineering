---
marp: true
theme: cloudcourse
paginate: true
footer: 'Week 5 · Networking and access boundaries'
---

<!--
Deck for week 5. Derived from weeks/week-05/teaching-guide.md — that file is authoritative
for the teaching; this is what goes on the wall.

Render:  bash course/slides/render.sh 05
-->

<!-- _class: lead -->

# Networking and access boundaries

## Week 5

Cloud Computing: Principles and Practice

<!--
TIMING: 180 min total — 90 concepts · 30 discussion · 60 practical. No break row: take one inside the firewall block, the longest.
Guide: weeks/week-05/teaching-guide.md
Before you start: a VM up for the refused-vs-hung demo, or recorded output (and say so). Lab 2 is due at the end of the week, with graded teardown verification.
-->

---

## Last week's question

It worked on the VM. It did not work from your laptop.

You wrote down why. **Today you find out which of your reasons was the real one** — and how to tell from the symptom alone.

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:00 – 0:15</span>

# The network is software now

VPC, subnets, routes

---

## Configured with API calls, not cables

Your VM sits on a **VPC network**. Inside it:

- A **subnet** is a range of private addresses in one region.
- A **route** decides where packets for a destination go.
- A **firewall rule** decides whether a packet is allowed at all.

---

## One quirk worth knowing

**A GCP VPC is global, with regional subnets.** On several other providers the VPC itself is regional.

Not better or worse. A real structural difference — and the reason "AWS VPC ≈ GCP VPC" is a sentence that will eventually hurt you.

---

<!-- _class: block -->

<span class="min">25 minutes</span><span class="clock">0:15 – 0:40</span>

# Firewall rules

Allow-lists, and the default is deny

---

## What a rule says

| Part | Lab 2's rule |
|---|---|
| Direction | Ingress |
| Action | Allow |
| Protocol and port | TCP 8080 |
| **Source range** | your decision |
| **Target** | instances tagged `docapp` — not the whole network |

Nothing reaches your instance from outside until a rule says it may.

---

<!-- _class: punch -->

## Target scoping is the difference between opening a door and opening a door in every wall.

---

## The source range is the decision

`0.0.0.0/0` — the entire internet. The fastest way to make a lab work. A standing invitation.

`203.0.113.4/32` — one address, yours. Narrow, and it breaks when your address changes — which on a home or campus network it will.

**Neither is "correct".** Lab 2 grades the **justification**, not the value — and then asks what you would choose for a service real users had to reach.

<!--
Break inside this block if the room needs it — the plan has no separate break row.
-->

---

<!-- _class: block -->

<span class="min">25 minutes</span><span class="clock">0:40 – 1:05</span>

# Two boundaries, not one

The centre of the session

---

## Two things must both be true

1. **The network must deliver the packet.** That is the firewall rule.
2. **The process must be listening on an address that can receive it.** That is `DOCAPP_HOST`.

`127.0.0.1` accepts only from the machine itself. `0.0.0.0` accepts on every interface.

<!--
Draw the packet's journey and mark both gates. Ask what breaks if you remove each, and insist the answers differ.
Guide: "Two boundaries, drawn once"
-->

---

<!-- _class: ask -->

## Fast error, or a long wait?

Hands up for each, before I run it.

---

<!-- _class: demo -->

## Two failures, side by side

```bash
# nothing listening on 9999, packet allowed through
curl --max-time 10 http://$EXTERNAL_IP:9999/healthz

# something listening on 8080, firewall rule removed
curl --max-time 10 http://$EXTERNAL_IP:8080/healthz
```

<!--
Take the split for EACH before running it. Live if a VM is up; recorded output otherwise, and say which.
Guide: "The refused-vs-hung demo is the centre of the session"
-->

---

## The symptom tells you where the packet died

| Symptom | Meaning | Likely cause |
|---|---|---|
| **Connection refused**, immediately | Something answered, and said no | The packet arrived. Nothing listening on that port. |
| **Hangs**, then times out | Nothing answered at all | The packet was **dropped** — a firewall discarded it |

---

<!-- _class: punch -->

## Refused means something answered. Hung means nothing did.

<!--
Write it on the board and leave it there for the practical. It saves more time across the rest of the course than anything else this week.
-->

---

<!-- _class: block -->

<span class="min">10 minutes</span><span class="clock">1:05 – 1:15</span>

# Public and private

Remove the problem instead of defending against it

---

## A private-only instance can still reach out

It has no external address, and reaches the internet **outbound** through a gateway.

It simply cannot be reached **inbound**.

For anything that does not serve public traffic — a database, a worker — that is the right default. It removes a whole category of problem rather than defending against it.

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">1:15 – 1:30</span>

# Load balancing

A stable front door

---

## What a load balancer gives you

- **One address** that does not change when the instances behind it do.
- **Distribution** across healthy backends.
- **Health checking** — a backend that fails its check stops receiving traffic.

You will not configure one until Lab 4. The idea belongs here.

---

<!-- _class: ask -->

## How does the balancer know a backend is dead?

<!--
It does not. It waits and guesses — a timeout — exactly as they did in week 3. Thirty seconds, worth it: the hard problem does not go away, it gets a budget and a default value.
-->

---

## Identity at the boundary

Every request crossing a boundary carries an identity, and something at that boundary decides whether it may proceed.

In Lab 2 Part 3 you trace one request and name, **at every hop**:

1. **What permitted it?**
2. **Who was it acting as?**

Those two questions are the whole of access control, from one VM to any architecture you will meet.

---

<!-- _class: block -->

<span class="min">30 minutes</span><span class="clock">1:30 – 2:00</span>

# Discussion

Narrow this design

---

## A design to fix

- A VM with a **public address**
- Firewall: `0.0.0.0/0` on ports **22, 80, 443, 8080 and 5432**
- The **default service account, with Editor**
- A **database on the same instance**

**Small groups, 10 minutes.** List every change you would make, **ordered by risk removed per unit of effort**.

<!--
Expected, roughly in order: close 5432 entirely; replace Editor with a scoped role; narrow or remove 22; scope rules by target tag; question the public address at all.
The point is the ORDERING, not the list. That is what a security review is, and what the project's security band asks for.
Guide: "Discussion (30 min): narrow this design"
-->

---

<!-- _class: ask -->

## Which change removes the most risk for the least effort?

---

<!-- _class: block -->

<span class="min">60 minutes</span><span class="clock">2:00 – 3:00</span>

# Practical

Lab 2 Parts 3–6

---

<!-- _class: demo -->

## Part 3 — trace it, name the identity

```bash
curl -sS -o /dev/null -w 'connect=%{time_connect}s total=%{time_total}s\n' \
     "http://$EXTERNAL_IP:8080/healthz"

gcloud compute instances describe docapp-vm --zone "$ZONE" \
  --format='yaml(name, machineType, networkInterfaces, serviceAccounts)'
```

At each hop: **the rule that permitted it**, and **the identity it acted as**.

<!--
If nobody reacts to "no credential was placed on this machine", stop the room and ask it directly.
-->

---

## Part 4 — give it less than it was given

Replace the default account's **Editor** with a dedicated service account holding only `roles/logging.logWriter`.

`04-service-account.sh` stops the instance to swap the account. **The external IP will change.** That is expected, not broken.

---

## Part 5 — one variable: distance

The same tool, the same settings as Lab 1. On the VM over loopback, then from your laptop across the internet.

```bash
python3 application/tools/measure.py \
  --url "http://$EXTERNAL_IP:8080" --requests 12 --concurrency 1
```

**Three runs each.** Then concurrency 4. The variation between runs **is** a finding.

*Light in fibre covers roughly 200 km per millisecond, and the route is not a straight line.*

---

<!-- _class: demo -->

## Part 6 — take it all down, and prove it

```bash
./05-teardown.sh
./06-verify-clean.sh
```

The `TODO` in `06-verify-clean.sh`: check for the **three resource classes that survive a deleted VM**. `operations/cost-model.md` §6 says where to look.

**The verification output is what is graded.** "No errors" is not evidence.

<!--
BEFORE ANYONE LEAVES: every student shows you clean verification output. Do not let a room of running instances go home for the weekend — the cheapest intervention in the cost model.
Check the billing report at the start of week 6. Anyone over $1 has left something running.
-->

---

## This week's work — 180 minutes

| | |
|---|---|
| Read the notes | 25 min |
| Lab 2 Parts 3–6 and the write-up, including teardown verification | 155 min |

**Lab 2 is due at the end of this week.** Check the billing report the day after teardown too — usage takes time to appear.

---

<!-- _class: lead -->

# Next week

Storage abstractions — block, file, object, database

**Quiz 3** · **Lab 3 starts** — your application's state leaves the machine
