# Lab 1 — Local foundations

**Weeks 2–3 · 7.5% of the final grade · Individual submission**

| | |
|---|---|
| **Cloud resources** | None. No account, no billing, no spend. **$0.00.** |
| **Outcomes** | CLO-2 (execution models), CLO-3 (tracing a request), CLO-5 (state and design) |
| **Estimated novice time** | ~2 h guided in class (2 × 60 min) + ~5 h independent over two weeks |
| **Observed pilot time** | *not yet measured — no pilot has been run* |

> The estimate above is a design estimate for a student meeting the stated prerequisites.
> It has not been validated by watching anyone do it. If it takes you dramatically longer,
> that is information the course wants — say so.

---

## Why this lab exists

Everything later in this course is a variation on one question: **when execution and state
are separated by a network, what changes?**

Before you can answer that in the cloud, you have to see it on one machine, where nothing is
hidden and nothing costs money. By the end of this lab you will have:

- followed a single request from `curl` to a log line to a stored file and back,
- watched the same program behave differently inside and outside a container, and understood
  which differences are isolation and which are configuration,
- deliberately destroyed some state and been unsurprised by which parts survived,
- and fixed it — by moving state somewhere that outlives the process.

That last step is the lab. The rest is the reason it matters.

## Prerequisites

- Week 1's environment check passing: `python3 operations/check_environment.py`
- A container runtime installed and running (see `operations/student-setup.md`)
- `pip3 install -r application/requirements-dev.txt` (pytest — nothing else)

## Preflight

```bash
cd application
python3 -m pytest -q            # expect: all tests pass
python3 -m pytest -m lab01 -q   # expect: all FAIL — that is your exercise
```

If the first command does not pass on a fresh clone, stop and ask. Something is wrong with
your setup, not with your understanding, and debugging it alone is not a good use of your
180 minutes.

---

## The system you are working with

```text
   curl  ──HTTP──▶  ┌──────────────── one OS process ────────────────┐
                    │                                                │
                    │   app.py       routing, status codes           │
                    │      │                                         │
                    │   service.py   what the application does       │
                    │      │                                         │
                    │      ├──▶ jobstore.py  ── job records ──▶  a Python dict
                    │      │                                    (dies with the process)
                    │      │
                    │      └──▶ storage.py   ── document bytes ─▶  ./data/documents/
                    │                                    (a directory on your disk)
                    └────────────────────────────────────────────────┘
```

In words, because a diagram is not an explanation: one process accepts HTTP requests. It
keeps document *bytes* in a directory on disk and job *records* in a dictionary in memory.
Both feel equally real while the process is running. Only one of them is.

The arrows are not the interesting part. The **boundary** is: everything inside the box
disappears when the process does, and everything outside it does not.

---

## Prediction — write this down before you run anything

Answer in your submission, **before** doing Part 3. You are marked on the quality of your
reasoning, not on being right. A confidently wrong prediction that you then explain is worth
more than a hedge.

1. You create a document and a job, then stop the server with Ctrl-C and start it again.
   Which of the two can you still retrieve? Why?
2. You run the application inside a container with no volume mounted, create a document,
   then delete the container and start a new one from the same image. Is the document there?
   Is this the same reason as question 1, or a different one?
3. `DOCAPP_PROCESSING_DELAY_MS=200`. You send 12 job requests one at a time, then 12 with
   four in flight at once. Predict the **total wall time** and the **median per-request
   latency** for each. Which of those two numbers do you expect to change, and which do you
   expect to stay roughly the same?

---

## Part 1 — Trace one request (~45 min)

Start the application and watch what it says about itself.

```bash
cd application
DOCAPP_LOG_LEVEL=debug python3 -m docapp
```

In a second terminal, send a request with a request id you choose:

```bash
curl -i -X POST http://127.0.0.1:8080/documents \
     -H 'Content-Type: text/plain' \
     -H 'X-Document-Name: intro.txt' \
     -H 'X-Request-Id: trace-me-1' \
     --data-binary @samples/cloud-intro.txt
```

**Checkpoint.** In the response headers you should see `X-Request-Id: trace-me-1` echoed
back, plus `X-Instance-Id`. In the server terminal you should see two JSON log lines both
carrying `"request_id": "trace-me-1"`.

Now follow the same request through the filesystem:

```bash
find data -type f | head
cat data/documents/<the id from the response>/metadata.json
```

**Record for your submission:** the full path a request takes, from the `curl` command to
the bytes on disk and back. Name each thing that touched it — the client, the socket, the
handler, the router, the service, the storage backend, the file. One short paragraph, or an
annotated list. Not a screenshot.

