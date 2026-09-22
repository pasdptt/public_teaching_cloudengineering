# Week 8 — Teaching guide: Managed containers and serverless

| | |
|---|---|
| **Outcomes** | CLO-1, CLO-2, CLO-5 |
| **Assessment** | **Quiz 4** (weeks 5–7) |
| **Practical** | Lab 4 Parts 0–3 |
| **Prep time** | ~3.5 h first delivery, ~1 h subsequently |

## Session objectives

1. State what the customer stops operating when moving from a VM to managed execution, and
   what they take on instead.
2. Explain the request-scoped instance lifecycle, and why an instance may be created or
   destroyed without anything going wrong.
3. Explain why statelessness is a precondition rather than a style, using the application's
   own two kinds of state.
4. Describe what happens during a cold start, in order, and name what makes one longer.
5. Treat the concurrency setting as a design decision with a cost, not a default.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| What you stop operating | 20 | The Lab 2 responsibility list, crossed out item by item |
| **The instance lifecycle** | 20 | Request-scoped. Created, reused, destroyed, all without failure. |
| **Statelessness as the price** | 25 | The heart of the session. Two kinds of state, one survives. |
| Break | 10 | |
| Cold start | 15 | What is actually happening, in order |
| Concurrency, and what it costs | 15 | 1 vs 80, and the per-request/per-hour crossover |
| **Quiz 4** | 15 | Weeks 5–7 |
| Practical | 60 | Lab 4 Parts 0–3 |

**180 minutes exactly.** 95 concepts · 15 quiz · 60 practical, plus the break. The discussion
prompt below is an alternative to part of the concept time, not an addition to it — in a quiz
week there is no room for both, and the quiz is the fixed obligation.

---

## Teaching notes

### Open by crossing things out

Put the Lab 2 responsibility list on the board — they wrote it five weeks ago. Choose the
machine size, create it, install Python, write a systemd unit, open a firewall port, keep it
patched, notice when it dies, delete it before it costs money.

Then cross out the ones managed execution takes over, one at a time, asking each time *who*
now does it. The list shrinks to almost nothing, and that visible shrinking is the lesson.

Then ask what got **added**, and let the silence sit before answering: a build step, a
registry to keep clean, a cold start, a platform whose scaling decisions you do not control,
and a hard requirement that your application hold no state. Week 14 revisits this as
"a managed service is a dependency".

### The lifecycle, with no failure in it

Students arrive believing instances appear when something goes wrong. Say it plainly:

> An instance being created, serving one request, and being destroyed is **not** an incident.
> It is Tuesday.

Draw the timeline: request arrives, no instance exists, one is started, it serves, it is kept
warm for a while in case another comes, then it is gone. Nothing failed at any point.

Now the question that makes it bite: *which of those transitions does your application get
told about?* Effectively none. That is what "request-scoped" costs.

### Statelessness, using their own application

This is the block that matters, and the application makes it concrete for free.

Ask: the service stores documents in a bucket and job records in a dictionary. Two instances
are running. Draw what each one can see.

Let them work out that the documents are shared and the jobs are not. Then push:

> Nothing has failed. Both instances are healthy. Why does the user get a 404?

Land on the formulation the whole course has been building towards:

> **State is not "data". State is anything an instance knows that the next instance will
> need.** If it lives inside the instance, there is no next instance — there are only
> unrelated ones.

Then the sharper version, which is Lab 4's Part 3 and is worth showing rather than telling:
the idempotency key stops working. Retries stop being deduplicated, work is done twice, and
**nothing logs an error**. A bug that returns 500 gets fixed. A bug that returns 200 twice
gets shipped.

If there is a machine and a projector, run
`pytest tests/test_two_instances_disagree.py -v` live. Three tests, ten seconds, and the
third one shows that the fix is a wiring change and not a code change.

### Cold start: say what is actually happening

Not "it is slow the first time". In order: the platform must find capacity, pull the image
(or not, if it is cached), start the container, wait for the process to initialise, and wait
for it to accept a connection on `$PORT`. Only then does the request get served.

Ask which of those the developer controls. Image size and initialisation work — that is it.
Then ask what in *this* application would dominate, and note that it is a small image with no
framework, which is why their measurement in Part 5 may be less dramatic than the internet
led them to expect. Say that in advance, so a modest number reads as a finding rather than a
mistake.

