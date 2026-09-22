# docapp — the course application

A small document/job-processing service. You submit a text document, ask for an operation
on it, and read the result back.

This one application is the substrate for the whole course. It starts here as a local
Python program and acquires cloud behaviour one lab at a time. You will not be asked to
build a different application in week 10.

---

## Run it

```bash
cd application
python3 -m docapp
```

No installation step. No virtual environment required. No `pip install`.

In another terminal:

```bash
curl http://127.0.0.1:8080/healthz
```

To try the whole flow:

```bash
# store a document
DOC=$(curl -sS -X POST http://127.0.0.1:8080/documents \
        -H 'Content-Type: text/plain' \
        -H 'X-Document-Name: sample.txt' \
        --data-binary @samples/cloud-intro.txt)
echo "$DOC"

# pull the id out of that response, then ask for some work
DOC_ID=$(printf '%s' "$DOC" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

curl -sS -X POST http://127.0.0.1:8080/jobs \
     -H 'Content-Type: application/json' \
     -H 'Idempotency-Key: my-first-job' \
     -d "{\"document_id\":\"$DOC_ID\",\"operation\":\"wordcount\"}"
```

Send that last request a second time, unchanged. Look at the HTTP status code and at
`deduplicated` in the body. That is not a trick — it is the first thing this application
is trying to teach you.

## Why there are no dependencies

The application uses only the Python standard library. That is a deliberate choice with
four reasons behind it, and it is worth knowing them because you will make this trade-off
yourself one day:

1. **Nothing to install is nothing to go wrong.** One instructor, no teaching assistant,
   ten laptops in two operating systems. Every dependency is a support request waiting for
   week 1.
2. **The mechanism stays visible.** Week 2 teaches HTTP just-in-time. You can open
   `docapp/app.py` and see the method, the path, the headers and the status code. A
   framework would be more comfortable and would hide precisely the thing being taught.
3. **The container image stays small.** In Lab 4 this is built into an image and pushed to
   Artifact Registry, whose free allowance is 0.5 GiB. No `pip install` means a small
   image, a fast build, fewer build minutes, and a lab that stays free.
4. **It is honest about its limits.** `http.server` is not a production web server, and the
   code says so where it matters. Knowing *why* it is not is worth more than using one that
   never raises the question.

Labs 3 and 5 add pinned Google Cloud client libraries to `requirements.txt` — one at a
time, when there is a reason.

