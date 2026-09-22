# Lab 4 — Managed execution and elasticity

**Weeks 8–9 · 7.5% of the final grade · Individual submission**

| | |
|---|---|
| **Cloud resources** | One Cloud Run service (`us-central1`), one Artifact Registry repository, one Cloud Storage bucket, one service account, and the Firestore `(default)` database from Lab 3 |
| **Estimated cost** | **$0.00.** Everything here is inside Always Free — *provided* `--min-instances=0`, the experiment bounds are respected, and the images are deleted at the end. |
| **Outcomes** | CLO-2 (distributed behaviour under load), CLO-5 (stateless design), CLO-6 (measurement and interpretation) |
| **Estimated novice time** | ~2 h guided (2 × 60 min) + ~5 h independent over two weeks |
| **Observed pilot time** | *not yet measured* |

---

## Why this lab exists

Lab 2 gave you a machine. You chose its size, installed things on it, started a service, and
were responsible for all of it. Lab 3 took the state off that machine.

This lab asks what is left. You hand the platform a container image and it runs it — starting
instances when requests arrive, stopping them when they stop, and charging you for the time
it spent executing rather than for the time the machine existed.

That trade has a price of admission, and the price is statelessness. An instance can appear
at any moment, serve one request, and be gone. Anything it knows privately is knowledge the
next request cannot reach. **Lab 3 is what makes this lab possible**, and Part 3 is where you
watch what happens to someone who tried it in the other order.

You will also do the first real **experiment** of the course: change one setting, measure,
and account for the result. Week 9 is largely about why that is harder than it sounds.

## Before you start

- [ ] Lab 3 submitted, its bucket removed, and your `GcsStorage` and `FirestoreJobStore`
      implementations to hand. **You will deploy your own code**, not a reference version.
- [ ] Your Lab 3 measurement table, with its conditions. Part 6 compares against it.
- [ ] Your Lab 2 measurement table, for the same reason.
- [ ] `cd labs/lab-04/starter && cp config.env.example config.env`, then edit `PROJECT_ID`.
- [ ] Your trial has not expired. Check now, not in week 9.

> **One thing to fix before you build.** The container image is built from
> `application/`. If your Lab 3 implementations are not committed there, you will deploy an
> image that raises `NotImplementedError` on its first request, and the error will arrive
> from a machine in Iowa instead of from your laptop.

---

## Part 0 — Predict (~20 min) · **before you run anything**

Write these down now, with a sentence of reasoning each. You will be marked on the
reasoning and on your account of where you were wrong, never on being right.

1. Your service is deployed with `--min-instances=0` and nobody calls it for two hours. What
   does it cost? Say what you are assuming.
2. You send 12 requests, one at a time, from Bangkok to a service in Iowa. Compare the median
   latency you expect against your **Lab 3** figure, where the application ran on your laptop
   and its storage was in Iowa. Higher, lower, or the same — and why?
3. You send 40 requests with 20 in flight at once, to a service allowed at most 4 instances
   and set to handle 80 concurrent requests each. How many instances do you expect to answer?
4. Now the same 40 requests to a service set to handle **1** request at a time. How many
   instances, and what happens to the median latency?
5. The application is deployed with `DOCAPP_JOBSTORE=memory`. You create a job, then
   immediately ask for its status. Under what conditions do you get a 404, and how often?

## Part 1 — Build the artefact (~45 min)

```bash
./01-enable-apis.sh
./02-create-registry.sh     # prints a BUCKET_NAME; add it to config.env
./03-build-push.sh
```

The build runs on Google's infrastructure from your `Dockerfile`, and the result is pushed
to Artifact Registry. The script prints the image **digest** as well as the tag.

**Answer in your submission:**

1. You deployed `docapp:v1`. Tomorrow you push a different build with the same tag. What can
   someone reading `v1` in a deployment record now conclude about what is running? What can
   they conclude from the digest?
2. `application/Dockerfile` installs dependencies in one layer and copies source in a later
   one. Swap them in your head: what changes about the second build, and about what gets
   pushed? Artifact Registry's free allowance is 0.5 GiB — connect your answer to that number.
3. The image runs as `appuser`, not root. On managed execution you never touch the host. Name
   something that choice still protects, and something it does not.

**Checkpoint.** `gcloud artifacts docker images list` shows one image. Record its size.

## Part 2 — Deploy it, and decide who may call it (~50 min)

```bash
./04-runtime-identity.sh    # has a TODO. Read it before running it.
./05-deploy.sh
```

