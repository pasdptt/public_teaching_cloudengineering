# Week 2 — Teaching guide: Processes, isolation, virtualization, containers

| | |
|---|---|
| **Outcomes** | CLO-1, CLO-2 |
| **Assessment** | **Quiz 1** (covers week 1 only), in the discussion block |
| **Practical** | Lab 1 Parts 1–2 |
| **Prep time** | ~4 h first delivery (the demos need rehearsing), ~1.5 h subsequently |

## Session objectives

1. Define a process in terms of what the OS gives it, and name what isolates two processes.
2. Explain a port, and the practical difference between binding `127.0.0.1` and `0.0.0.0`.
3. Read an HTTP request and response, and say what each status class implies about retrying.
4. Explain virtualization as presenting virtual hardware to a guest OS.
5. Explain a container as a process with namespaces and cgroups, **sharing the host kernel**,
   and support that with an observation.
6. Compare the three execution models on isolation, start-up, control and responsibility.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| Processes | 15 | What the OS gives a process. Isolation as the base case. |
| Ports and binding | 10 | Live demo: two servers, one port. Then loopback vs all-interfaces. |
| HTTP | 20 | Live `curl -i`. Methods, status classes, headers. Request-id tracing. |
| Break | 10 | |
| Virtualization | 15 | Hypervisor, guest OS, the cost of a whole OS per tenant |
| Containers | 25 | Namespaces and cgroups. **The shared-kernel demo.** Images and layers. |
| **Quiz 1** | 15 | Covers week 1 |
| Discussion | 10 | Lab 1 prediction questions, hands up, before anyone runs anything |
| Practical | 60 | Lab 1 Parts 1–2 |

**180 minutes exactly.** 85 concepts · 15 quiz · 10 discussion · 60 practical, plus the break.

---

## Teaching notes

### Two demos carry this session

**Demo 1 — one port, two servers.** Start the application, then start it again in another
terminal. `Address already in use`. Ask *why the OS bothers to prevent this*. Then
`PORT=8081` and both run. Thirty seconds, and the port abstraction is now concrete.

**Demo 2 — the shared kernel.** This is the session's centrepiece and it must be rehearsed.

```bash
uname -r                                  # on the host
docker run --rm python:3.12-slim uname -r # inside a container
```

Same kernel version. Then:

```bash
docker run --rm python:3.12-slim python3 -c \
  "import os; print(sorted(int(p) for p in os.listdir('/proc') if p.isdigit()))"
```

A list of two or three PIDs.

Ask the room, before running the second command: *will these match?* Take a show of hands.
The split is the teaching moment, and it disappears the instant the output is on screen.

**Caveat to state honestly:** on macOS and Windows, Docker runs a Linux VM, so `uname -r`
shows that VM's kernel and not the laptop's. Say so rather than letting a student discover
it and conclude the demo was wrong. It actually reinforces the point — on those machines
there is a VM *and* containers inside it, and the layers are doing different jobs.

### Frame containers as an answer, not a technology

Ask the question first: *processes are already isolated in memory — what else would a
process need before it believed it was alone on the machine?* Let the room generate the list:
its own files, its own process table, its own network, a cap on resources. Then name them:
namespaces and cgroups. Students who derive the list remember it; students who are given it
do not.

### HTTP: teach the retry consequence, not the vocabulary

Anyone can memorise that 4xx is client error. The thing worth teaching is: **the status class
tells you whether retrying could possibly help.** Retrying a 400 is pointless forever;
retrying a 503 is often correct. Plant that now — week 10 is built on it.

Show the request id round-trip live: send `-H 'X-Request-Id: demo-1'` and grep the server's
log output for `demo-1`. That is the mechanism Lab 1 Part 1 asks them to use.

---

## Quiz 1 (15 min, week 1 material)

Outcomes CLO-1 and CLO-2 (introductory). Student version in `quizzes/quiz-01.md`; key in the
private repository. Scenario-based: an incident to attribute across the responsibility
boundary, a statement about elasticity or metering to correct, a service-model placement.

**No service names, no pricing trivia, no console menus.**

Hand it back the following week. Ten students, short answers — budget 30–45 minutes to mark.

---

## Discussion: Lab 1 predictions (10 min)

Put the three prediction questions from `labs/lab-01/README.md` on screen. Take a **show of
hands** on question 3 — will median latency rise, fall, or stay flat as concurrency goes up?

Most rooms split. Most students predict latency rises. It does not, at these concurrency
levels, because the simulated work is a sleep and sleeping threads do not contend for
anything. Do **not** resolve it now. Let them find out in Part 5, and revisit it in week 9
when a real resource does saturate.

Make sure they write the predictions down before leaving. Band B1 of the rubric awards marks
for committing to an answer, and the whole point evaporates if the prediction is written
after the result is known.

---

## Common misconceptions

| Misconception | Surfaces as | Response |
|---|---|---|
| "A container is a lightweight VM" | Everywhere, all semester | Demo 2. Same kernel. |
| "Containers are secure because they're isolated" | In the comparison discussion | Isolated by the *shared* kernel. One kernel bug is everyone's bug. Stronger than nothing, weaker than a VM. |
| "The image contains an operating system" | Reasonable, and half-true | It contains a userland — libraries, binaries, files. No kernel. Ask what `FROM python:3.12-slim` actually ships. |
| "0.0.0.0 is just a shortcut for localhost" | Now, harmlessly; in Lab 2, expensively | It means *every* interface. On a VM with a public IP that is the internet. |
| "POST and GET are interchangeable" | When someone's curl works either way | Ask which one is safe to send twice. |
| "Layers are a Docker implementation detail" | When Dockerfile order is discussed | Layer order is a build-time and a *storage* decision. 0.5 GiB free allowance in Lab 4. |

---

## Practical block (60 min)

Lab 1 Parts 1 and 2. Expect:

- **Windows `curl` aliasing.** PowerShell's `curl` is `Invoke-WebRequest`. Announce it before
  anyone hits it; it is in the lab troubleshooting section and they will still hit it.
- **Container runtime not started.** Installed ≠ running. Docker Desktop must be open.
- **Port 8080 occupied** by an earlier run they forgot about.
- **Apple Silicon image pulls.** Fine this week. Flag that Lab 4 will care.

Students who still have no working container runtime: get them through Part 1, and get their
setup sorted before week 3. They cannot complete Part 2 without one, and Lab 1 is due at the
end of week 3.

## Links

- Student notes: `weeks/week-02/student-notes.md`
- Lab: `labs/lab-01/README.md` · Rubric: `labs/lab-01/rubric.md`
- Instructor solution and pilot data: private repo, `lab-solutions/lab-01/`
- Quiz key: private repo, `quiz-keys/quiz-01-key.md`
