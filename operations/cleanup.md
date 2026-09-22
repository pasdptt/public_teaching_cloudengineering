# Cleanup and teardown

The course-wide procedure for removing cloud resources, and for **proving** they are gone.

Two sentences to hold onto:

> Deleting is a command you ran. Verifying is evidence it worked.
>
> The resources that cost you money are the ones you forgot about, not the ones you are using.

From Lab 2 onwards, the verification — not the deletion — is what earns the reproducibility
marks in every lab rubric.

---

## The routine, every time

1. **Inventory before you build.** Each lab lists what it creates. Know the list before you
   need it.
2. **Delete, do not stop.** A stopped VM keeps its disk, and keeps a static address if it has
   one. Deletion is what ends the meter.
3. **Verify.** Run the lab's `verify-clean` script and read the output.
4. **Keep the output.** It goes in your submission.
5. **Check the billing report the next day.** Usage takes time to appear. A lab that looked
   clean on the day and shows charges two days later has taught you something important
   about how metering works.

## What survives a deleted VM

Full table with verified rates in `operations/cost-model.md` §6. The short version, in the
order students actually get caught:

| Resource | Survives | Why it is missed |
|---|---|---|
| **Reserved static external IP** | everything | You deleted the VM; the *address* was a separate resource you reserved. **$0.01/h ≈ $7.20/month** — double the rate of one attached to a running VM |
| **Persistent disk** | the VM, unless auto-delete was set | "The VM is gone" — the disk was a separate resource attached to it |
| **Storage buckets and their objects** | everything | Nothing about deleting compute touches storage |
| **Object versions / soft-deleted objects** | deleting the visible object | Versioning keeps paying for data you believe is gone |
| **Container images in Artifact Registry** | deleting the service | Layers accumulate on every rebuild; the free allowance is 0.5 GiB |
| **Disk snapshots and custom images** | the source disk | — |
| **Pub/Sub subscription with no consumer** | deleting the publisher, and deleting the consumer | Retained messages are billable storage. This is Lab 5's version of the idle IP: the cost comes from something you **stopped** using |
| **Cloud Run with `min-instances > 0`** | having no traffic | It looks idle; it is provisioned |
| **Firestore *named* database** | — | Works identically to the free `(default)` one and qualifies for no free quota at all |
| **A `dev` environment left up while `prod` runs** | attention | Two environments is two of everything, and the free tier allows one |
| **The Terraform state bucket** | every `destroy` | It is the record of the system rather than part of it, so nothing that removes the system removes it. Versioning is deliberately on, so check for old versions too |
| **A Workload Identity Federation pool** | everything | Costs nothing and grants something: a standing trust relationship between a repository and a project. Delete it, or it outlives the course |
| **A service account and its role bindings** | the thing it was created for | Costs nothing, grants something. An identity with write access to a bucket, outliving the service it was made for, is a finding rather than untidiness — and deleting the account does not always remove every binding it appears in |

## Per-lab teardown

| Lab | Script | The one to watch |
|---|---|---|
| 1 | `rm -rf application/data`; `docker rmi docapp:lab1` | Nothing billable. The habit only. |
| 2 | `labs/lab-02/starter/05-teardown.sh` then `06-verify-clean.sh` | Boot disk; any address you reserved |
| 3 | manual — the commands are in the lab | Bucket contents and object versions; the Firestore database |
| 4 | `labs/lab-04/starter/06-teardown.sh` then `07-verify-clean.sh` | **Old images in Artifact Registry** — invisible from the Cloud Run console; also the runtime service account |
| 5 | `labs/lab-05/starter/06-teardown.sh` then `07-verify-clean.sh` | **The subscription, deleted first** — an abandoned one retains messages and bills for them. Also a second service account, and two topics |
| 6 | `terraform destroy` for **each** environment, then verify | State says it is gone; verify independently that it is. Then, in order: registry images, deployer account and WIF pool, and **the state bucket last** |

## Verifying by hand

When a lab's script is not to hand, or you want to check the whole project:

```bash
PROJECT_ID="your-project-id"

gcloud compute instances list        --project="$PROJECT_ID"
gcloud compute disks list            --project="$PROJECT_ID"
gcloud compute addresses list        --project="$PROJECT_ID"   # the expensive one
gcloud compute snapshots list        --project="$PROJECT_ID"
gcloud compute images list           --project="$PROJECT_ID" --no-standard-images
gcloud compute firewall-rules list   --project="$PROJECT_ID"
gcloud storage buckets list          --project="$PROJECT_ID"
gcloud run services list             --project="$PROJECT_ID"
gcloud pubsub subscriptions list     --project="$PROJECT_ID"
gcloud pubsub topics list            --project="$PROJECT_ID"
gcloud artifacts repositories list   --project="$PROJECT_ID"
gcloud firestore databases list      --project="$PROJECT_ID"
gcloud iam service-accounts list     --project="$PROJECT_ID"   # identities outlive their services
```

**Order matters for one pair.** Delete a Pub/Sub subscription *before* the service it pushes
to. The other way round, every retained message is redelivered to an endpoint that returns
404 until the broker gives up — harmless, noisy, and a decent illustration of why teardown is
a sequence rather than a set.

One of these lies to you by omission. `gcloud run services list` shows nothing after Lab 4's
teardown, and the images that lab pushed can still be sitting in Artifact Registry using the
0.5 GiB allowance. A repository that still exists needs its contents checked:

```bash
gcloud artifacts docker images list \
  "${REGION}-docker.pkg.dev/${PROJECT_ID}/docapp" --project="$PROJECT_ID"
```

Empty output from all of these is what "clean" means.

## Check the bill, not just the console

```bash
gcloud billing accounts list
```

Then open the billing report in the console and look at the **daily** view for your project.
Expected shape for this course: flat at zero, with a few cents around Lab 2 and Lab 6.
Labs 4 and 5 should show **nothing at all** — if they do not, the three things to check are
`min-instances`, how much is sitting in Artifact Registry, and whether a subscription is
still holding messages.

A line you cannot explain is the important one. Find out what it is before it becomes a
pattern — the amount will be trivial, and the reason will not be.

## At the end of the course (week 15)

Done together in the session:

1. Teardown of every remaining resource, per the table above.
2. Full verification, with output kept.
3. Confirm the billing report shows nothing accruing.
4. For **paired projects**: revoke the partner's IAM access on the owner's project, and say
   in the submission who did it and when.
5. Leave the trial to expire on its own. It closes without charge, and no upgrade is needed
   — the course never asks anyone to upgrade to a paid account.

## If you find something running

Do not panic and do not hide it. Delete it, then work out **why** it survived:

- Was it created outside a script, by clicking in the console? That is the honest answer more
  often than not, and it is exactly the problem Lab 6's declarative configuration solves.
- Did a teardown script fail partway and you did not read its output?
- Is it a resource type your verification never checked? Add the check.

The amount will be small. The reason is the valuable part, and reporting it costs you
nothing — a student who finds and explains an orphaned resource has demonstrated the skill
the reproducibility band is actually testing.
