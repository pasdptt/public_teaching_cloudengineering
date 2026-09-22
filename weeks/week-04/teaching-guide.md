# Week 4 — Teaching guide: Hierarchy, virtual machines and identity

| | |
|---|---|
| **Outcomes** | CLO-1, CLO-3 |
| **Assessment** | **Quiz 2** (weeks 1–3) |
| **Practical** | **Trial activation** + Lab 2 Parts 1–2 |
| **Prep time** | ~4 h first delivery, ~1.5 h subsequently |

> **This is the highest-risk session in the course.** Ten students activating billing
> accounts at once, some of whom will fail eligibility. Rehearse Part 0 and have the fallback
> path ready to hand out, not to improvise.

## Session objectives

1. Explain why billing and policy attach to a project, and what that buys.
2. Distinguish region from zone as latency floor and blast radius.
3. Describe a cloud VM's parts, including the boot disk as a separate resource.
4. Explain why an idle reserved address costs more than a working one.
5. Explain where a VM's identity comes from and the security consequence.
6. Apply least privilege to a workload identity.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| Hierarchy | 15 | Project as billing and policy boundary; downward inheritance |
| Regions and zones | 15 | Blast radius vs latency floor. **Justify `us-central1` openly.** |
| The VM | 20 | Machine type, image, **boot disk as a separate resource**, metadata |
| **Addresses and the price table** | 15 | Ephemeral vs static. Idle costs double. The stopped-VM trap. |
| Identity | 25 | Principals, roles, service accounts. **Live metadata-token demo.** Default Editor. |
| **Quiz 2** | 15 | Weeks 1–3 |
| **Practical: activation** | 30 | Trial, project, gcloud, **$1 budget alert** |
| Practical: Lab 2 | 45 | Parts 1–2 |

---

## Teaching notes

### Justify the region out loud

Someone will ask why a Bangkok class deploys to Iowa. Answer it properly, because the answer
models the reasoning the course teaches: the Always Free `e2-micro` exists only in three US
regions, so anywhere else is a billed lab; every latency measurement compares against itself,
so a constant offset changes no conclusion; and for a real service serving Thai users the
answer would be different. Cost drove an architecture decision, the decision is recorded, and
its downside is known. That is the whole lesson in one exchange.

### The address price table is the session's best fifteen minutes

Put it up:

| | Rate | 30 days |
|---|---|---|
| Attached to a running VM | $0.005/h | ~$3.60 |
| **Static, attached to nothing** | **$0.01/h** | **~$7.20** |

Ask why idle costs *more*. Let them work it out — scarcity, and a price as a signal. Then the
trap: a static address is "in use" while its VM is stopped, so stopping saves nothing there.

Then say plainly that Lab 2 uses an ephemeral address and deletes the VM, that the address
will change every time, and that they will find this annoying. **Name the annoyance in
advance.** It is exactly the pressure that makes people reserve a static address without
thinking, and a student who has been told to expect it will notice themselves feeling it.

### The metadata demo

If you have a VM up, do it live; otherwise use recorded output and say so.

```bash
curl -sS -H "Metadata-Flavor: Google" \
  http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email
```

Then ask the room: *who put a credential on this machine?* Nobody. Establish that this is
good design — no key to leak, rotate or commit — **and then** ask the consequence: anything
that can run code on the instance gets that identity.

Follow immediately with the project IAM policy showing the default service account holding
Editor. Ask what a remote-code-execution bug would have meant. Do not soften it; Lab 2 Part 4
is the fix and lands much harder after this.

---

## Practical: activation (30 min) — run this tightly

**Before the session:**
- [ ] Re-fetch the trial terms (`course/references.md` R-01, R-02) and update anything stale
- [ ] Have `operations/cloud-access-and-fallback.md` §4 ready to hand out
- [ ] Know which students flagged an eligibility or payment problem in week 1

**In the session, in this order:**

1. Activate. Expect the payment-method authorisation question — say up front that a $0–$1
   pending authorisation may appear for a few days and is not a charge.
2. One project each. Note the id.
3. `gcloud init`.
4. **Budget alert at $1.** Say why $1 and not $150: the whole course costs under a dollar, so
   this alert should never fire, and one at 50% of the credit would only tell them something
   had been wrong for weeks.
5. Say, again: **an alert is a notification, not a cap.**

**Students who cannot activate start the fallback path in this session, at their desk, at the
same time as everyone else.** Not privately afterwards. The design intent is that taking the
fallback costs nothing socially, and that intent is destroyed if they are handled separately.

**Record who activated and on what date.** Their 90 days starts then, and week 15 has to fit
inside it. A student who activated early in week 1 despite being told not to needs a plan
now, not in week 14.

---

## Quiz 2 (15 min, weeks 1–3)

CLO-1, CLO-2, CLO-3 (introductory). Scenarios: attribute an incident; correct a statement
about state durability; explain a container/VM difference; identify what survives a restart.
No service-name recall. Key in the private repository.

---

## Common misconceptions

| Misconception | Surfaces as | Response |
|---|---|---|
| "Stopping the VM stops the cost" | Constantly | Disk, and a static address. Both keep billing. |
| "A static IP is obviously better" | When the ephemeral one changes | Better *and* twice the price when idle, plus an orphan that outlives everything. Ask what habit you need before reserving one. |
| "The free tier means I can't be charged" | Around activation | A discount, not a cap. Over the allowance, billing starts silently at the normal rate. |
| "$300 means I can experiment freely" | Around activation | The labs cost under a dollar. Credit is insurance. No marks for spending. |
| "The service account is just an admin detail" | Before Part 4 | It is the identity your code runs as, and it currently holds Editor. |
| "A budget alert will stop me" | Whenever budgets come up | It emails you. Smoke detector, not sprinkler. |

---

## Practical: Lab 2 Parts 1–2 (45 min)

Expect:
- **Billing not linked to the project** → every create call fails on permissions.
- **New-account quotas** → they have probably created more than one instance.
- **`gcloud compute ssh` slow on first use** — it generates and propagates a key. Tell them to
  wait rather than re-run it five times.
- **The Part 1 "it doesn't work from my laptop" moment.** This is *designed*. Do not rescue
  them. Make them write the prediction first.

End the session by reminding them: delete, do not stop; and the teardown verification is
graded from this lab onwards.

## Links

- Student notes: `weeks/week-04/student-notes.md`
- Lab: `labs/lab-02/README.md` · Rubric: `labs/lab-02/rubric.md`
- Activation checklist: `operations/cloud-access-and-fallback.md` §6
- Rates used in the address block: `operations/cost-model.md` §2