`04-runtime-identity.sh` creates a service account and then stops, because **choosing its
permissions is the exercise**. The application writes objects to one bucket, reads and writes
Firestore documents, and writes logs. Work out the smallest role for each, grant it at the
smallest scope that works, and record one sentence of justification per role.

`roles/editor` will work. It is also the answer that means you cannot say what your service
can do, and band C of the rubric is about exactly that difference.

**No key file is created anywhere in this lab.** The identity is *attached* to the service
and the platform supplies short-lived credentials at runtime. A downloaded service-account
key is a permanent credential sitting in your filesystem, and it is an automatic zero.

Now call the service:

```bash
SERVICE_URL=$(gcloud run services describe docapp --region=us-central1 \
  --project="$PROJECT_ID" --format='value(status.url)')

curl -i "$SERVICE_URL/healthz"                                    # expect 403
curl -i -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
     "$SERVICE_URL/healthz"                                       # expect 200
```

**The 403 is the deployment working.** Every tutorial you will find makes this service public
with one flag. This lab does not, and asks you to say what that flag would have changed —
specifically, who could then reach it, and what your bounded 40-request experiment would
become if anyone on the internet could contribute to it.

**Answer in your submission:** there are two identities in play in the commands above —
the one that *calls* the service and the one the service *runs as*. Name both, say what each
is allowed to do, and explain why conflating them is a mistake.

**Checkpoint.** `/healthz` returns 200 with a token, 403 without, and the response body
carries an `instance_id`.

## Part 3 — Two instances, two answers (~45 min) · **the point of the lab**

`05-deploy.sh` deploys a configuration that is deliberately **half right**. Documents go to
your Lab 3 bucket, so every instance sees the same ones. Job records stay in a dictionary
inside each instance, which is how the application has shipped since week 2. Same code, same
request path, two kinds of state — and only one of them survives a second instance.

Create a document and a job:

```bash
cd ../../../application
TOKEN=$(gcloud auth print-identity-token)

DOC=$(curl -s -X POST "$SERVICE_URL/documents" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: text/plain" \
  -H "X-Document-Name: notes.txt" --data-binary @samples/cloud-intro.txt \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

JOB=$(curl -s -X POST "$SERVICE_URL/jobs" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"document_id\":\"$DOC\",\"operation\":\"wordcount\"}" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')
```

Both succeeded. Now ask forty times at once who has that job:

```bash
python3 tools/instances.py --url "$SERVICE_URL" --path "/jobs/$JOB" \
  --requests 40 --concurrency 20 --header "Authorization: Bearer $TOKEN"
```

The report gives you two things at once: the distinct instances that answered **200**, and
a `<HTTP 404>` count for the ones that had never heard of this job. Save the output.

> **If you get no 404s at all**, only one instance existed — your client did not manage to
> keep twenty requests genuinely in flight, or the platform absorbed them all. Run the same
> command again immediately, while the first instances are still warm. If it still does not
> reproduce, **say so and say why**: a lesson about concurrency that you could not reproduce
> on demand is itself a finding about how hard this class of bug is to catch in testing, and
> it earns full marks when it is honestly reported.

Now the same thing for idempotency. Send the same submission five times with one key:

```bash
for i in 1 2 3 4 5; do
  curl -s -X POST "$SERVICE_URL/jobs" \
    -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -H "Idempotency-Key: retry-me-please" \
    -d "{\"document_id\":\"$DOC\",\"operation\":\"wordcount\"}" \
    | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["id"], d["deduplicated"], d["worker_instance"])'
done
```

**Count the distinct job ids.** More than one means the same work was done more than once, in
response to a client doing exactly the right thing.

**Record what you saw, exactly, then explain it. Three things to be precise about:**

1. Nothing crashed, nothing restarted, no instance is unhealthy, and no log line says
   anything is wrong. What, then, is broken?
2. The document is visible from every instance and the job is not. Both were created by the
   same client against the same service seconds apart. **Why do they behave differently?**
   Read `application/tests/test_two_instances_disagree.py`, which pins this as a test, and
   say what that test's local stand-in for a shared store does **not** reproduce.
3. The duplicate-submission result is the version of this bug that costs money rather than
   returning an error. Say what a user would see, what the operator would see, and which of
   those two is the problem.

Now fix it — and notice that the fix changes **no application code at all**:

```bash
gcloud run services update docapp --region=us-central1 --project="$PROJECT_ID" \
  --update-env-vars="DOCAPP_JOBSTORE=firestore,DOCAPP_PROJECT_ID=${PROJECT_ID}"
```