## What it does

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/healthz` | Liveness. Deliberately does not touch storage — week 11 explains why. |
| `GET` | `/stats` | In-process counters, backend names, instance id. |
| `POST` | `/documents` | Store a document. Body is the content; `X-Document-Name` names it. |
| `GET` | `/documents/{id}` | Document metadata. |
| `DELETE` | `/documents/{id}` | Delete. Idempotent — deleting twice succeeds. |
| `POST` | `/jobs` | Create a job. Body: `{"document_id": "...", "operation": "..."}`. Honours `Idempotency-Key`. |
| `GET` | `/jobs/{id}` | Job status and result. |
| `GET` | `/jobs?limit=N` | Recent jobs, newest first. |

Operations: `wordcount`, `checksum`, `extract`. The domain logic is trivial on purpose —
this course is about the cloud, not about text analysis, and every minute spent on domain
features is a minute not spent on what is being assessed.

Two headers come back on every response. `X-Request-Id` is echoed if you send one and
generated if you do not, and it appears on every log line produced while handling that
request — which is what makes "trace this request" a matter of grepping rather than
guessing. `X-Instance-Id` tells you *which process* answered; meaningless on your laptop,
essential in Lab 4 when there are several.

## Configuration

Everything arrives through environment variables. Nothing is read from a config file, and
nothing is hard-coded to a particular machine — because in Lab 4 this runs in a container
where there is no file to edit and no shell to edit it from.

| Variable | Default | Notes |
|---|---|---|
| `PORT` | `8080` | Managed platforms set this for you. Honouring it is why Lab 4 needs no code change. |
| `DOCAPP_HOST` | `127.0.0.1` | Local only, and therefore not reachable from the network. Lab 2 changes this and asks you to explain the consequence. |
| `DOCAPP_STORAGE` | `local` | Lab 3 adds `gcs`. |
| `DOCAPP_JOBSTORE` | `memory` | `file` is **your Lab 1 exercise**. Lab 3 adds `firestore`. |
| `DOCAPP_QUEUE` | `inline` | Lab 5 adds `pubsub`. |
| `DOCAPP_DATA_DIR` | `./data` | Where local storage writes. |
| `DOCAPP_MAX_DOCUMENT_BYTES` | `65536` | Bounded so a typo cannot fill a disk. |
| `DOCAPP_PROCESSING_DELAY_MS` | `250` | Simulated work. Explicit rather than hidden, so you always know what you are measuring. |
| `DOCAPP_LOG_LEVEL` | `info` | `debug`, `info`, `warning`, `error`. |

Give one of these a value it cannot accept and the application refuses to start, with a
sentence telling you what to fix. That is intentional: failing at start-up beats failing
halfway through your first request.

## Tests

```bash
pip3 install -r requirements-dev.txt   # pytest only
python3 -m pytest                      # the standard suite
python3 -m pytest -m lab01             # the Lab 1 acceptance tests (your exercise)
```

A fresh clone passes the standard suite. `-m lab01` fails until you have done Lab 1 — those
tests **are** the specification for the exercise, and reading them first is the intended
way to start.

The tests check behaviour the course depends on, not implementation detail: that a document
survives a restart and a job record does not, that a repeated submission with the same
idempotency key returns the same job, that reprocessing a finished job does no work, that a
failed job is recorded as failed rather than crashing the worker, and that ten simultaneous
requests produce ten jobs.

Two files pin the course's two hardest lessons as tests rather than as prose.
`test_state_is_not_in_the_process.py` is Lab 1's: state inside a process dies with it.
`test_two_instances_disagree.py` is Lab 4's: two healthy instances, nothing crashed, and two
different answers to the same question — including an idempotency key that silently stops
working. Read both before the labs that need them.

## How the code is laid out

```text
docapp/
  config.py       Environment → validated Config, with actionable errors
  models.py       Document, Job, Counters — the state that matters
  storage.py      Storage Protocol + LocalStorage       (Lab 3 adds Cloud Storage)
  jobstore.py     JobStore Protocol + MemoryJobStore    (Lab 1: FileJobStore; Lab 3: Firestore)
  queue.py        Queue Protocol + InlineQueue          (Lab 5 adds Pub/Sub)
  processing.py   The domain work. Pure: bytes in, dict out.
  service.py      What the application does, independent of HTTP
  app.py          Routing, status codes, request/response — and nothing else
  logs.py         Structured JSON logs to stdout
  wiring.py       Builds the object graph from config
  __main__.py     Entry point

tools/
  measure.py      Load measurement: N requests, C in flight, latency percentiles
  instances.py    How many instances answered a burst, read from X-Instance-Id
```

Both tools are standard-library only and bounded by default — an unbounded request
generator pointed at a metered service is how a free tier becomes a bill. Both take a
repeatable `--header`, which is how Lab 4 measures a service that refuses callers with no
identity. **Read the `--help` epilogue of each before drawing a conclusion from its output**:
the limitations printed there are part of what the course is teaching, and several marks in
Lab 4 are sitting in them.

The three `Protocol` classes are the seams. Each lab supplies a new implementation of one
of them and changes an environment variable; no lab rewrites the application. That is the
design lesson hiding in the directory listing — an application that names an *abstraction*
can move, and one that calls `open()` inside its request handler cannot.

`service.py` holds the behaviour and `app.py` holds only the HTTP. That is why the same
logic runs behind a web request in week 2 and behind a queue consumer in week 10 without
changing, and why the tests can exercise real behaviour without starting a server.
