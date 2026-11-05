---
marp: true
theme: cloudcourse
paginate: true
footer: 'Week 2 · Processes, isolation, containers'
---

<!--
Deck for week 2. Derived from weeks/week-02/teaching-guide.md, which is authoritative.
Two live demos carry this session and both must be rehearsed ON THE LAPTOP YOU PRESENT FROM.

Render:  bash course/slides/render.sh 02
-->

<!-- _class: lead -->

# Processes, isolation, containers

## Week 2

Quiz 1 today · Lab 1 starts

<!--
TIMING: 180 min — 85 concepts · 15 quiz · 10 discussion · 60 practical · 10 break.
Guide: weeks/week-02/teaching-guide.md
REHEARSE DEMO 2 BEFORE THE SESSION. On macOS/Windows the host kernel line does NOT match,
and you need to be ready to explain why rather than look surprised.
-->

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:00 – 0:15</span>

# Start with the process

---

## What a process is

A running program, plus what the OS gives it:

- its own view of **memory**
- a set of **open files**
- an **identity**
- a **number** — the process id

The important word is *own*.

---

## Isolation is the base case

Two processes on one machine **cannot read each other's memory**.

That is not politeness. The hardware and the kernel enforce it.

> Every fancier boundary in this course is built on the same idea:
>
> **give each tenant its own view of something they think is the whole world.**

---

<!-- _class: demo -->

## Look at it as a process

```bash
cd application
python3 -m docapp
```

```bash
ps aux | grep docapp
```

One process. One open socket on port 8080. Some memory holding your job records. A working directory where it writes documents.

---

<!-- _class: block -->

<span class="min">10 minutes</span><span class="clock">0:15 – 0:25</span>

# Ports and binding

---

## What a port is

A machine has an IP address. Many programs want the network at once.

A **port** is a 16-bit number that says *which program*.

The OS lets **one process at a time** listen on a given port.

---

<!-- _class: demo -->

## Demo 1 — one port, two servers

```bash
python3 -m docapp          # terminal 1
python3 -m docapp          # terminal 2  →  Address already in use
```

```bash
PORT=8081 python3 -m docapp    # and now both run
```

<!--
Thirty seconds. Ask: why does the OS bother to prevent this? Then the port abstraction is
concrete rather than a number they type.
-->

---

## The address you bind to

| | Means | On your laptop | On a cloud VM |
|---|---|---|---|
| `127.0.0.1` | this machine only | safe default | unreachable |
| `0.0.0.0` | **every** interface | mostly harmless | **published to the internet** |

Lab 1 asks you about this. Lab 2 makes it real.

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">0:25 – 0:45</span>

# HTTP, in five minutes

---

## A request

```text
POST /jobs HTTP/1.1
Host: 127.0.0.1:8080
Content-Type: application/json
Idempotency-Key: my-first-job

{"document_id": "doc_abc", "operation": "wordcount"}
```

A method · a path · headers · optionally a body.

---

## A response

```text
HTTP/1.1 201 Created
Content-Type: application/json
X-Request-Id: req_9f2c

{"id": "job_123", "status": "succeeded", ...}
```

A status code · headers · a body.

---

## Methods carry meaning

- `GET` reads, and should change nothing
- `POST` creates
- `DELETE` removes

**Something that changes nothing is safe to retry.**

In a network where responses go missing, "safe to retry" is enormously valuable. Hold onto that — week 3.

---

## Status codes are grouped

| | |
|---|---|
| `2xx` | it worked |
| `3xx` | look elsewhere |
| `4xx` | **you** made a mistake |
| `5xx` | **I** made a mistake |

---

<!-- _class: punch -->

## The status class tells you
## whether retrying could possibly help.

<!--
Anyone can memorise "4xx is client error". THIS is the thing worth teaching. Retrying a 400
is pointless forever; retrying a 503 is often correct. Plant it now — week 10 is built on it.
-->

---

<!-- _class: demo -->

## Watch it, and trace it

```bash
curl -i http://127.0.0.1:8080/healthz
```

```bash
curl -i -H 'X-Request-Id: demo-1' http://127.0.0.1:8080/healthz
```

Every log line the server wrote while handling that request carries `demo-1`.

That is how you trace a request — the same idea as a distributed trace, minus the tooling.

<!--
Show the round trip live, then grep the server log for demo-1. This is the mechanism Lab 1
Part 1 asks them to use.
-->

---

<!-- _class: block -->

<span class="min">Break — 10 minutes</span><span class="clock">0:45 – 0:55</span>

# Break

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:55 – 1:10</span>

# Virtual machines

Fooling an operating system

---

## The hypervisor

Software that presents **virtual hardware** to an operating system.

The guest OS believes it has a processor, memory and disks. It does not — it has a slice of something bigger, and the hypervisor arbitrates.

---

## What you get, what you pay

**Get:** very strong isolation. The boundary is at the hardware interface, and each guest runs **its own kernel**.

**Pay:** an entire operating system per VM — gigabytes of disk, a boot measured in tens of seconds, and its own patching.

This is IaaS from last week. Lab 2 deploys onto one.

---

<!-- _class: block -->

<span class="min">25 minutes</span><span class="clock">1:10 – 1:35</span>

# Containers

Fooling a process

---

<!-- _class: ask -->

## Processes are already isolated in memory.
## What else would a process need
## before it believed it was alone on the machine?

<!--
Let the room generate the list: its own files, its own process table, its own network, a cap
on resources. THEN name them. Students who derive the list remember it; students who are
given it do not.
-->

---

