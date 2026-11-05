---
marp: true
theme: cloudcourse
paginate: true
footer: 'Week 1 · What makes a cloud'
---

<!--
Deck for week 1. Derived from weeks/week-01/teaching-guide.md — that file is authoritative
for the teaching; this is what goes on the wall.

Presenter notes carry only what you need while standing up: the commands to type, the timing
marker, and which guide section to glance at. Everything else is in the guide.

Render:  bash course/slides/render.sh 01
-->

<!-- _class: lead -->

# What makes a cloud

## Week 1

Cloud Computing: Principles and Practice

<!--
TIMING: 180 min total — 85 concepts · 25 discussion · 60 practical · 10 break.
Guide: weeks/week-01/teaching-guide.md
Before you start: have the env-check command ready in a terminal, and the running order
of the practical block in mind. No assessment this week; Quiz 1 next week covers it.
-->

---

<!-- _class: block -->

<span class="min">5 minutes</span><span class="clock">0:00 – 0:05</span>

# Opening

What this course is, and is not

---

## This course in one sentence

You will build **one application**, all semester.

It starts as a Python program on your laptop.

By week 12 it is deployed, scaled, asynchronous, reproducible from code — and you will have **measured it at each step**.

> The test is not that you can deploy something. It is that when a deployment behaves strangely, you can say **why**.

---

## What it is not

- Not certification preparation — we do not memorise product names
- Not a Kubernetes administration course
- Not a course where **"it worked"** is the goal

Explanation and evidence carry **more marks** than a working deployment.

*Lab rubric: implementation 35 · explanation and evidence 40.*

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:05 – 0:20</span>

# The problem that made clouds

Before the definition

---

## It is 2003. You want to launch a website.

You estimate your peak. You buy enough servers for it. You wait weeks for delivery.

Three things follow:

1. You pay for the peak **all the time** — Black Friday capacity sits idle in February
2. Being wrong is expensive **in both directions**
3. The lead time is weeks — an idea you cannot test for six weeks is one you do not test

---

<!-- _class: ask -->

## Who has the most idle capacity in the world?

<!--
Let them get there. Amazon's fleet sized for December; Google's for whatever the web throws
at it. Do not answer it yourself.
Guide: "Open with the problem, not the definition"
-->

---

## Statistical multiplexing

Two shops. Each needs **100 servers** at peak.

| | Peak hour | Servers needed |
|---|---|---|
| Shop A | 9am in Bangkok | 100 |
| Shop B | 9am in São Paulo | 100 |
| **Separately** | | **200** |
| **Shared pool** | peaks do not coincide | **~110** |

Independent peaks do not happen at the same time.

<!--
Put this arithmetic on the board as you say it. Students remember arithmetic they watched
happen. This is the economic engine under everything else in the course.
-->

---

<!-- _class: punch -->

## Everything that follows — the APIs, the elasticity, the pricing —
## is machinery for selling access to a shared pool.

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">0:20 – 0:40</span>

# Five characteristics

Each one is a claim. Each claim has a consequence.

---

## On-demand self-service

You can get a server **without asking a human**.

**Consequence:** infrastructure can be created by a script — which is why Lab 6 exists.

And why *"I created it by clicking around and now I can't remember how"* is a real failure.

---

## Broad network access

Capacity is reached over a network, by standard mechanisms.

**Consequence:** the network is now **part of your application**.

Lab 2 is about tracing it.

---

## Resource pooling

Many customers share the same physical hardware.

You do not know which machine you are on. That is the deal.

**Consequence:** your "virtual machine" is a slice of something larger — week 2.

---

## Rapid elasticity

Capacity grows and shrinks quickly, and can **appear** unlimited.

Note *appear*.

- It is not unlimited
- It takes real time to arrive
- The delay between "we need more" and "more has arrived" causes a surprising amount of misbehaviour — week 9

---

## Measured service

Usage is metered, and therefore billed.

This is the one students underestimate.

It gets its own block.

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:40 – 0:55</span>

# Metering, properly

Provisioned ≠ used

---

<!-- _class: punch cost -->

## A resource that is provisioned is metered —
## whether or not anyone is using it.

---

<!-- _class: cost -->

## An external IP address

| Situation | Rate | Over 30 days |
|---|---|---|
| Attached to a **running** VM | $0.005/hour | ~$3.60 |
| **Reserved, attached to nothing** | **$0.01/hour** | **~$7.20** |

<!--
Verified rates — operations/cost-model.md §2, references.md R-09.
-->

---

<!-- _class: ask -->

## Why would a provider charge *more*
## for the one doing nothing?

<!--
Addresses are genuinely scarce. The price is a signal. Let them reason to it.
-->

---

<!-- _class: cost -->

## The lesson that pays for itself

> **The resources that cost you money are the ones you forgot about, not the ones you are using.**

This is why every lab in this course ends with a teardown step.

And why **the teardown is worth marks**.

---

<!-- _class: block -->

<span class="min">Break — 10 minutes</span><span class="clock">0:55 – 1:05</span>

# Break

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">1:05 – 1:20</span>

# Service models

Who operates what

---

## The stack

From the bottom up:

```text
  who may touch it
  your data
  your application
  runtime
  operating system
  hypervisor
  hardware
  building and power
```

