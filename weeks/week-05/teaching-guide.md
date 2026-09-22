# Week 5 — Teaching guide: Virtual networking and access boundaries

| | |
|---|---|
| **Outcomes** | CLO-3 |
| **Assessment** | **Lab 2 due** at the end of this week, including graded teardown verification |
| **Practical** | Lab 2 Parts 3–6 |
| **Prep time** | ~3.5 h first delivery, ~1 h subsequently |

## Session objectives

1. Describe a VPC, subnet, route and firewall rule, and that the default is deny.
2. **Diagnose from the symptom**: distinguish a refused connection from a dropped packet and
   infer where the packet died.
3. Explain the two boundaries — what the process accepts, and what the network delivers.
4. Justify a firewall source range, and distinguish a lab answer from a production one.
5. Explain what a load balancer does and which week-3 problem it still has.
6. Verify a teardown rather than assert one.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| VPC, subnets, routes | 15 | Software-defined networking. The global-VPC quirk, named as a real difference. |
| Firewall rules | 25 | Allow-lists, default deny, source ranges, **target scoping** |
| **Two boundaries** | 25 | `DOCAPP_HOST` vs the rule. **The refused-vs-hung demo.** |
| Public and private | 10 | Private-only as a default for things that need no inbound traffic |
| Load balancing | 15 | Stable front door, health checks — and the same slow-vs-dead problem |
| Discussion | 30 | Architecture exercise: narrow an over-permissive design |
| Practical | 60 | Lab 2 Parts 3–6, ending with verified teardown |

**180 minutes exactly.** 90 concepts · 30 discussion · 60 practical. No break row: take one inside the firewall block, which is the longest.

---

## Teaching notes

### The refused-vs-hung demo is the centre of the session

Rehearse it. Do it live if you have a VM up; use recorded output otherwise and say which.

```bash
# nothing listening, packet allowed through -> immediate refusal
curl --max-time 10 http://<ip>:9999/healthz

# something listening, packet dropped by the firewall -> hangs, then times out
curl --max-time 10 http://<ip>:8080/healthz    # with the rule removed
```

Ask *before* running each: fast error, or long wait? Take the split. Then give the rule that
makes it permanent:

> **Refused means something answered. Hung means nothing did.** A firewall that drops your
> packet does not send an apology.

This single distinction saves students more time across the rest of the course than anything
else in week 5. Say it, demonstrate it, and put it on the board for the practical.

### Two boundaries, drawn once

Draw the packet's journey and mark the two gates: the firewall (does the packet arrive?) and
the listening socket (is anything there to receive it?). Ask what breaks if you remove each,
and insist the answers differ. Students who merge these into "the network config" will fight
Lab 4 and Lab 6 for no reason.

### Load balancing back to week 3

After the health-check explanation, ask: *how does the balancer know a backend is dead?* It
does not. It waits and guesses, exactly as they did in week 3. The callback is worth the
thirty seconds — it shows that the hard problem does not go away, it just gets a budget and a
default value.

---

## Discussion (30 min): narrow this design

On screen: a VM with a public address, a firewall allowing `0.0.0.0/0` on ports 22, 80, 443,
8080 and 5432, the default service account with Editor, and a database on the same instance.

Small groups, ten minutes: list every change you would make, in order of how much risk each
removes per unit of effort.

Expected, roughly in order: close 5432 entirely (the database needs no public ingress at all);
replace Editor with a scoped role; narrow 22 to a known range or remove it in favour of a
managed access path; scope the rules by target tag rather than network-wide; question whether
the instance needs a public address at all.

The point is not the list. It is **ordering by risk removed per unit of effort** — which is
what a real security review is, and what the project's security band asks for in week 15.

---

## Common misconceptions

| Misconception | Surfaces as | Response |
|---|---|---|
| "The firewall is the only thing controlling access" | All session | Two boundaries. Remove either and it breaks, differently. |
| "A hang and a refusal are both 'it's broken'" | In the practical | The demo. Different symptoms, different causes, different fixes. |
| "`0.0.0.0/0` is fine, it's only a lab" | In Part 2 | Fine *if chosen and justified*. The lab grades the justification, not the value. |
| "GCP VPCs are like AWS VPCs" | When someone has prior experience | Global with regional subnets. A genuine structural difference. |
| "Private instances can't reach the internet" | In the public/private block | Outbound through a gateway is fine. It is *inbound* they cannot receive. |
| "The teardown script printed no errors, so it's clean" | At submission | Then show me the verification output. That is the graded artefact. |

---

## Practical (60 min): Lab 2 Parts 3–6

Watch for:

- **Part 3's metadata observation passing unnoticed.** If nobody reacts to "no credential was
  placed on this machine", stop the room and ask the question directly.
- **Part 4 stopping the instance** to change the service account — the external IP changes,
  and a student who has not read ahead thinks they have broken something. The script warns
  them; some will not read it.
- **Part 5 single runs.** Insist on three. The variation is the finding.
- **Part 6's `TODO`.** Students will want the answer to which three resources survive a
  deleted VM. Point them at `operations/cost-model.md` §6 rather than telling them.

**Before anyone leaves:** every student runs `06-verify-clean.sh` and shows you clean output.
Do not let a room full of running instances go home for the weekend — this is the single
cheapest intervention in the whole cost model.

Check the billing report at the start of week 6. Anyone over $1 has left something running,
and that is a conversation to have immediately.

## Links

- Student notes: `weeks/week-05/student-notes.md`
- Lab: `labs/lab-02/README.md` · Rubric: `labs/lab-02/rubric.md`
- Teardown procedure: `operations/cleanup.md`
- Next week: storage abstractions; Lab 3 moves state off the machine