**Question to answer:** `X-Request-Id` is generated if you do not supply one. Why would a
system bother to accept one from the client instead of always generating its own?

## Part 2 — Find the process boundary (~60 min)

Run the same application inside a container. A `Dockerfile` is supplied in `application/`.

```bash
cd application
docker build -t docapp:lab1 .          # or: podman build -t docapp:lab1 .
docker run --rm --name docapp-lab1 -p 8080:8080 docapp:lab1
```

With it running, in another terminal:

```bash
curl -sS http://127.0.0.1:8080/stats
```

Then run these **inside** the container and **outside** it, and compare:

```bash
# What process ids exist inside the container?
# (the image is a slim one and has no `ps`, so we ask the kernel directly through /proc)
docker exec docapp-lab1 python3 -c \
  "import os; print(sorted(int(p) for p in os.listdir('/proc') if p.isdigit()))"

# What filesystem does it see?
docker exec docapp-lab1 ls /

# And on your own machine, for comparison:
ps aux | grep -c .        # roughly how many processes your laptop is running
ps aux | grep docapp      # the container's process, from the outside
```

**Checkpoint.** Inside, a very short list of process ids — probably two or three, with the
application at PID 1. Outside, hundreds of processes, including the container's, with an
entirely different PID.

That mismatch is the first hard evidence of the boundary: the *same running program* has two
different process ids depending on who is asking.

**Questions to answer:**

1. The application is PID 1 inside the container and something else entirely outside it.
   It is one process, and it has two ids. What is actually doing the renumbering, and is the
   container running its own operating system kernel? Say how what you observed supports
   your answer.
2. You published port 8080 with `-p 8080:8080`. What would happen if you omitted that flag,
   and *why* — in terms of the boundary, not the flag?
3. The application inside the container has `DOCAPP_HOST=0.0.0.0` set in the Dockerfile,
   while the default on your laptop is `127.0.0.1`. Explain why the container needs the
   different value. Then explain what `0.0.0.0` would mean on a machine with a public IP
   address — you will meet this again, for real, in Lab 2.

## Part 3 — Break it on purpose (~45 min)

Now test your predictions.

```bash
# with the application running locally (not in the container):
DOC=$(curl -sS -X POST http://127.0.0.1:8080/documents \
        -H 'Content-Type: text/plain' -H 'X-Document-Name: intro.txt' \
        --data-binary @samples/cloud-intro.txt)
DOC_ID=$(printf '%s' "$DOC" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

JOB=$(curl -sS -X POST http://127.0.0.1:8080/jobs \
        -H 'Content-Type: application/json' \
        -d "{\"document_id\":\"$DOC_ID\",\"operation\":\"wordcount\"}")
JOB_ID=$(printf '%s' "$JOB" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')
```

Confirm both exist. Then stop the server with Ctrl-C, start it again, and ask for both:

```bash
curl -i http://127.0.0.1:8080/documents/$DOC_ID
curl -i http://127.0.0.1:8080/jobs/$JOB_ID
```

**Checkpoint.** One returns `200`. One returns `404`.

**Record:** which, and the one-sentence reason. Then compare with your prediction and say
plainly whether you were right.

Now the container version. Run the container, create a document through it, stop and remove
the container, start a fresh one from the same image, and ask for the document again.

**Question:** the document vanished this time, even though it "was written to disk". Is that
the same failure as the job record disappearing, or a different one? Be precise — this
distinction is the difference between *state kept in memory* and *state kept on storage that
is itself disposable*, and it is the reason Lab 3 exists.

## Part 4 — Fix it (~2–3 h, the main exercise)

Implement `FileJobStore` in `application/docapp/jobstore.py` so that job records survive a
restart.

**The acceptance tests are the specification.** Read them first:

```bash
python3 -m pytest -m lab01 -q
```

They tell you, one test at a time, what your implementation has to be true of — including
the things that are easy to miss: that `get()` on a missing id raises `JobNotFound` rather
than returning `None`, that deleting a job releases its idempotency key, that twenty threads
writing at once lose nothing, and that a brand-new store on a missing file is simply empty
rather than an error.

The docstring on the class asks you four questions. **Answer them in your submission** —
they are worth more marks than the code:

1. When do you read the file, and when do you write it? What does your choice cost?
2. The server is threaded. What goes wrong if you ignore that?
3. What does the next start-up read if the process is killed mid-write? (Look at how
   `LocalStorage.put` in `storage.py` handles this.)
4. `MemoryJobStore` keeps a second dictionary for idempotency keys. Do you need one?

A few dozen lines is the right size. If you are writing more than that, re-read question 1.