**Create a new document and a new job** before you re-test. The old job lived in the memory
of instances that no longer exist; it was never written anywhere, so there is nothing for
Firestore to have. Losing it is the same lesson one more time.

Re-run both commands above against the new job.

**Checkpoint.** Forty concurrent status requests, several distinct instances, **zero 404s**.
Five retries with one key, **one job id**, `deduplicated` true for four of them.

**Then answer the question the fix raises:** every status request is now a round trip to
Firestore rather than a dictionary lookup. You have made the application correct and slower.
Estimate the cost per request from your Lab 3 numbers, and say what you would need to
measure before deciding that trade was wrong.

## Part 4 — Concurrency is a design decision (~60 min)

The experiment. **Change one variable; keep everything else fixed.**

```bash
# A: the platform default
gcloud run services update docapp --region=us-central1 --concurrency=80 --project="$PROJECT_ID"
python3 tools/measure.py --url "$SERVICE_URL" --requests 40 --concurrency 20 \
  --header "Authorization: Bearer $TOKEN"
python3 tools/instances.py --url "$SERVICE_URL" --requests 40 --concurrency 20 \
  --header "Authorization: Bearer $TOKEN"

# B: one request per instance
gcloud run services update docapp --region=us-central1 --concurrency=1 --project="$PROJECT_ID"
# ...the same two commands again.
```

**Three runs of each.** Wait for the deployment to finish before measuring, and record the
conditions: concurrency setting, max instances, processing delay, time of day, where you were
sitting.

**Bounds, and they are what keep this lab free:** at most 3 runs per configuration, at most
40 requests per run, client concurrency at most 20, `--max-instances` at most 4.

Now write ~300 words:

1. Which configuration had the lower median latency, and which had the higher throughput?
   If they are not the same configuration, explain why not.
2. How many instances answered in each case? Compare with your Part 0 predictions and
   account for any difference.
3. The application's processing delay is 250 ms of **waiting**, not of computation. Would
   your result be the same if it were 250 ms of arithmetic? Say what you would expect and why
   — this is a prediction, not a measurement, and should be labelled as one.
4. Concurrency 1 gives each request an instance to itself. Name the cost. Then say which
   setting you would ship, for this application, and what evidence would change your mind.

## Part 5 — What a cold start actually is (~30 min)

Leave the service completely alone for **fifteen minutes**. Write up Part 4 while you wait —
the wait is not optional and it is not dead time.

Then:

```bash
python3 tools/measure.py --url "$SERVICE_URL" --requests 5 --concurrency 1 \
  --header "Authorization: Bearer $TOKEN" --json
```

Compare `min` and `max`. Run it again immediately and compare the two reports.

**Answer:** what is the platform doing during the slow request that it is not doing during
the fast ones? List the steps in order. Then: your image is small and has no framework to
load. Name two changes to this application that would make its cold start materially worse,
and one that would make it better.

Finally, the cost question. `--min-instances=1` would remove the cold start entirely. Using
the figures in `operations/cost-model.md`, say what that would cost per month and what you
would need to believe about your users to justify it.

## Part 6 — The comparison, and its limits (~90 min)

You now have measurements of the same application in three places: your laptop (Lab 1), a VM
in Iowa (Lab 2), and managed execution in Iowa (this lab).

Put them in one table with **conditions stated for every row**, then write ~400 words:

1. Where did the time go in each case? Attribute it — network, processing delay, platform
   overhead, cold start — and say which parts of your attribution are measured and which are
   inferred.
2. **What can this comparison not tell you?** The three sets of numbers were taken on
   different days, from different places, possibly on different networks, with code that
   changed in between. Name the confounds specifically. A student who lists four real ones
   and says which would matter most scores higher here than one who reports a clean-looking
   table and no caveats.
3. **Operational responsibility.** For each of: patching the operating system, deciding the
   instance count, handling an instance dying mid-request, and being paged at 3 a.m. — say
   who does it on the VM and who does it on managed execution. Then name one thing that got
   *harder* when you moved, not easier.
4. On the VM you could have run ten instances of this application. The platform will run four
   without being asked. Under what circumstances is the VM still the right answer? Give a
   concrete workload, not a principle.

> **Optional, and it costs about $0.01.** If you want a same-day comparison rather than a
> cross-week one, bring your Lab 2 VM back up with your own scripts, measure it within the
> hour, and tear it down. Declare the cost in your submission. This removes two of the
> confounds from question 2 and you should say which two.

