---
marp: true
theme: cloudcourse
paginate: true
footer: 'Week 9 · Managed containers and serverless'
---

<!--
Deck for week 9. Derived from course/teaching-guides/week-09.md — that file is authoritative
for the teaching; this is what goes on the wall.

Render:  bash course/slides/render.sh 09
-->

<!-- _class: lead -->

# Managed containers and serverless

## Week 9

Cloud Computing: Principles and Practice

<!--
TIMING: 180 min total — 95 concepts · 15 quiz · 60 practical · 10 break. The discussion prompt replaces concept time; it is never added on top.
Guide: course/teaching-guides/week-09.md
Before you start: Quiz 4 printed. application/ open with tests/test_two_instances_disagree.py ready to run. Remind them to have their Lab 3 code committed in application/ before anyone builds.
-->

---

## Where we are

Lab 2 gave you a machine. Lab 3 took the state off it.

This week you hand the platform an image and **stop having a machine at all**.

Today: what you stop doing, what you take on instead, and the one requirement that makes it possible.

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">0:00 – 0:20</span>

# What you stop operating

Your Lab 2 list, crossed out

---

## Your Lab 2 responsibility list

- Choose the machine size
- Create it
- Install Python
- Write a systemd unit
- Open a firewall port
- Keep it patched
- Notice when it dies
- Delete it before it costs money

<!--
They wrote this list five weeks ago. Put it on the board and cross out each item managed execution takes over, one at a time, asking each time WHO now does it. The visible shrinking is the lesson.
Guide: "Open by crossing things out"
-->

---

<!-- _class: ask -->

## The list got shorter.
## What got added?

<!--
Let the silence sit. Then: a build step · a registry to keep clean · a cold start · a platform whose scaling decisions you do not control · a hard requirement that the application hold no state.
-->

---

## What you take on instead

| Added | Why it matters |
|---|---|
| A build step | What runs is an image, not a directory |
| A registry to keep clean | 0.5 GiB free — about a dozen builds of this image |
| A cold start | The first request after quiet pays for starting an instance |
| Scaling you do not control | The platform decides how many copies, and when |
| **No state in the instance** | Not a style. A precondition. |

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">0:20 – 0:40</span>

# The instance lifecycle

Created, reused, destroyed — and nothing failed

---

## One instance's life

```text
request arrives  ->  no instance exists
                 ->  one is started
                 ->  it serves the request
                 ->  it is kept warm in case another comes
                 ->  it is gone
```

Nothing failed at any point.

<!--
Draw the timeline on the board as well. Students arrive believing instances appear when something goes wrong.
Guide: "The lifecycle, with no failure in it"
-->

---

<!-- _class: punch -->

## An instance being created, serving one request, and being destroyed is not an incident. It is Tuesday.

---

<!-- _class: ask -->

## Which of those transitions does your application get told about?

<!--
Effectively none. That is what "request-scoped" costs.
-->

---

<!-- _class: block -->

<span class="min">25 minutes</span><span class="clock">0:40 – 1:05</span>

# Statelessness as the price

Two kinds of state, and only one survives

---

<!-- _class: ask -->

## Documents in a bucket. Job records in a dictionary. Two instances.
## Draw what each one can see.

<!--
Let them work out that the documents are shared and the jobs are not. This is the heart of the session — give it the full time.
Guide: "Statelessness, using their own application"
-->

---

## Two healthy instances

| | Instance A | Instance B |
|---|---|---|
| Documents (Cloud Storage) | sees every document | sees every document |
| Job records (in memory) | sees **its own** jobs | sees **its own** jobs |

A job created on A, then read on B: **404.**

<!--
Push: nothing has failed, both instances are healthy. Why does the user get a 404?
-->

---

<!-- _class: punch -->

## State is anything an instance knows that the next instance will need.

<!--
Then: if it lives inside the instance, there is no next instance — there are only unrelated ones.
-->

---

## The sharper version: idempotency stops working

The idempotency key lives in the same dictionary as the jobs.

So a retry that lands on a different instance **is not recognised**. The work is done twice.

**Nothing logs an error.** Every response is a 200.

---

<!-- _class: punch -->

## A bug that returns 500 gets fixed. A bug that returns 200 twice gets shipped.

---

<!-- _class: demo -->

## The lesson as a test

```bash
cd application
python3 -m pytest tests/test_two_instances_disagree.py -v
```

Three tests, ten seconds. Watch the third one.

<!--
The third test shows that the fix is a WIRING change, not a code change — the same point Lab 4 Part 3 makes in the cloud.
-->

---

<!-- _class: block -->

<span class="min">Break — 10 minutes</span><span class="clock">1:05 – 1:15</span>

# Break

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">1:15 – 1:30</span>

# Cold start

What is actually happening, in order

---

## Before the first request is served

1. The platform finds capacity
2. It pulls the image — or not, if it is cached
3. It starts the container
4. It waits for the process to initialise
5. It waits for the process to accept a connection on `$PORT`

**Then** the request is served.

---

<!-- _class: ask -->

## Which of those five steps do you control?

<!--
Image size and initialisation work. That is it.
-->

---

## What dominates for this application?

A small image with **no framework** to load.

So your Part 5 measurement may be less dramatic than the internet led you to expect.