The acronyms matter less than the question underneath them.

---

<!-- _class: ask -->

## Which parts of this stack do I operate,
## and which does someone else operate?

---

## Four models, one question

| Model | Provider operates up to | You supply | Lab |
|---|---|---|---|
| **IaaS** | the hypervisor | an OS and everything above | Lab 2 |
| **Container / PaaS** | the OS and scheduler | an image and a port | Lab 4 |
| **Serverless** | everything up to your code | a function | — |
| **SaaS** | everything | data and configuration | — |

---

<!-- _class: punch -->

## Moving up the list, you operate less
## **and** you control less.
## Always both.

<!--
Ask for a case where you hand over the work and keep the control. There isn't one. That
absence is the whole trade-off, and a lot of bad architecture comes from people who believed
otherwise.
-->

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">1:20 – 1:35</span>

# Shared responsibility

The most practically important idea this week

---

## The rule

> The provider is responsible for the security **of** the cloud.
>
> You are responsible for security **in** the cloud.

At IaaS level — provider: datacentre, hardware, hypervisor, availability as described.

You: OS patches, firewall rules, access policies, your application, **your data**.

The line **moves** as you move up the service models.

---

## Three cases

**1. A bucket of confidential files was readable by anyone on the internet.**

→ Yours. The provider gave you a permissions system; you configured it to allow that.

This is the most common cloud data breach and it is never the provider's fault.

---

## Three cases

**2. A whole datacentre lost power; services in that zone stopped.**

→ The provider's responsibility for **the outage**.

→ Yours if your design assumed one zone would never fail.

**Both are true at once.** Holding both is the actual skill.

<!--
Spend time here. Students want a single answer and there isn't one. Comes back in week 11.
-->

---

## Three cases

**3. An unpatched OS vulnerability on your VM was exploited.**

→ Yours on IaaS.

→ Theirs on a managed runtime where the provider maintains it.

> The same incident lands on different sides of the line **depending on a choice you made earlier.**

The service model you pick decides what you are on the hook for.

---

<!-- _class: block -->

<span class="min">25 minutes</span><span class="clock">1:35 – 2:00</span>

# Discussion

Attribute the incident

---

<!-- _class: ask -->

## Four incidents.
## Who is responsible, and why?

Small groups · 5 minutes each · then the whole room

---

## The four

1. A storage bucket with confidential files was readable by anyone on the internet.

2. A zone lost power; every service in it stopped for four hours.

3. A guest OS vulnerability on a VM was exploited **three weeks after the patch was published**.

4. A managed database was unreachable for 20 minutes during a maintenance window **announced a month in advance**, and the customer's application had **no retry logic**.

<!--
Expected: (1) customer, unambiguously. (2) both, in different senses. (3) customer on IaaS,
provider on a managed runtime — the same incident moves. (4) the trap: outage is the
provider's, the IMPACT is the customer's — the announcement and the missing retry were both
theirs.
Number 4 is the best one. Leave time for it.
Guide: "Discussion exercise (25 min)"
-->

---

<!-- _class: block -->

<span class="min">60 minutes</span><span class="clock">2:00 – 3:00</span>

# Practical

The environment check

---

<!-- _class: demo -->

## Run this now

```bash
python3 operations/check_environment.py
```

It installs nothing, changes nothing, and contacts **no cloud service**.

- **PASS** — good
- **WARN** — nothing is blocking you; read before Lab 1
- **FAIL** — bring the output to me. Do not spend an evening on it alone.

<!--
THIS IS THE PURPOSE OF THE WEEK. The planning assumption is that students have machines they
can install on. This block turns that assumption into evidence while there is time to act.
Circulate. Expect, in order: Python not on PATH (Windows); no container runtime (a WARN);
pip3 externally-managed (venv); campus network blocking HTTPS (a WARN — note who).
RECORD WHO FAILED WHAT. More than two without containers → D-10 needs revisiting.
-->

---

<!-- _class: demo -->

## Then run the application

```bash
cd application
python3 -m docapp
```

```bash
curl http://127.0.0.1:8080/healthz
```

Nothing to install. No virtual environment. No `pip install`.

*`application/README.md` says why that was a deliberate choice.*

---

<!-- _class: cost -->

## Two things before you go

**1. Do not activate a cloud trial before week 4.**

Ninety days has to reach week 15. Every day spent early is a day off the end.

**2. If you expect a problem** — eligibility, payment method, or you have used the trial before — **tell me this week.**

There is a documented local path. You are not disadvantaged in grading.

<!--
Ask #2 openly, as ordinary logistics, in the same breath as asking about laptops — so that
saying "that's me" costs nothing socially. Handling it now is the difference between a
supported path and a student quietly falling behind in week 4.
Expect at least one student to have signed up already. Note them and plan for an early expiry.
-->

---

## This week's work — 180 minutes

| | |
|---|---|
| Read NIST SP 800-145 (three pages) | 30 min |
| Environment check, and fix what it reports | 30 min |
| Run the application, try each endpoint | 60 min |
| Read the syllabus, including the cost section | 30 min |
| Skim the Lab 1 brief | 30 min |

Nothing is graded this week.

---

<!-- _class: lead -->

# Next week

Processes, isolation, virtualization, containers

**Quiz 1** — on this week's material

**Lab 1 starts**