### Concurrency: put the two numbers side by side

Draw 20 simultaneous requests into a service with concurrency 80, then into one with
concurrency 1. Ask for a show of hands on which has lower median latency before revealing
anything.

The useful confusion is that both answers are defensible, because it depends on whether the
work is waiting or computing. The application waits — a 250 ms sleep — so one instance can
overlap a great many. If it computed for 250 ms, it could not.

Do not resolve it fully. Part 4 measures it, and a class that has argued about it measures
with more attention.

### Then the pricing shape, in the same block

Per-request-second versus per-machine-hour. The point is not the rates; it is that the
crossover exists. Ask: at what traffic level does a $0.005/hour always-on VM become cheaper
than paying per request? Nobody needs the exact number. Everybody needs to know the question
has an answer, and that `--min-instances=1` silently moves you to the wrong side of it.

Tie it to the concurrency argument they have just had: concurrency 1 gives every request an
instance to itself, which is lovely for isolation and multiplies the vCPU-seconds you are
billed for. Both halves of this block are the same decision seen from two directions.

---

## Common misconceptions

| Misconception | Surfaces as | Response |
|---|---|---|
| "Serverless means there are no servers" | Week 1 onwards | There are servers. You have stopped having a relationship with any particular one. |
| "An instance being destroyed means something failed" | Lifecycle block | It is the normal case. Draw the timeline with no failure in it. |
| "Statelessness is a coding style" | Constantly | It is a precondition. Without it the platform's freedom to move you is a bug generator. |
| "A 200 response means it worked" | Idempotency demo | Two 200s for one submission means it worked twice. |
| "Cold start is about the language" | Cold-start block | It is image size plus initialisation. A small image in a slow language starts faster than a huge one in a fast language. |
| "min-instances=1 is a small optimisation" | Practical | It converts request pricing into machine pricing, all month, for a service nobody is calling. |
| "Higher concurrency is always better" | Concurrency block | Better for throughput, sometimes worse for tail latency, and it depends entirely on whether the work is waiting or computing. |
| "The registry is free" | Teardown | 0.5 GiB. About a dozen builds of this image. |

---

## Discussion prompt — use it *instead of* concept time, not on top of it

> A team moves a service to managed execution. It works in testing and breaks in production
> once a week, always at peak load, always with users reporting "my thing vanished".

Give them three minutes in pairs to produce the diagnosis, then ask for the evidence they
would want. The answer they should converge on is per-instance state plus scaling. The part
worth pressing is *why testing did not catch it*: one instance is always enough to pass.

That is also the honest framing for Lab 4 Part 3, where some students will fail to reproduce
the bug on demand — which proves the point rather than undermining it.

---

## Practical (60 min): Lab 4 Parts 0–3

- **Part 0 is written before anything is run**, and collected. It is worth marks and it is
  the only part that cannot be reconstructed later.
- **Make sure their Lab 3 code is in the working tree** before anyone builds. An image built
  from a tree without `GcsStorage` fails at the first request, from Iowa, and the student
  will debug the platform instead of their build.
- **The 403 will read as a failure** to several students. Say once, to the room, that it is
  the deployment working.
- **`04-runtime-identity.sh` has a TODO and no answer.** Expect to be asked for the role
  names. Do not give them; ask instead what the application does that touches a service, and
  let them search for the role that covers it. Note who reaches for `roles/editor`.
- **Watch the clock on the build.** The first `gcloud builds submit` takes a few minutes.
  Start it early and use the wait for the identity discussion.

End by asking them to leave the service deployed on the *broken* configuration, and to bring
their Part 3 output to week 9. Instances stay warm for a few minutes and cost nothing at
rest.

## Links

- Student notes: `weeks/week-08/student-notes.md`
- Lab: `labs/lab-04/README.md` · Rubric: `labs/lab-04/rubric.md`
- The lesson as a test: `application/tests/test_two_instances_disagree.py`
- Cost reasoning: `operations/cost-model.md` §3, Lab 4
- Solutions, the expected role set and the mistake list: private repo, `lab-solutions/lab-04/`