## Namespaces and cgroups

A container is a normal process with:

- **namespaces** — its own view of the filesystem, the process table, the network
- **cgroups** — a limit on how much CPU and memory it can take

That is it. Linux provides exactly these.

---

<!-- _class: punch -->

## A container does not have its own kernel.
## It shares the host's.

---

<!-- _class: demo -->

## Demo 2 — the shared kernel

```bash
docker run --rm python:3.12-slim uname -r   # Debian-based
docker run --rm alpine uname -r             # a different distribution entirely
uname -r                                    # the host
```

Two "operating systems" — **one kernel between them**.

<!--
THE CENTREPIECE. Rehearse on the laptop you present from.
Linux host: all three match.
macOS / Windows (Docker Desktop): the host does NOT match — it prints Darwin or a Windows
version, the containers print Linux (often linuxkit/microsoft). SAY WHY OUT LOUD: Docker
Desktop runs containers inside a small Linux VM, and the shared kernel is THAT VM's.
This is not a failed demo — it shows both of today's boundaries at once, and half the room
will see exactly this in Lab 1.
-->

---

<!-- _class: ask -->

## Before I run this —
## will the process ids match?

```bash
docker run --rm python:3.12-slim python3 -c \
  "import os; print(sorted(int(p) for p in os.listdir('/proc') if p.isdigit()))"
```

<!--
Take a show of hands FIRST. The split is the teaching moment and it disappears the instant
the output is on screen. Two or three PIDs inside; hundreds outside; same program, two ids.
-->

---

## Why the speed difference

A VM **boots an operating system**.

A container is **a process that has been lied to** about its surroundings.

Milliseconds versus tens of seconds — and weaker isolation, because there is one shared kernel and a kernel bug is a shared problem.

---

## Images and layers

An image is a filesystem plus metadata, built in **layers**. Each Dockerfile instruction makes one. Layers are cached and shared.

Two consequences, both arriving in Lab 4:

1. **Order from least to most frequently changing.** Dependencies before source code.
2. **Layers accumulate.** Artifact Registry's free allowance is **0.5 GiB**, so deleting old images is not housekeeping — it is how the lab stays free.

---

## Three ways to run code

| | VM | Container | Managed |
|---|---|---|---|
| Boundary | virtual hardware, own kernel | namespaces, **shared** kernel | provider's |
| Starts in | tens of seconds | milliseconds | ms–seconds (cold start) |
| You operate | guest OS and up | the image and up | your code and up |
| Isolation | strongest | good; shared-kernel risk | their promise |

You will argue this table **with measurements** in Lab 4.

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">1:35 – 1:50</span>

# Quiz 1

Week 1 material

<!--
Scenario-based: attribute an incident, correct a statement about elasticity or metering,
place a workload on the service-model spectrum. No service names, no pricing trivia, no
console menus. Hand back next week; budget 30–45 min to mark ten.
-->

---

<!-- _class: block -->

<span class="min">10 minutes</span><span class="clock">1:50 – 2:00</span>

# Lab 1 predictions

Hands up, before anyone runs anything

---

<!-- _class: ask -->

## As concurrency goes up,
## does median latency rise, fall, or stay flat?

Write your answer down **now**.

<!--
TAKE A SHOW OF HANDS. Most rooms split; most students predict latency rises. It does not at
these levels — the simulated work is a sleep, and sleeping threads do not contend.
DO NOT RESOLVE IT. They find out in Part 5; revisit in week 9 when a real resource saturates.
Make sure the predictions are written down before they leave — rubric band B1 awards marks
for committing, and the point evaporates if it is written after the result.
-->

---

<!-- _class: block -->

<span class="min">60 minutes</span><span class="clock">2:00 – 3:00</span>

# Practical

Lab 1, Parts 1–2

---

<!-- _class: demo -->

## Part 1 — trace one request

```bash
DOCAPP_LOG_LEVEL=debug python3 -m docapp
```

```bash
curl -i -X POST http://127.0.0.1:8080/documents \
     -H 'Content-Type: text/plain' \
     -H 'X-Document-Name: intro.txt' \
     -H 'X-Request-Id: trace-me-1' \
     --data-binary @samples/cloud-intro.txt
```

**Checkpoint:** `trace-me-1` echoed in the headers, and on two server log lines.

---

<!-- _class: demo -->

## Part 2 — find the boundary

```bash
docker build -t docapp:lab1 .
docker run --rm --name docapp-lab1 -p 8080:8080 docapp:lab1
```

```bash
docker exec docapp-lab1 python3 -c \
  "import os; print(sorted(int(p) for p in os.listdir('/proc') if p.isdigit()))"
```

<!--
Expect, in order of frequency: PowerShell aliasing curl to Invoke-WebRequest (announce it
BEFORE anyone hits it); container runtime installed but not started; port 8080 still held by
an earlier run; Apple Silicon image pulls (fine this week — flag that Lab 4 will care).
Students with no working runtime: get them through Part 1, fix setup before week 3. Lab 1 is
due at the end of week 3 and Part 2 needs a container.
-->

---

## This week's work — 180 minutes

| | |
|---|---|
| Read the week 2 notes; prepare for Quiz 1 | 30 min |
| Lab 1 Parts 1 and 2 | 150 min |

Quiz 1 covers **week 1** only. The reading *is* the preparation — there is no separate revision session in the budget, by design.

---

<!-- _class: lead -->

# Next week

What changes when a call crosses a machine boundary

Latency · partial failure · why slow and dead look identical

**Lab 1 is due at the end of next week**