**Checkpoint.** Both of these pass:

```bash
python3 -m pytest -m lab01 -q     # your exercise
python3 -m pytest -q              # nothing else broke
```

Then run the application for real with your store and confirm by hand what the tests claim:

```bash
DOCAPP_JOBSTORE=file python3 -m docapp
# create a job, Ctrl-C, start again, fetch the job — it should still be there
```

## Part 5 — The experiment (~45 min)

**Change one variable. Measure. Explain.**

```bash
# terminal 1
DOCAPP_JOBSTORE=file DOCAPP_PROCESSING_DELAY_MS=200 python3 -m docapp

# terminal 2
python3 tools/measure.py --url http://127.0.0.1:8080 --requests 12 --concurrency 1
python3 tools/measure.py --url http://127.0.0.1:8080 --requests 12 --concurrency 4
```

**Run each three times.** One run is one sample of a noisy system.

Then push further: try concurrency 8, 16, 32. Somewhere the numbers stop improving the way
they did at first.

**Record:** a small table of concurrency against wall time, throughput and p50/p95 latency,
with your machine and the delay setting stated.

**Explain, in about 150 words:**

1. Which number changed as concurrency rose, and which stayed roughly flat? Does that match
   your prediction from question 3?
2. Why does per-request latency stay near the configured delay while throughput climbs?
3. Where did throughput stop climbing, and what do you think limited it? You do not need to
   be certain — you need to name a candidate and say what you would measure to test it.
4. `measure.py --help` lists its own honest limitations. Name the one that most threatens
   *your* conclusion here, and say why.

Do not guess at numbers you did not observe. If a run failed, report that it failed.

---

## What to submit

One Markdown file, `lab01-<your-name>.md`, plus your modified `jobstore.py`. Keep it short —
the rubric rewards precision, not length.

1. **Predictions** (written before Part 3), unedited.
2. **Request trace** from Part 1, and your answer on client-supplied request ids.
3. **Process boundary** — your three answers from Part 2.
4. **What survived and what did not** — Part 3, both experiments, and whether your
   predictions held.
5. **Your FileJobStore**, plus your four design answers.
6. **The experiment** — your measurement table and your ~150-word explanation.
7. **Resource inventory and cleanup** (below).
8. **AI-assistance disclosure**, per the course policy.

Evidence means commands and their output, not screenshots. Measurements need units and
conditions. An experiment that did not work still earns full analysis credit when the
evidence is real and the reasoning is sound — **fabricated numbers earn zero**.

## Resource inventory and cleanup

This lab creates nothing that costs money, but the habit starts here, because from Lab 2
onwards it does.

| Resource | Where | How to remove |
|---|---|---|
| Document files | `application/data/` | `rm -rf application/data` |
| Job records file | `application/data/jobs/jobs.json` | removed with the above |
| Container image | local image store | `docker rmi docapp:lab1` |
| Stopped containers | local | `docker ps -a` then `docker rm <id>` |

**Cleanup verification** — include the output of these in your submission:

```bash
ls application/data 2>&1          # expect: No such file or directory
docker images | grep docapp       # expect: no output
docker ps -a | grep docapp        # expect: no output
```

Claiming cleanup is not the same as verifying it. From Lab 2 this distinction costs marks.

## Troubleshooting

**`Address already in use`** — something is already on port 8080, often a previous run.
Find it (`lsof -i :8080` on macOS/Linux, `netstat -ano | findstr :8080` on Windows) and stop
it, or run with `PORT=8081`.

**`Configuration error: ...`** — the application refused to start because an environment
variable cannot work. The message names the variable and what it will accept. This is
working as intended.

**`NotImplementedError: FileJobStore is your Lab 1 exercise`** — you set
`DOCAPP_JOBSTORE=file` before doing Part 4. Use `memory` until then.

**`pytest: command not found`** — use `python3 -m pytest`, which does not depend on your
PATH.

**`docker: Cannot connect to the Docker daemon`** — the engine is not running. Start Docker
Desktop (or Podman Desktop) and wait for it to report ready.

**`curl` on Windows PowerShell behaves oddly** — PowerShell aliases `curl` to
`Invoke-WebRequest`, which takes different arguments. Use `curl.exe` explicitly, or work in
WSL2. See `operations/student-setup.md`.

**Your `-m lab01` tests hang** — almost certainly the concurrency test, and almost certainly
a lock you take twice on the same thread. Look for a method holding the lock that calls
another method which also takes it.

**Something else** — post it in the class issue log before spending a second 30 minutes on
it. One person's solved problem is everyone's solved problem, and that is the only
scaling mechanism a course with no teaching assistant has.
