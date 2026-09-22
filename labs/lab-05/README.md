# Lab 5 — Asynchrony and resilience

**Weeks 10–11 · 7.5% of the final grade · Individual submission**

| | |
|---|---|
| **Cloud resources** | One Pub/Sub topic, one dead-letter topic, one push subscription, the Lab 4 Cloud Run service rebuilt, one bucket, two service accounts |
| **Estimated cost** | **$0.00.** Well inside the 10 GiB/month Pub/Sub allowance and the Cloud Run free tier — *provided* the subscription is deleted at the end. A subscription nobody reads retains messages, and retained messages are billed storage. |
| **Outcomes** | CLO-5 (asynchronous design, idempotency), CLO-6 (controlled failure experiments and evidence) |
| **Estimated novice time** | ~2 h guided (2 × 60 min) + ~5 h independent over two weeks |
| **Observed pilot time** | *not yet measured* |

---

## Why this lab exists

Lab 4 scaled the service and every request still waited for the processing to finish. More
instances bought more places to wait; they did not make anyone wait less.

This lab takes the work out of the request path. Submitting a job stops meaning "do this
now" and starts meaning "I have written this down, and something will pick it up".

Everything hard about this course arrives with that sentence. The client no longer learns
the answer from the response. The work happens somewhere you were not watching. And the
thing that carries the message promises to deliver it **at least once** — which is a
promise with a sharp edge, because "at least once" includes "twice".

The assessed idea is **idempotency**, not the queue product. Pub/Sub is this course's
workbench; the property that makes retries safe is the thing you will still need in ten
years.

## Before you start

- [ ] Lab 4 submitted, torn down and verified.
- [ ] `pip3 install -r application/requirements.txt` — one new package since Lab 3.
- [ ] `cd labs/lab-05/starter && cp config.env.example config.env`, then edit `PROJECT_ID`.
- [ ] Your trial has not expired. There are five weeks left and this is the last billable lab.

> **You will rebuild and redeploy the Lab 4 service from source.** That is deliberate. You
> tore it down completely, and bringing it back with three scripts is the first time this
> course asks you to demonstrate that a deployment is reproducible rather than remembered.
> If anything is missing, the missing thing is a finding — write it down, because it is the
> problem Lab 6 exists to solve.

---

## Part 0 — Predict (~20 min) · **before you run anything**

Write these down now, with a sentence of reasoning each.

1. The response to `POST /jobs` currently contains the finished result. After this lab, what
   should it contain? Design the answer before you see what the code does.
2. A client submits a job, the network eats the response, and the client retries. Describe
   what happens with the idempotency key, and what happens without one.
3. The broker delivers the same message twice. What in the application stops the work
   happening twice? Name the exact code path — you have read it before.
4. You publish a message to a topic that has no subscription. Where does it go?
5. Your service is broken and returns an error for every delivery. What does a sensible
   broker do, and for how long?

## Part 1 — Do the whole lab on your laptop first (~60 min) · **no cloud account**

The application ships with a real queue that runs in your own process. It is not durable and
it is not distributed, and it is exactly right for learning what at-least-once means —
because you can turn the duplicates on:

```bash
cd application
DOCAPP_QUEUE=thread DOCAPP_QUEUE_DUPLICATE_PERCENT=100 \
DOCAPP_PROCESSING_DELAY_MS=1000 python3 -m docapp
```

In another terminal, submit a job and read the response carefully:

```bash
DOC=$(curl -s -X POST localhost:8080/documents -H "Content-Type: text/plain" \
  -H "X-Document-Name: notes.txt" --data-binary @samples/cloud-intro.txt \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

curl -s -X POST localhost:8080/jobs -H "Content-Type: application/json" \
  -d "{\"document_id\":\"$DOC\",\"operation\":\"wordcount\"}" | python3 -m json.tool
```

**`"status": "pending"`.** The response no longer carries the answer. Wait two seconds and
look at `/stats`:

```bash
curl -s localhost:8080/stats | python3 -m json.tool
```

You should see `jobs_processed: 1` and **`duplicate_deliveries_skipped: 1`**, with the queue
reporting `delivered: 2, duplicates_injected: 1`. The message arrived twice. The work
happened once.

**Find out why.** Read `run_job` in `docapp/service.py`, name the lines that did it, and
then read `tests/test_threadqueue.py` — particularly
`test_duplicate_delivery_does_not_do_the_work_twice`, whose docstring tells you exactly
which line to delete if you want to watch it fail. Run the suite and see the retry and
dead-letter behaviour too:

```bash
python3 -m pytest tests/test_threadqueue.py -v
```

**Answer in your submission:**

1. `POST /jobs` returned `pending`. What must a client do now that it did not have to do
   before? Sketch the client's loop, and say what it should do if the job is still `pending`
   after five minutes.
2. What is the *earliest* moment the application could have returned to the caller, and what
   would it have given up by returning then?
