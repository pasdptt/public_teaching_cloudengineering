# Week 1 — Teaching guide: What makes a cloud

| | |
|---|---|
| **Outcomes** | CLO-1 (characteristics, service models, shared responsibility) |
| **Assessment** | None. Quiz 1 next week covers this material. |
| **Practical** | Environment check + first local run. Ungraded, but every student must complete it. |
| **Prep time** | ~3 h first delivery, ~1 h subsequently |

## Session objectives

By the end of the session a student can:

1. Explain statistical multiplexing as the economic reason clouds exist.
2. Name the five NIST characteristics and say what each one *costs* as well as what it buys.
3. Place a workload on the IaaS/PaaS/serverless spectrum by asking who operates what.
4. Given a described incident, attribute it across the shared-responsibility boundary and
   justify the attribution.
5. Start the course application locally and describe what it does.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| Opening | 10 | What the course is and is not. The one-application promise. |
| The problem | 20 | Pre-cloud capacity planning. Build to the peak. Statistical multiplexing. |
| Five characteristics | 25 | NIST's five, each with its consequence |
| **Metering, properly** | 15 | Provisioned ≠ used. The idle-IP example. Why teardown is graded. |
| Break | 10 | |
| Service models | 20 | The stack, and who operates each layer |
| Shared responsibility | 20 | The rule, then three worked incidents |
| **Discussion** | 30 | Incident attribution exercise (below) |
| **Practical** | 60 | Environment check, first run, troubleshooting |

Quizzes replace part of the discussion block in weeks 2, 4, 6, 8, 10, 12 and 14. This week
the discussion block is intact.

---

## Teaching notes

### Open with the problem, not the definition

Resist starting with "cloud computing is…". Start in 2003 with a room full of servers bought
for a peak that happens twice a year. Let the class work out that the cost is the idle
capacity. Then ask: *who has the most idle capacity in the world?* — and let them arrive at
the answer themselves. The definition lands afterwards as a description of something they
have already reasoned their way into.

Worked example to have ready: two shops, one busy at 9am in Bangkok and one at 9am in São
Paulo. Each needs 100 servers at peak. Separately: 200 machines. Together: nearer 110. Put
the numbers on the board — students remember arithmetic they watched happen.

### Metering deserves its own block

This is the part that has a consequence in every remaining week, and it is the part students
skim. Make it concrete with the real figures from `operations/cost-model.md` §2:

- an external IP on a running VM: **$0.005/hour**
- the same address **reserved and attached to nothing**: **$0.01/hour**

Ask why a provider would charge *more* for the idle one. (Addresses are genuinely scarce;
the price is a signal.) Then make the point that lands: *the resources that cost you money
in practice are the ones you forgot about, not the ones you are using.* This is why every
lab ends in teardown and why the teardown is worth marks.

### Service models: ask the question, not the acronym

Draw the stack once and keep it up. For each model, shade who operates what. The takeaway
sentence is: **you operate less and you control less, always both.** Ask for a case where
you hand over the work and keep the control. There isn't one. That absence is the whole
trade-off.

### Shared responsibility

Give the rule — "of the cloud" versus "in the cloud" — then immediately test it on the three
incidents in the student notes. Do the first one together, then put the other two to the
room.

The one to spend time on is the zone outage: **both** attributions are true. The provider
owns the outage; the customer owns having designed for one zone. Students want a single
answer and there isn't one. Getting comfortable with that is the actual skill, and it comes
back in week 11.

---

## Discussion exercise (30 min)

Four incidents on a slide. Small groups, five minutes each, then whole-room.

1. A storage bucket with confidential files was readable by anyone on the internet.
2. A zone lost power; every service in it stopped for four hours.
3. A guest OS vulnerability on a VM was exploited three weeks after the patch was published.
4. A managed database was unreachable for 20 minutes during a provider maintenance window
   that was announced a month in advance, and the customer's application had no retry logic.

Expected: (1) customer, unambiguously. (2) both, in different senses. (3) customer on IaaS,
provider on a managed runtime — *the same incident moves across the line depending on an
architecture choice*. (4) the trap: the outage is the provider's, the *impact* is the
customer's, because the announcement and the missing retry were both theirs.

Number 4 is the best of the four. It gets at the idea that a provider's stated behaviour is
part of your design inputs, not an excuse.

---

## Common misconceptions

| Misconception | How it surfaces | Response |
|---|---|---|
| "The cloud is just someone else's computer" | Offered as a joke, believed as an analysis | True and useless. The interesting part is the *pooling* and the *API*, neither of which is a property of someone else's computer. |
| "Elastic means unlimited" | In the characteristics discussion | Ask what happens when everyone scales up at once. Then mention quotas, which they will meet in week 4. |
| "Idle resources are free" | Constantly | The IP example. Twice the price for doing nothing. |
| "Serverless means no servers" | Whenever the word appears | Someone else's servers, allocated per request. Ask who patches them — that is the actual difference. |
| "The provider handles security" | In the responsibility exercise | Incident 1. It was their permissions system, correctly enforcing what the customer configured. |
| "I'll use the $300 to try things" | Around the trial discussion | Reframe: the labs cost under a dollar. Credit is insurance, not budget. Marks are never given for spending. |

---

## Practical block (60 min)

Every student runs:

```bash
python3 operations/check_environment.py
```

**This is the purpose of the week.** The course's planning assumptions say students have
Windows or macOS machines with permission to install Python and container tooling. That is an
assumption, not evidence. This block turns it into evidence while there is still time to act.

Circulate. Expect, in rough order of frequency:

1. Python not on PATH (Windows, installer checkbox missed) — reinstall with the box ticked,
   or switch them to WSL2 now rather than later.
2. No container runtime — a WARN, not a blocker. Point at `operations/student-setup.md` and
   move on; it is not needed until Lab 1.
3. `pip3` refusing to install into an externally-managed environment — venv, as documented.
4. Corporate or campus network blocking outbound HTTPS — a WARN. Note who, and check again
   before week 4, when it will matter.

**Record who failed what.** If more than two students cannot run containers, decision D-10
needs revisiting before Lab 1 and the fallback path becomes the main path for them.

### Also in this block

- Say out loud: **do not activate a cloud trial before week 4.** Say why — 90 days has to
  reach week 15. Expect at least one student to have already signed up; note them, and plan
  around a trial that expires early rather than pretending it will not.
- Ask openly: *does anyone expect a problem with eligibility or a payment method?* Ask it as
  ordinary logistics, in the same breath as asking about laptops, so that saying "that's me"
  costs nothing socially. Handling it now is the difference between a supported alternative
  path and a student quietly falling behind in week 4.

---

## Links

- Student notes: `weeks/week-01/student-notes.md`
- Environment check: `operations/check_environment.py`
- Setup: `operations/student-setup.md`
- Cost figures used in the metering block: `operations/cost-model.md` §2
- Next week: processes, isolation, containers — and Quiz 1 on this material
