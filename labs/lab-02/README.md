# Lab 2 — Compute and networking

**Weeks 4–5 · 7.5% of the final grade · Individual submission**

| | |
|---|---|
| **Cloud resources** | One `e2-micro` in `us-central1`, 10 GB standard disk, one firewall rule, one **ephemeral** external IP, one service account |
| **Estimated cost** | **~$0.04** — the IP address, at $0.005/hour. Everything else is Always Free. |
| **Outcomes** | CLO-3 (tracing a request across network and identity boundaries), CLO-1 |
| **Estimated novice time** | ~2 h guided (2 × 60 min) + ~5 h independent over two weeks |
| **Observed pilot time** | *not yet measured* |

> **This is the first lab that spends money, and the first with a graded teardown.** Four
> cents is not a risk. The habit is the point: from here to week 15, every cloud lab ends
> with you proving that nothing is left running.

---

## Why this lab exists

In Lab 1 everything was on your machine, and "can I reach it?" was never a question. Now the
application runs somewhere else, and between you and it are an address, a route, a firewall,
and an identity. Each of those either lets your request through or does not.

By the end you will be able to point at a request and say, at every hop: **what permitted
this, and who is it acting as?** That is CLO-3, and it is the skill that makes cloud
debugging possible rather than superstitious.

## Before you start

- [ ] Week 1's environment check passes.
- [ ] Lab 1 submitted.
- [ ] **Do not activate your trial before the week 4 session.** Ninety days has to reach week
      15. Part 0 is done together, in class.
- [ ] If you cannot get a trial — eligibility, payment method, or a previous account — tell
      the instructor **now**. The fallback path starts in the same session as everyone
      else's, not quietly a week later.

---

## Part 0 — Activate, and set your guardrails (~30 min, in class)

Done together in the week 4 session.

1. Activate the Google Cloud Free Trial. $300, 90 days, a payment method for identity
   verification only. **Charging requires a manual upgrade to a paid account, which this
   course never asks you to do.**
2. Create one project. Note its id — you will type it a lot.
3. Install the `gcloud` CLI and run `gcloud init`.
4. **Set a budget alert at $1.**

Why $1, when you have $300? Because your entire course is expected to cost under a dollar. An
alert at $1 should never fire. An alert at $150 would tell you something had been wrong for
weeks.

**Say this back to yourself before moving on:** a budget alert is a **notification, not a
cap**. It stops nothing. The things that actually control your spend are staying inside the
free tier, bounding your experiments, deleting what you create, and verifying.

**Checkpoint:**

```bash
gcloud config list                      # your project and account
gcloud billing accounts list            # your trial billing account
```

---

## Part 1 — Put the application on a machine you do not own (~60 min)

Starter scripts are in `starter/`. They are **incomplete on purpose** — the `TODO` blocks are
your work, and each one is a decision rather than a missing command.

```bash
cd labs/lab-02/starter
cp config.env.example config.env     # then edit: your project id
./01-create-vm.sh
```

**Checkpoint.** `gcloud compute instances list` shows one `RUNNING` instance, machine type
`e2-micro`, zone in `us-central1`.

Three constraints are not style preferences — break any one and you leave the free tier:

| Constraint | Why |
|---|---|
| Exactly **one** `e2-micro` | Always Free covers one per month per **billing account** |
| Region `us-central1` | The allowance exists only in `us-west1`, `us-central1`, `us-east1` |
| **Ephemeral** external IP, never a reserved static one | A reserved unattached address costs **$0.01/h — double** an attached one |

Then deploy and start the application:

```bash
./02-deploy.sh
```

**Checkpoint.** SSH to the instance and confirm it is listening locally:

```bash
gcloud compute ssh docapp-vm --zone "$ZONE" --command 'curl -sS http://127.0.0.1:8080/healthz'
```

That works. Now try it from your laptop, using the external IP. **It will not work yet.**
Before you investigate, write down why you think it fails. There are at least two plausible
reasons and only one of them is the actual one.

## Part 2 — Open exactly one door (~45 min)

**Predict first, in writing:**

1. The application is listening and healthy on the instance, but unreachable from your
   laptop. Name the two most likely causes and say which you would check first, and how.
2. You will create a firewall rule allowing TCP 8080 from `0.0.0.0/0`. Name one thing that
   becomes true the moment that rule exists which was not true before.