3. The local queue is in your process. Name three things a real broker gives you that it
   cannot, and one thing it does better.

## Part 2 — The envelope (~50 min) · **still no cloud account**

Pub/Sub delivers a message by making an HTTP POST to your service. The body is a JSON
envelope with the payload nested inside it and **base64-encoded**.

Implement `decode_push_envelope` in `application/docapp/pubsub_queue.py`. The acceptance
tests are the specification and they cost nothing to run:

```bash
cd application
python3 -m pytest -m lab05
```

Fourteen of these tests need no cloud account at all. Get all fourteen green before you
create a single cloud resource — the base64 mistake in particular is one you want to find
here, in two seconds, rather than against a real broker as a 404 for a job you can see in
the console.

The docstring asks you five questions. **Answer them.** Question 2 is about a message id you
are deliberately not using, and question 5 is about who is allowed to call your push
endpoint — which is Part 3.

## Part 3 — The real broker (~75 min)

Implement `PubSubQueue.submit`, then:

```bash
cd ../labs/lab-05/starter
./01-enable-apis.sh
./02-create-queue.sh      # prints a BUCKET_NAME; add it to config.env
./03-build-push.sh
./04-deploy.sh            # has a TODO: the runtime identity needs one new permission
```

**Stop here and submit a job**, before you create the subscription. Watch it stay `pending`.
Check `/stats`. Wait a minute and check again.

Nothing is consuming. Nothing ever will be. **Record what you observe and connect it to your
Part 0 answer to question 4** — a topic with no subscription discards what it receives, so
those jobs are not delayed, they are gone. That is a design property worth meeting once,
deliberately, rather than during an incident.

Now connect the two ends:

```bash
./05-create-subscription.sh   # has a TODO: the push identity needs exactly one role
```

`05` creates a **second** service account. Pub/Sub has to call your service, your service
refuses anonymous callers, so the broker needs an identity of its own.

**Answer in your submission:** there are now three identities — the one you use, the one the
service runs as, and the one the broker calls with. State what each may do. Then say what a
project-level `roles/run.invoker` grant would have permitted that your service-level grant
does not.

**Checkpoint.** Submit a job. It returns `pending` and reaches `succeeded` without anyone
asking it to.

## Part 4 — Duplicates, for real (~55 min)

You cannot make a broker redeliver on demand. You can make it deliver the same message
again, which drives your service down exactly the same path:

```bash
JOB=$(curl -s -X POST "$SERVICE_URL/jobs" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"document_id\":\"$DOC\",\"operation\":\"wordcount\"}" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

sleep 5
for i in 1 2 3 4 5; do
  gcloud pubsub topics publish "$TOPIC_NAME" --message="$JOB" --project="$PROJECT_ID"
done
```

Wait, then check the job and `/stats`.

**What you should see:** `attempts` still 1, one result, `completed_ms` unchanged, and
`duplicate_deliveries_skipped` up by five.

**Now the honesty question, and it is worth real marks.** You just published five messages;
the broker did not redeliver one. Those are different things.

- What does this experiment prove about your service?
- What does it **not** prove about Pub/Sub?
- Part 1 made real duplicates happen on demand, locally. Which of the two experiments is
  better evidence for which claim? Say why a lab that only did the cloud version would be
  weaker.

Then the design question: your idempotency protection is `run_job` returning early for a
terminal job. **Describe a sequence of events that defeats it.** (Hint: two instances, one
message each, at the same moment, and a job that is not terminal yet.) You are not asked to
fix it. You are asked to say what it would take to fix, and whether this application should
bother.

## Part 5 — The failure experiment (~60 min)

**Change one variable. Measure. Explain.**

Break the consumer on purpose, by pointing the subscription at an endpoint that does not
exist:

```bash
gcloud pubsub subscriptions update "$SUBSCRIPTION_NAME" --project="$PROJECT_ID" \
  --push-endpoint="${SERVICE_URL}/tasks/does-not-exist"
```

Submit three jobs. Then watch, recording the time at each step:

```bash
gcloud pubsub subscriptions describe "$SUBSCRIPTION_NAME" --project="$PROJECT_ID"
gcloud pubsub topics list-subscriptions "$DEAD_LETTER_TOPIC" --project="$PROJECT_ID"
gcloud logging read \
  'resource.type="cloud_run_revision" AND httpRequest.status>=400' \
  --project="$PROJECT_ID" --limit=30 --freshness=20m
```

**Record a timeline**: when you submitted, when the first delivery attempt arrived, when the
next one did, and when the message stopped being retried. You configured
`MAX_DELIVERY_ATTEMPTS=5`.

Now repair it:

```bash
gcloud pubsub subscriptions update "$SUBSCRIPTION_NAME" --project="$PROJECT_ID" \
  --push-endpoint="${SERVICE_URL}/tasks/process"
```

