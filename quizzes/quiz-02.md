# Quiz 2 — Processes, isolation and state

**Covers weeks 1–3.** Taken in week 4, in the discussion block — before the cloud material
taught in that session, none of which is assessed here. Outcomes: CLO-1, CLO-2, CLO-3
(introductory).

**12 marks · about 12 minutes · closed book · individual.** Short answers are fine. You are
marked on reasoning; a correct conclusion with no reason earns little.

---

## Question 1 — The lightweight-VM myth (3 marks)

A classmate explains:

> "A container is just a lightweight virtual machine. It has its own small kernel, which is
> why it starts in milliseconds instead of tens of seconds."

1. What is wrong with this explanation? Say what a container actually is.
2. Describe **one** observation from Lab 1 that supports your answer, and say *how* it
   supports it.
3. Give **one** consequence of your answer for isolation between containers on the same
   host.

## Question 2 — What survives? (3 marks)

The course application runs **inside a container with no volume attached**. Documents are
written to a directory inside the container; job records are held in the process's memory.
A user uploads one document and submits one job.

Copy the table and fill in each cell with **survives** or **lost**:

| Event | Document | Job record |
|---|---|---|
| (i) The container is deleted and a new one is started from the same image | | |
| (ii) The same application runs directly on a laptop, *not* in a container, and its process is stopped and started again | | |

Then, in one or two sentences: in which of the four cells did the data *feel* durable while
not actually being durable, and why is that the more dangerous case?

## Question 3 — "It works on my machine" (3 marks)

A student starts the course application on a cloud VM with its default settings. From a
terminal **on the VM**, `curl http://127.0.0.1:8080/healthz` succeeds. From a teammate's
laptop, a request to the VM's public address fails — and the application's log shows **no
line at all** for the teammate's request.

1. What does the *absence* of a log line tell you about where the request stopped?
2. Name the most likely cause, given the application's defaults.
3. Name the **one** check that would confirm it.

## Question 4 — The request that never answered (3 marks)

A client sends `POST /jobs` to submit a job. After its timeout expires it has received no
response.

1. The client can retry, or not retry. State the risk of **each** option.
2. What property of the operation makes retrying safe, and what exactly must the client do
   on the retry for the course application to provide it?