## Part 7 — Teardown and verification (~30 min) · **graded**

```bash
cd ../labs/lab-04/starter
./06-teardown.sh
./07-verify-clean.sh
```

Four things to remove, and only one of them is a running service:

| Resource | Why it is easy to forget |
|---|---|
| Cloud Run service | It is not running. Nothing is being billed. It is still there. |
| **Artifact Registry images** | The one that actually accrues. 0.5 GiB free, and every build adds to it. |
| Bucket and objects | Check versioning again, as in Lab 3. |
| Service account | Costs nothing, grants something. An identity with bucket write access outliving the thing it was made for is a finding, not a tidiness issue. |

Include the `07-verify-clean.sh` output. **Cleanup claimed but not verified earns nothing in
band C.**

---

## What to submit

`lab04-<your-name>.md`, plus the filled-in `04-runtime-identity.sh` and your `config.env`
**with nothing secret in it**.

1. **Part 0 predictions**, written before you ran anything, unedited, with your own account
   of which were wrong and why.
2. **The artefact answers** — tag vs digest, layer order, the non-root user — and the image
   size you recorded.
3. **The roles you granted**, at what scope, one sentence of justification each; plus the
   two-identities answer.
4. **The Part 3 evidence**: the polling output before and after, the idempotency retry
   counts, and your explanation of why nothing had failed.
5. **The Part 4 experiment**: table with conditions, instance counts, and ~300 words.
6. **The cold-start measurement** and the `--min-instances=1` cost answer.
7. **The three-way comparison**, ~400 words, including the confounds and the
   operational-responsibility table.
8. **Teardown verification output.**
9. **Cost estimate vs actual**, each line traced to the allowance covering it.
10. **AI-assistance disclosure.**

## Resource inventory

| Resource | Created by | Removed by | Watch |
|---|---|---|---|
| Cloud Run service `docapp` | `05-deploy.sh` | `06-teardown.sh` | `--min-instances` must be 0 |
| Artifact Registry repo + images | `02`, `03` | `06-teardown.sh` | **0.5 GiB free; rebuilds accumulate** |
| Cloud Storage bucket | `02-create-registry.sh` | `06-teardown.sh` | Object versions, as in Lab 3 |
| Service account + role bindings | `04-runtime-identity.sh` | `06-teardown.sh` | Deleting the account does not always remove every binding — check |
| Firestore `(default)` | Lab 3 | kept; empty the collection | Empty is free; a *named* database is not |
| Cloud Build | `03-build-push.sh` | nothing to remove | 2,500 min/month free; builds also leave logs |

## Troubleshooting

**`403 Forbidden` calling the service, even with a token.** Two different causes. Either your
own account lacks `roles/run.invoker` on the service, or your token expired — they are an
hour long, and a run that starts fine and turns into a wall of failures halfway through is
the second one. Re-run `gcloud auth print-identity-token`.

**`401` mentioning an invalid audience.** An identity token is issued *for* an audience.
If your setup produces one whose audience is not the service, request it explicitly:
`gcloud auth print-identity-token --audiences="$SERVICE_URL"`.

**The revision fails to start, and the logs say `PermissionError` or `Address already in
use`.** The container must listen on `$PORT` and on `0.0.0.0`. Both come from the Dockerfile;
if you changed either, change it back and say why it matters.

**`NotImplementedError: GcsStorage is your Lab 3 exercise`, from the deployed service.** You
built the image from a working tree without your Lab 3 code in it. Rebuild and redeploy —
and note that this is the first time in the course a stale artefact has bitten you. Week 13
is about the machinery that stops it.

**Every request returns 500 after the Part 3 switch.** The runtime service account cannot
reach the bucket or Firestore. That is Part 2's TODO, and the error in the logs names the
permission it wanted. Grant that one, not a bigger one.

**`instances.py` reports one instance when you expected several.** Suspect your own machine
first. If your client cannot keep 20 requests genuinely in flight, the service never sees 20
at once and has no reason to scale. `measure.py`'s throughput figure tells you whether you
managed it.

**The latency numbers are much worse than Lab 3's.** Possibly correct and possibly a
cold start contaminating a small sample. Which of your five requests was slow? That is the
difference between a finding and an artefact, and Part 5 exists to teach you to tell them
apart.

**A build fails with a quota or permission error on Cloud Build.** The API needs a minute to
propagate after `01-enable-apis.sh`. Wait thirty seconds and retry rather than enabling
anything twice.
