# Lab N — write-up

<!--
  Copy this file; do not edit it here:
      mkdir -p submissions/lab-0N && cp submissions/TEMPLATE.md submissions/lab-0N/README.md

  Then replace the headings below with the numbered items under "What to submit" in the
  lab's README, in the same order, with the same numbers. The examples under each heading
  show the conventions; delete them. How to hand it in: operations/lab-submission.md.
-->

**Project id:** `your-project-id` (Labs 2–6) · **Handed in at commit:** printed by `check_submission.py`

## 1. Predictions

_Written before Part N and committed in `abc1234` ("Lab N predictions, before Part N").
Not edited since; where they were wrong, section 4 says why._

1. …
2. …

## 2. What I did

Commands and configuration, not narration. Paste the command and what it printed:

```console
$ curl -s http://127.0.0.1:8080/healthz
{"status": "ok", "instance_id": "a1b2c3"}
```

## 3. Measurements

Ran on: _laptop or service, region, date_. Varied: _…_. Held constant: _…_.

| Concurrency | Requests | Throughput (req/s) | p50 latency (ms) | p95 latency (ms) |
|---:|---:|---:|---:|---:|
| 1 | 200 | … | … | … |

## 4. Explanation

Where the prediction held, where it did not, and why. Link code rather than pasting it, with
a path relative to this file: `[jobstore.py](../../application/docapp/jobstore.py)`.

## 5. Resource inventory and cleanup verification

| Resource | Created by | Removed by | Verified gone |
|---|---|---|---|
| … | … | … | output below |

```console
$ bash weeks/week-NN/lab-0N/starter/0X-verify-clean.sh
…
```

## 6. AI-assistance disclosure

_Which tools, for what, and what you checked or changed yourself. "None" is an answer._