3. You will then narrow the rule to your own IP address only. What would still be able to
   reach the service, and what would not?

Now complete and run `03-firewall.sh`. Its `TODO` asks you to decide the source range.

**Checkpoint.** From your laptop:

```bash
curl -sS "http://$EXTERNAL_IP:8080/healthz"
```

Then change one variable and observe:

```bash
./03-firewall.sh --source-range "$(curl -sS https://api.ipify.org)/32"   # only you
curl -sS "http://$EXTERNAL_IP:8080/healthz"                             # still works?

./03-firewall.sh --source-range "198.51.100.0/24"                       # a range you are not in
curl -sS --max-time 10 "http://$EXTERNAL_IP:8080/healthz"               # now what?
```

**Record:** what each attempt did, and **exactly how the failure presented**. A refused
connection and a hung connection are different symptoms with different causes, and telling
them apart is most of network debugging. Which did you get, and what does that tell you about
where the packet died?

**The question to answer properly:** `DOCAPP_HOST` is `0.0.0.0` on the VM. There is also a
firewall rule. Both are involved in whether you can reach the service. Explain what each one
does, and why removing either would break it — in terms of the boundary each controls, not
which command sets it.

## Part 3 — Trace the path, and name the identity (~45 min)

Follow one request from your laptop to the application and back. For **each** hop, record two
things: **what rule permitted it**, and **which identity it acted as**.

```bash
# Where does the name resolve, and where do the packets go?
curl -sS -o /dev/null -w 'connect=%{time_connect}s total=%{time_total}s\n' \
     "http://$EXTERNAL_IP:8080/healthz"

# The instance's own view of itself
gcloud compute instances describe docapp-vm --zone "$ZONE" \
  --format='yaml(name, machineType, networkInterfaces, serviceAccounts)'

# What identity is the code on that machine actually running as?
gcloud compute ssh docapp-vm --zone "$ZONE" --command \
  'curl -sS -H "Metadata-Flavor: Google" \
    http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email'
```

That last one is worth pausing on. **Nobody put a credential on that machine**, and yet code
running there has an identity and can get a token for it. Work out where that identity comes
from and what would happen if someone else could run code on the same instance.

**Record:** the full path — your machine, DNS/address, the internet, the VPC's external
address, the firewall rule, the instance, the listening socket, the process — with the
permitting rule and the acting identity at each hop. A short annotated list is fine. Not a
screenshot.

## Part 4 — Give it less than it was given (~40 min)

Look at what your instance's service account can do:

```bash
gcloud projects get-iam-policy "$PROJECT_ID" --format=json \
  | python3 -c "import json,sys; [print(b['role'], b['members']) for b in json.load(sys.stdin)['bindings']]"
```

The default Compute Engine service account typically holds **Editor** on the whole project.
Your application, at this point in the course, reads and writes nothing in Google Cloud at
all. It needs **nothing**.

Complete `04-service-account.sh`: create a dedicated service account, give it only
`roles/logging.logWriter`, and attach it to the instance.

**Checkpoint.** The metadata query above now returns your new service account, and the
application still works.

**Questions to answer:**

1. Your application needed no permissions. Why is attaching an identity with almost none
   better than attaching one with none at all?
2. The default account had Editor. Describe concretely what an attacker who found a remote
   code execution bug in your application could have done with that, and what they can do now.
3. This is the shared-responsibility boundary from week 1, made specific. Which side was the
   default-Editor configuration on, and who would have been accountable?

## Part 5 — The experiment (~45 min)

**Change one variable. Measure. Explain.**

You measured this application on your laptop in Lab 1. Now measure it across a continent —
**the same tool, the same settings**, so the only thing that changed is the distance.

```bash
# On the VM, over loopback: no network between client and server
gcloud compute ssh docapp-vm --zone "$ZONE" --command \
  'cd /opt/docapp/application && python3 tools/measure.py \
     --url http://127.0.0.1:8080 --requests 12 --concurrency 1'

# From your laptop, across the internet
python3 application/tools/measure.py \
  --url "http://$EXTERNAL_IP:8080" --requests 12 --concurrency 1
```

Run each **three times**. Then repeat both at concurrency 4.

**Record** a table: location, concurrency, wall time, throughput, p50, p95 — with
`DOCAPP_PROCESSING_DELAY_MS` and your own location stated.

**Explain, in about 200 words:**