Submit another job and confirm recovery.

**Write ~350 words:**

1. **The timeline**, with intervals. Were the retries evenly spaced? What does the spacing
   tell you, and why would evenly-spaced retries be a worse design?
2. The jobs from the broken period: what state are their **job records** in, and what state
   are their **messages** in? These are different answers, and the gap between them is the
   most important thing in this lab. What would a user see?
3. Dead-lettering is a decision to stop trying. What is the alternative, what does it cost,
   and what would you have to build to make a dead-letter topic useful rather than a place
   where messages go to be ignored?
4. **What evidence was missing?** You had job records, logs and subscription metrics. Name
   one question about this incident you could not answer, and say what you would add.
   Answering this well is most of band B3.

> **This experiment is why the subscription retention guard exists.** While the consumer was
> broken, messages were being *stored*. That is Lab 5's version of Lab 2's idle IP address:
> the cost arrives from something you stopped using, not something you are using.

## Part 6 — Teardown and verification (~30 min) · **graded**

```bash
./06-teardown.sh
./07-verify-clean.sh
```

**Delete the subscription first**, and the script does. Deleting the service while a live
subscription still has retained messages means every one of them is redelivered to an
endpoint that 404s until the broker gives up. Harmless, noisy, and a decent illustration of
why teardown has an order.

Include the verification output. **Cleanup claimed but not verified earns nothing in band C.**

---

## What to submit

`lab05-<your-name>.md`, plus your `pubsub_queue.py` and the two filled-in TODO scripts.

1. **Part 0 predictions**, unedited, with your account of which were wrong.
2. **The local evidence** from Part 1: the `pending` response, the `/stats` output showing
   one processing and one skipped duplicate, and your three answers.
3. **Your `decode_push_envelope`**, the five docstring answers, and `pytest -m lab05` output.
4. **Your `PubSubQueue.submit`**, plus what you observed with a topic and no subscription.
5. **The three identities**, what each may do, and the project-vs-service grant answer.
6. **The duplicate experiment**, including what it does and does not prove, and the sequence
   of events that defeats the current protection.
7. **The failure experiment**: timeline with intervals, ~350 words, and the missing-evidence
   answer.
8. **Teardown verification output.**
9. **Cost estimate vs actual**, each line traced to its allowance.
10. **AI-assistance disclosure.**

## Resource inventory

| Resource | Created by | Removed by | Watch |
|---|---|---|---|
| Pub/Sub topic + dead-letter topic | `02-create-queue.sh` | `06-teardown.sh` | A topic alone holds nothing |
| **Push subscription** | `05-create-subscription.sh` | `06-teardown.sh` — **first** | **Retains messages and bills for them.** The one to check twice |
| Cloud Run service | `04-deploy.sh` | `06-teardown.sh` | `--min-instances` must be 0 |
| Artifact Registry repo + images | `03-build-push.sh` | `06-teardown.sh` | 0.5 GiB free; `v1` and `v2` both count |
| Bucket | `02-create-queue.sh` | `06-teardown.sh` | Object versions |
| Two service accounts | `04`, `05` | `06-teardown.sh` | Two now, not one |
| Firestore `(default)` | Lab 3 | kept; empty the collection | Empty is free |

## Troubleshooting

**Jobs stay `pending` forever.** Expected until Part 3's subscription exists — then it is
the push endpoint. Check that the subscription's endpoint ends in `/tasks/process`, and look
for 403s in the logs: that is the push identity missing `roles/run.invoker`.

**`403` on every push delivery, and you granted `run.invoker`.** You probably granted it at
the project level to the wrong account, or you are missing the second grant — Pub/Sub's own
service agent needs permission to mint tokens for your push account. The error names it.
Read the error rather than searching.

**Every message dead-letters immediately.** Your endpoint is returning 4xx. A 400 means
`decode_push_envelope` is rejecting a real envelope: capture the body from the logs and feed
it to your decoder in a local test.

**Jobs succeed but `attempts` climbs above 1.** Your service is being redelivered messages
it already acknowledged, which usually means it is answering too slowly for the ack
deadline. Compare your processing delay with `ACK_DEADLINE_SECONDS` and say what you found.

**`NotImplementedError: PubSubQueue is your Lab 5 exercise`** from the deployed service. You
built the image before implementing it, or built from a tree without your changes. Rebuild.

**The 404 experiment produces nothing in the dead-letter topic.** Dead-lettering needs both
the subscription's dead-letter configuration *and* permissions for Pub/Sub to publish to
that topic. Check `gcloud pubsub subscriptions describe` output first — if the dead-letter
policy is absent, the subscription was created before you set it.

**Everything works locally and nothing works deployed.** The single most likely cause is
that the deployed service has `DOCAPP_QUEUE=pubsub` and your local one does not. Check
`/stats` — it reports the backends it is actually running.
