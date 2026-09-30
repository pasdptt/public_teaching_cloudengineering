# Quiz 3 — Networks, identity, and what outlives a machine

**Covers weeks 3–5**, including Lab 2. Taken in week 6, in the discussion block — the storage
material taught in that session is not assessed here. Outcomes: CLO-3, CLO-4 (introductory).

**12 marks · about 12 minutes · closed book · individual.** Short answers are fine. You are
marked on reasoning, not on product names.

---

## Question 1 — Read the symptom (4 marks)

The course application is on a VM with a public address. A firewall rule allows TCP 8080
**only from one source address**, and the application's listening address is set by
`DOCAPP_HOST`. For each case below, a request is sent from your laptop to the VM's public
address on port 8080.

| Case | Firewall rule | `DOCAPP_HOST` | Your laptop's address |
|---|---|---|---|
| (a) | allows your laptop's address | `127.0.0.1` | as allowed |
| (b) | **no rule exists** | `0.0.0.0` | — |
| (c) | allows the address you had yesterday | `0.0.0.0` | **changed overnight** |

For **each** case: predict the symptom you would see — *refused immediately*, *hangs then
times out*, or *succeeds* — and name the boundary that decided it. *(1 mark each)*

Then: for case (c), name the **one** check that would confirm your diagnosis. *(1 mark)*

## Question 2 — Who is this code? (3 marks)

An application on a VM runs as the default compute identity, which holds a broad
**Editor** role on the whole project. Nobody ever copied a credential onto the machine. An
attacker finds a bug that lets them run commands on the VM.

1. How does the attacker obtain a working cloud identity, given that there is no key file to
   steal?
2. What could they do with it that they could not do with a least-privilege identity?
3. The application reads and writes nothing in the cloud. Why does Lab 2 attach an identity
   with **one small role**, rather than no role at all?

## Question 3 — "I stopped it" (3 marks)

On Friday a student **stops** (does not delete) their Lab 2 VM, which has a **reserved static
address**, planning to delete it next week.

1. Name **two** things that keep billing over the weekend, and for each say why it is a
   separate resource from the VM rather than part of it.
2. Next week they delete everything and the teardown script prints no errors. What would
   count as **evidence** that nothing billable remains, and why is the clean exit not enough?

## Question 4 — Two complaints, two causes (2 marks)

A service runs in **one zone** of a US region and serves users in Bangkok. Users make two
complaints:

- **(i)** Every request is roughly 200 ms slower than for a colleague in the US.
- **(ii)** Last month the service was completely down for an hour when that zone had a power
  problem.

For each: which property of regions and zones explains it, and could a design change **inside
the same region** remove it?