A modest number is a **finding**, not a mistake.

<!--
Say this in advance, so a modest number reads as a result.
-->

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">1:30 – 1:45</span>

# Concurrency, and what it costs

One setting, seen from two directions

---

<!-- _class: ask -->

## Twenty requests at once. Concurrency 80, or concurrency 1.
## Which has the lower median latency?

<!--
Show of hands BEFORE revealing anything. Both answers are defensible: it depends on whether the work is waiting or computing. The application waits — a 250 ms sleep — so one instance can overlap many. If it computed for 250 ms, it could not.
Do not resolve it fully. Part 4 measures it.
Guide: "Concurrency: put the two numbers side by side"
-->

---

<!-- _class: cost -->

## Per request, or per machine-hour

| | Billed for |
|---|---|
| Managed execution | the seconds an instance spends handling requests |
| A virtual machine | every hour it exists, used or not |

At some traffic level an always-on VM becomes cheaper. **Nobody needs the exact number. Everybody needs to know it exists.**

`--min-instances=1` quietly moves you to the wrong side of it.

<!--
Ask: at what traffic level does a $0.005/hour always-on VM become cheaper than paying per request?
-->

---

<!-- _class: cost -->

## The same decision, seen from the bill

Concurrency 1 gives every request an instance to itself.

Lovely for isolation. It also **multiplies the vCPU-seconds you are billed for**.

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">1:45 – 2:00</span>

# Quiz 4

Weeks 5–7

<!--
CLO-1, CLO-2, CLO-4. Storage, consistency, and what a machine commits you to — including Labs 2 and 3. Today's managed-execution material is not assessed. Key in the private repository.
-->

---

<!-- _class: block -->

<span class="min">60 minutes</span><span class="clock">2:00 – 3:00</span>

# Practical

Lab 4 Parts 0–3

---

## Part 0 — predict, before you run anything

Five predictions, a sentence of reasoning each. **Written now, collected, and never edited.**

You are marked on the reasoning and on your account of where you were wrong — never on being right.

<!--
Part 0 is the only part that cannot be reconstructed later. Collect it.
Check before anyone builds: their Lab 3 GcsStorage and FirestoreJobStore are committed in application/. An image built without them fails at the first request, from Iowa.
-->

---

<!-- _class: demo -->

## Part 1 — build the artefact

```bash
cd weeks/week-09/lab-04/starter
cp config.env.example config.env     # set PROJECT_ID
./01-enable-apis.sh
./02-create-registry.sh              # prints a BUCKET_NAME
./03-build-push.sh
```

The script prints the image **digest** as well as the tag. Record both, and the image size.

<!--
The first gcloud builds submit takes a few minutes. Start it early and use the wait for the identity discussion.
-->

---

<!-- _class: demo -->

## Part 2 — deploy it, and decide who may call it

```bash
./04-runtime-identity.sh             # has a TODO. Read it first.
./05-deploy.sh
```

Choosing the service account's roles **is the exercise**. Smallest role, smallest scope, one sentence of justification each.

**No key file is created anywhere in this lab.**

<!--
Expect to be asked for the role names. Do not give them. Ask what the application does that touches a service, and let them search. Note who reaches for roles/editor.
-->

---

<!-- _class: demo -->

## The 403 is the deployment working

```bash
SERVICE_URL=$(gcloud run services describe docapp --region=us-central1 \
  --project="$PROJECT_ID" --format='value(status.url)')

curl -i "$SERVICE_URL/healthz"                                    # 403
curl -i -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
     "$SERVICE_URL/healthz"                                       # 200
```

<!--
Say ONCE, to the room, that the 403 is correct. Several students will read it as a failure.
-->

---

<!-- _class: demo -->

## Part 3 — forty requests: who has this job?

```bash
cd ../../../../application
python3 tools/instances.py --url "$SERVICE_URL" --path "/jobs/$JOB" \
  --requests 40 --concurrency 20 --header "Authorization: Bearer $TOKEN"
```

Distinct instances that answered **200**, and a count of `<HTTP 404>` from the ones that had never heard of it.

No 404s at all? Run it again at once. Still none? **Say so and say why** — that is a finding too.

<!--
Then the five-retries idempotency loop from the README. Count the distinct job ids.
-->

---

<!-- _class: demo -->

## The fix changes no application code

```bash
gcloud run services update docapp --region=us-central1 --project="$PROJECT_ID" \
  --update-env-vars="DOCAPP_JOBSTORE=firestore,DOCAPP_PROJECT_ID=${PROJECT_ID}"
```

Create a **new** document and job before you re-test. The old job was never written anywhere.

**Checkpoint:** forty requests, several instances, zero 404s. Five retries, one job id.

---

## This week's work — 180 minutes

| | |
|---|---|
| Read the notes | 30 min |
| Lab 4 first half: build, deploy, two instances | 150 min |

Leave the service on the **broken** configuration if you have not reached the fix, and bring your Part 3 output to week 10.

---

<!-- _class: lead -->

# Next week

Horizontal scaling, and measuring it honestly

**Lab 4 due** — the concurrency experiment, cold starts, and teardown

<!--
Instances stay warm for a few minutes and cost nothing at rest with --min-instances=0.
-->