1. How much latency did the network add? Compare it with what you would predict from the
   physical distance. (Light in fibre covers roughly 200 km per millisecond, and the route is
   not a straight line.)
2. The configured processing delay is identical in both runs. So which part of the measured
   latency is the application, and which is the network? Show the arithmetic.
3. At concurrency 4, does the *network* portion behave like the *processing* portion did in
   Lab 1? Explain what you see.
4. Decision D-18 puts these labs in `us-central1` because that is where the free tier lives,
   even though you are not. Using your numbers: what does that choice cost you, and why is it
   still the right trade for this course? What would change your answer for a real service?

Do not guess at numbers you did not observe. A run that failed is reported as a run that
failed.

## Part 6 — Take it all down, and prove it (~30 min) · **graded**

```bash
./05-teardown.sh
./06-verify-clean.sh
```

`06-verify-clean.sh` is incomplete. Its `TODO` is to check every resource class this lab can
create — and the interesting ones are the resources that **survive a deleted VM**.

**Include the full output of the verification in your submission.** Claiming cleanup is not
verifying it, and from this lab onwards the difference costs marks.

### The cost lesson, in numbers you can check

This lab used an **ephemeral** IP and **deleted** the VM rather than stopping it. Here is what
you avoided (rates verified 2026-09-21, `course/references.md` R-09):

| Situation | Rate | Over 30 days |
|---|---|---|
| IP attached to a **running** VM | $0.005/h | ~$3.60 |
| IP attached to a **stopped** VM — if it is **static** | $0.005/h | ~$3.60 |
| **Static IP reserved, attached to nothing** | **$0.01/h** | **~$7.20** |

**An address doing nothing costs twice an address doing work.** And a *static* IP counts as
"in use" while its VM is merely stopped, so "I stopped the VM, I'm not paying" is wrong twice
over. An **ephemeral** IP is in use only while the instance runs, and disappears when you
delete it — which is why the lab is written the way it is.

**Answer this:** you now want your service to keep the same address across restarts, so a
static IP is genuinely the right choice. What operational habit must you adopt the moment you
reserve one?

---

## What to submit

`lab02-<your-name>.md`, plus your completed starter scripts. Short and precise.

1. **Predictions** from Part 2, written before you ran anything.
2. **Reachability** — why it failed at first, how the failure presented at each firewall
   setting, and your `DOCAPP_HOST` / firewall-rule explanation.
3. **Path trace** — every hop, with permitting rule and acting identity.
4. **Least privilege** — your three answers from Part 4.
5. **The experiment** — your table and ~200-word explanation.
6. **Resource inventory, teardown and the verification output.**
7. **Your cost estimate for this lab**, computed before you deployed, compared with what the
   billing report actually shows. Explain any difference.
8. **AI-assistance disclosure.**

## Resource inventory

| Resource | Created by | Removed by | Bills after the VM is gone? |
|---|---|---|---|
| `e2-micro` instance | `01-create-vm.sh` | `05-teardown.sh` | — |
| Boot disk, 10 GB | with the instance | with the instance, **if the delete rule says so** | **yes, if it survives** |
| Ephemeral external IP | with the instance | released with the instance | no |
| Firewall rule | `03-firewall.sh` | `05-teardown.sh` | no, but it is a standing hole |
| Service account | `04-service-account.sh` | `05-teardown.sh` | no |
| Logs | automatically | retention expiry | inside the 50 GiB free allowance |

## Troubleshooting

**`gcloud: command not found`** — the CLI is not installed or not on PATH. Part 0.

**`Required 'compute.instances.create' permission`** — wrong project selected, or billing not
linked. `gcloud config list`.

**`Quota exceeded`** — new trial accounts have low initial quotas. You need one very small
VM; if you are hitting a quota you have probably created more than one, or asked for a larger
machine type. List what exists before requesting more.

**`curl` hangs with no response** — a packet is being dropped, not refused. Firewall rule is
the first suspect: check the source range and that the rule targets your instance.

**`Connection refused` immediately** — something answered. The route and the firewall are
fine; the application is not listening where you think. Check `DOCAPP_HOST` and that the
process is running.

**SSH fails** — `gcloud compute ssh` generates a key on first use and can take a minute to
propagate. Try once more before investigating.

**The external IP changed after I recreated the VM** — correct, and expected. It is
ephemeral. That is the trade you accepted to avoid the reserved-address charge.

**Anything else** — class issue log first. One person's solved problem is everyone's.
