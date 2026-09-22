# Week 8 — Managed containers and serverless

**Quiz 4 this week** (weeks 5–7). **Lab 4 starts.**

---

## The question this week answers

You have run this application three ways now: on your laptop, inside a container, and on a
virtual machine you created and were responsible for. In Lab 2 you chose the machine size,
installed Python, wrote a systemd unit, opened a firewall port — and then deleted all of it
so it would stop costing money.

**Managed execution** is the abstraction where you stop doing that. You hand the platform a
container image and a few settings. It decides how many copies to run, where, and for how
long, and it charges you for time spent executing rather than for time the machine existed.

On Google Cloud the product is **Cloud Run**. Every other provider has one. The reasoning
below is about the abstraction; the flags are about the product.

## What you stop doing, and what you take on

Take the Lab 2 list and cross things off:

| Lab 2: you did this | Managed execution |
|---|---|
| Chose the machine type | The platform picks capacity; you set CPU and memory per instance |
| Installed the runtime | It is in your image |
| Wrote a service unit to keep it running | The platform runs your container |
| Opened a firewall port | The platform terminates HTTPS and routes to your `$PORT` |
| Patched the OS | The platform's problem |
| Noticed when it died | The platform replaces it |
| Deleted it so it would stop billing | At zero traffic and `min-instances=0`, it bills nothing |

That last row is the one worth dwelling on, because it changes what "forgetting" costs.

Now the other column, which tutorials leave out. You have taken on:

- **A build step and an artefact.** Something must turn your source into an image, and that
  image lives in a registry that is storage like any other.
- **A cold start**, because there is not always an instance ready.
- **No control over scaling decisions**, only over the bounds you give them.
- **A hard requirement to hold no state**, which is the rest of these notes.
- **A dependency.** The way you configure, deploy and observe this service is specific to
  this platform in a way a VM was not. Week 14 asks what leaving would cost.

## The instance lifecycle

An instance is created when a request arrives and there is nothing to serve it. It is kept
around for a while afterwards in case another one comes. Then it is destroyed.

**None of those transitions is a failure.** An instance serving one request and disappearing
is the normal case, not an incident. This is the part that most changes how you have to
write things:

> Your process may be created and destroyed at any time, for reasons that have nothing to do
> with anything going wrong, and it will not be told why.

A VM is a place. An instance is an event.

## Statelessness is the price of admission

Here is the thing that breaks, and it is worth understanding before Lab 4 shows it to you.

The application stores two things. Documents go to a bucket — that was Lab 3. Job records
live in a Python dictionary inside the process, which is how it has worked since week 2.

Run one instance and both work perfectly. Run two, and:

- Any instance can serve you a document. The bytes are in the bucket, which belongs to
  neither of them.
- Only the instance that created a job knows that job exists. Ask a different one and you
  get **404 — for a job that succeeded**.

Nothing failed. No instance is unhealthy. Nothing is in any log. The design was simply wrong
the moment there was more than one of it.

The definition worth memorising is not about data:

> **State is anything an instance knows that the next request will need.** If it lives inside
> the instance, there is no "next instance" — only unrelated ones.

### The version that costs money rather than returning an error

Since week 2 the application has supported an idempotency key: send the same submission
twice with the same key and the second one returns the first job instead of doing the work
again. That is what makes a client's retry safe.

It works by looking the key up in the job store. Two instances, two job stores, and the
lookup misses. The retry creates a second job and the work is done twice.

The user sees `200 OK`. The operator sees nothing. **A bug that returns an error gets fixed;
a bug that returns success twice gets shipped.** You will do this to yourself in Lab 4 Part 3
and then fix it by changing an environment variable — not a line of code.

The three tests in `application/tests/test_two_instances_disagree.py` pin all of this. Read
them; the third one shows that the fix is a wiring change.

## Cold start

If no instance exists when your request arrives, the platform must, in order:

1. find capacity,
2. fetch your container image (unless it is already cached nearby),
3. start the container,
4. wait for your process to initialise,
5. wait for it to accept a connection on `$PORT`.

Only then does anyone serve your request. That whole sequence is the cold start, and the
user experiences it as one slow request.

You control exactly two things in that list: **how big your image is** and **how much your
process does before it can accept a connection**. Not the language, not the framework — the
bytes to fetch and the work at startup. A small image in a slow language starts faster than a
large one in a fast language.

Our image is small and initialises almost nothing, so your Lab 4 measurement may be less
dramatic than the internet has led you to expect. That is a finding. Report it as one.

**`--min-instances=1` removes cold starts by keeping one instance always alive.** It also
means you are paying for an instance all month whether or not anyone calls it — which is a
rented machine again, bought at a worse price. Lab 4 asks you to work out what it would cost
and what you would have to believe about your users to justify it.

## Concurrency is a decision, not a default

One setting decides how many requests a single instance handles at the same time. Cloud Run's
default is 80.

Set it to **1** and each request gets an instance to itself: the strongest isolation, the
most predictable latency per request, and many more instances — which you pay for in
vCPU-seconds and which each carry their own cold start.

Set it **high** and one instance handles many requests at once. Fewer instances, better
utilisation, cheaper. But the requests share one process, so they share its CPU and its
memory, and a slow one can delay its neighbours.

Which is better depends on something you can reason about in advance:

> Is your request mostly **waiting**, or mostly **computing**?

Waiting overlaps beautifully — a hundred requests waiting on a network call cost almost
nothing to hold at once. Computing does not: two CPU-bound requests on one CPU take twice as
long each, and you have gained nothing but complexity.

Our application's 250 ms is a `sleep`. It is waiting. Predict accordingly, then measure it in
Lab 4 Part 4 and find out whether you were right.

## What transfers, and what does not

**Transfers everywhere:** request-scoped execution, statelessness as a precondition, cold
starts, a concurrency setting, per-use pricing, an image in a registry, an identity attached
to the running thing.

**Does not transfer:** the flag names, the default concurrency, the exact scaling algorithm,
the free-tier shape, and how you read logs. Those are worth knowing and not worth memorising.

## This week's work (~180 minutes)

| | |
|---|---|
| Read these notes; prepare for Quiz 4 (weeks 5–7) | 30 min |
| Lab 4 Parts 0–3: predict, build, deploy, and break it on purpose | 150 min |

Part 0 must be written **before** you run anything, and it is marked. Do not reconstruct it
afterwards — being wrong and explaining why is worth more than being right.

## Check yourself

1. Name three things you stop operating and three you take on.
2. An instance is created, serves one request, and is destroyed. What went wrong? (Careful.)
3. Why does a document survive a scale-out and a job record not, when the same request
   created both?
4. Explain how two instances break an idempotency key, and say what the user sees.
5. List, in order, what happens during a cold start. Which steps do you control?
6. Your service costs nothing at rest. What single flag changes that, and to what?
7. Concurrency 1 versus 80: which gives lower median latency for work that is mostly waiting?
   For work that is mostly computing? Say why they differ.
8. Artifact Registry's free allowance is 0.5 GiB. Why is that a cleanup problem and not a
   capacity problem?

## Next week

Scaling as a subject in its own right: horizontal versus vertical, why latency and throughput
are different questions, autoscaling as a feedback loop that reacts late, and how to design an
experiment whose answer you can actually defend. You finish Lab 4 by measuring one.
