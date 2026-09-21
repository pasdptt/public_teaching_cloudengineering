# Week 2 — Processes, isolation, virtualization, containers

**Quiz 1 this week**, on week 1's material. **Lab 1 starts.**

---

## Start with the process

A **process** is a running program plus everything the operating system gives it: its own
view of memory, a set of open files, an identity, and a number — the process id.

The important word is *own*. Two processes on the same machine cannot read each other's
memory. That is not politeness; the hardware and the kernel enforce it. Process isolation is
the oldest and most reliable boundary in computing, and every fancier boundary in this
course is built on the same idea: **give each tenant its own view of something they think is
the whole world.**

Run the course application and look at it as a process:

```bash
cd application
python3 -m docapp
# in another terminal
ps aux | grep docapp
```

One process. It holds an open socket on port 8080, some memory containing your job records,
and a working directory where it writes documents.

## What a port actually is

You will type `:8080` a hundred times this semester. It is worth thirty seconds on what it
means.

A machine has an IP address. Many programs on that machine may want to talk to the network at
once, so the address is not enough — you need to say *which program*. A **port** is a
16-bit number that does that. The operating system lets one process at a time listen on a
given port, which is why starting a second copy of the application gives you
`Address already in use`.

The address you bind to also matters, and this trips up everyone once:

- `127.0.0.1` — the loopback address. Only this machine can reach you. This is the
  application's default, deliberately.
- `0.0.0.0` — every network interface this machine has. On your laptop behind a router, mostly
  harmless. On a cloud VM with a public IP address, you have just published your service to
  the internet.

Lab 1 asks you about this. Lab 2 makes it real.

## HTTP in five minutes

Everything in this course talks HTTP. You need four things.

**A request** is a method, a path, some headers, and optionally a body:

```text
POST /jobs HTTP/1.1
Host: 127.0.0.1:8080
Content-Type: application/json
Idempotency-Key: my-first-job

{"document_id": "doc_abc", "operation": "wordcount"}
```

**A response** is a status code, headers, and a body:

```text
HTTP/1.1 201 Created
Content-Type: application/json
X-Request-Id: req_9f2c

{"id": "job_123", "status": "succeeded", ...}
```

**Methods carry meaning.** `GET` reads and should change nothing. `POST` creates. `DELETE`
removes. This matters more than it looks: something that changes nothing can be safely
retried, and in a network where responses go missing, "safe to retry" is an enormously
valuable property.

**Status codes are grouped.** `2xx` worked, `3xx` look elsewhere, `4xx` you made a mistake,
`5xx` I made a mistake. The `4xx`/`5xx` split is a statement about *whose fault it is*, and
you will use it to decide whether retrying could possibly help. Retrying a `400` will never
work. Retrying a `503` very well might.

Watch it happen with `curl -i`, which prints the response headers:

```bash
curl -i http://127.0.0.1:8080/healthz
```

Notice `X-Request-Id` coming back. Every log line the server wrote while handling your
request carries that same id. That is how you trace a request, and it is the same idea as a
distributed trace, minus the tooling.

## Virtual machines: fooling an operating system

A **hypervisor** is software that presents virtual hardware to an operating system. The
guest OS believes it has a processor, memory, and disks. It does not; it has a slice of
something bigger, and the hypervisor arbitrates.

What you get: very strong isolation, because the boundary is at the hardware interface and
each guest runs its own kernel. What you pay: each VM carries an entire operating system —
gigabytes of disk, a boot sequence measured in tens of seconds, and its own patching.

This is IaaS from week 1. Lab 2 deploys onto one.

## Containers: fooling a process

A container starts from a different question. If processes are already isolated from each
other's memory, what else would a process need before it believed it was alone on the
machine?

Mostly three things:

- **Its own view of the filesystem.** It should see its own `/` — not the host's.
- **Its own view of the process table.** It should see itself as PID 1 and not see the
  host's other processes.
- **Its own view of the network**, and a limit on how much CPU and memory it can take.

Linux provides exactly these as **namespaces** (its own view of things) and **cgroups**
(limits on how much it can consume). A container is a normal process with a set of
namespaces and cgroups wrapped around it.

The consequence is the thing to remember:

> **A container does not have its own kernel. It shares the host's.**

A VM boots an operating system. A container is a process that has been lied to about its
surroundings. That is why containers start in milliseconds and VMs in tens of seconds — and
why the isolation is weaker, because there is one shared kernel and a kernel bug is a shared
problem.

You will confirm the shared kernel yourself in Lab 1, with one command run in two places.

## Images and layers

A container **image** is a filesystem plus some metadata, built in **layers**. Each
instruction in a `Dockerfile` produces a layer, layers are cached, and layers are shared
between images that start the same way.

Two practical consequences that show up in Lab 4:

- **Order your Dockerfile from least to most frequently changing.** Dependencies before
  source code. Change a line of source and only the last layers rebuild.
- **Layers accumulate.** Every rebuild pushes new ones. Artifact Registry's free allowance is
  0.5 GiB, so "delete old images" is not housekeeping advice, it is how the lab stays free.

Look at `application/Dockerfile`. It is short and every line has a comment saying why.

## Choosing between them

| | Virtual machine | Container | Managed execution |
|---|---|---|---|
| Boundary | Virtual hardware; own kernel | Namespaces; shared kernel | Provider's, mostly invisible |
| Starts in | Tens of seconds | Milliseconds | Milliseconds to seconds (cold start) |
| You operate | Guest OS and up | The image and up | Your code and up |
| Isolation | Strongest | Good; shared-kernel risk | Provider's problem, and their promise |
| Fits | Existing systems, full OS control | Portable deployment units | Request-shaped workloads |

Being able to argue this table is CLO-2, and you will be asked to do it with *measurements*
in Lab 4 rather than from memory.

## This week's work (~180 minutes)

| | |
|---|---|
| Read these notes; prepare for Quiz 1 | 30 min |
| Lab 1 Parts 1 and 2 (trace a request; find the process boundary) | 150 min |

Quiz 1 is in class and covers **week 1** only. The reading above is the preparation; there is
no separate revision session in the budget, by design.

## Check yourself

1. Two processes on one machine. Can one read the other's memory? What stops it?
2. You start the application twice on port 8080. What happens, and why?
3. Explain `127.0.0.1` versus `0.0.0.0` to someone about to deploy on a public cloud VM.
4. Which status code class means "retrying might help", and which means it never will?
5. A container shows `/` with a handful of directories and itself as PID 1. Does it have its
   own kernel? How would you check with one command?
6. Why does a container start so much faster than a VM?
7. Why put `COPY requirements.txt` before `COPY docapp/` in a Dockerfile?

## Next week

What changes when a call crosses a machine boundary — latency, partial failure, and why
"slow" and "dead" look identical from the outside. Lab 1 is completed and submitted.
