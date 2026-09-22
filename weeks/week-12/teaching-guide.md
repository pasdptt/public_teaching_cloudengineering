# Week 12 — Teaching guide: Declarative infrastructure and environments

| | |
|---|---|
| **Outcomes** | CLO-7, CLO-9 |
| **Assessment** | **Quiz 6** (CLO-5, CLO-6; CLO-7 and CLO-9 **through the threads only** — cleanup since Lab 2, CI since week 3 — never that day's Terraform material) |
| **Practical** | Lab 6 Parts 1–3 |
| **Prep time** | ~4 h first delivery, ~1.5 h subsequently |

> **Restructured 2026-09-22 (D-24).** Lab 6 is a two-week lab covering delivery and
> environments as one subject. This week is its first half.

## Session objectives

1. Distinguish imperative from declarative provisioning by what each one *records*.
2. Explain what state is, why the tool cannot work without it, and what it contains.
3. Define drift, produce it deliberately, and say who decides which side is right.
4. Argue for a specific difference between `dev` and `prod`, and — harder — for a specific
   sameness.
5. Distinguish configuration from secrets, and say why a committed secret is permanent.
6. Produce a cost estimate **before** deploying, and say which allowance covers each line.

---

## Session plan (180 minutes)

| Block | Min | Content |
|---|---|---|
| Imperative vs declarative | 20 | Their own Lab 2–5 scripts, against `infra/main.tf` |
| **State, and what is in it** | 25 | Why it must exist. Then open one and find a secret. |
| Drift | 15 | Produced deliberately in the practical; framed here |
| Break | 10 | |
| **Environments** | 25 | What may differ, what must not, and who decides |
| Config vs secrets | 10 | Why "we removed it in the next commit" is not a fix |
| **Quiz 6** | 15 | CLO-5, CLO-6, and the two threads |
| Practical | 60 | Lab 6 Parts 1–3 |

**180 minutes exactly.** 95 concepts · 15 quiz · 60 practical, plus the break.

> Cost estimation has no block of its own. It is Lab 6 Part 6 and it is exercised in the
> practical; the concepts were taught in week 4 and have been a thread ever since. Adding a
> block here would mean cutting one that has nowhere else to go.

---

## Teaching notes

### Open with their own scripts

Put `labs/lab-02/starter/01-create-vm.sh` on one side of the screen and a slice of
`infra/main.tf` on the other. Ask what each one *is*.

Draw it out: the script is a list of **steps**, and it records what you did. The Terraform
file is a **description of the result**, and it records what you want. Then the question that
matters:

> Run the script twice. What happens? Run the Terraform twice. What happens?

The script fails, or worse, makes a second thing. The Terraform does nothing, because the
world already matches the description. **That is idempotency** — the same word they met in
week 10, applied to infrastructure instead of to messages, and it is worth naming the
connection explicitly. A desired-state description is idempotent for the same reason "set the
balance to 400" is and "add 100" is not.

Then the honest cost of declarative, which tutorials skip: you have to describe everything,
including the things you would have done by hand without thinking; the tool has opinions about
ordering that are sometimes wrong; and you now have a state file to look after.

### State: why it must exist, and what is in it

Ask the question that makes it necessary:

> Terraform's job is to make the world match the file. You delete a resource from the file.
> How does it know to destroy something, rather than doing nothing?

Let them get there: it must remember what it made. That memory is the **state file**, and it
is a JSON record of every managed resource and its attributes.

Then the two consequences, in order of how much trouble they cause:

**One.** Whoever holds the state holds the truth. Two people with two local state files each
believe they own the infrastructure and neither is told otherwise. That is why real teams put
state in a shared backend with locking, and why the `backend "gcs"` block in `versions.tf` is
commented out with a note rather than absent.

**Two, and do this live.** State contains the *values* of everything it manages. Open one and
scroll. Every output, every attribute, and — if anything sensitive ever passed through
Terraform — that too, in plain text.

> **A secret that goes through Terraform is a secret written to the state file.** Marking a
> variable `sensitive` hides it from the console output. It does not remove it from state.

That single sentence is the most practically dangerous thing in the week and it should be
delivered with the file open.

### Drift, in one demonstration

Define it as the gap between the description and the world, then say where it comes from:
somebody clicked something. Not malice — an incident at 2 a.m. and a console.

They will produce it deliberately in the practical. What to set up here is the question the
practical asks:

> `terraform plan` now says it will change your service back. Which is right — the console or
> the file?

Let the room argue. The useful answer is that **neither is automatically right**: the file is
right if you have decided the file is authoritative, and that is an organisational commitment,
not a property of the tool. What the tool gives you is *visibility* of the disagreement.

Then push once more: what if two people each believe theirs is the truth? That is not a
Terraform question at all, which is the point.

### Environments: the second list is the hard one

Start with what may differ, and collect answers — instance counts, log levels, retention.
Easy, and everyone can do it.

Then flip it, and give this plenty of room because it is the assessed skill:

> Name three things that must be **identical** between dev and prod, and say what breaks if
> each drifts apart.

Expect to have to pull the first one out of them. The answers worth reaching: **the container
image** (or dev tested something prod never runs), **the region** (or you have measured the
wrong latency and the wrong bill), and **the shape of the configuration itself** — if prod is a
copy of `main.tf` with edits, then the edits are differences nobody declared.

> **An undeclared difference is why "it works in dev" happens.**

Then the trap this course's own configuration contains, which is better than any invented
example. Dev and prod share **one Firestore database**, because there is one free `(default)`
database per project. The bucket is separated, the topic is separated, the service is
separated — and the data is not. Ask what that means for a student testing a destructive
change in dev.

The real answer is a project per environment. Say so, and then say what stops this course
doing it: a second project means a second free tier only if it is a second *billing account*,
and it is not. **This is a cost constraint producing an architectural compromise**, which is
the most realistic thing in the whole lab.

### Config versus secrets, briefly

A project id is configuration. A password is a secret. The test is not "is it sensitive" but
**"what happens if this appears in a public repository?"**

Then the part students underestimate:

> You commit a key, notice, and remove it in the next commit. Is it gone?

No. It is in the history, in every clone, in every fork, and quite possibly in a search index
within minutes. **The only fix is to rotate the credential**, and the cleanup is cosmetic.

Tie it back to D-01 — this course has two repositories for exactly this reason — and forward
to week 13, where the pipeline needs an identity and the whole design exists to avoid having a
long-lived credential to leak.

---

## Quiz 6 (15 min)

Covers **CLO-5 and CLO-6** — asynchrony, idempotency, failure, evidence — and touches CLO-7
and CLO-9 **only through the threads students have been living with**: cleanup since Lab 2,
and CI since week 3.

**It must not assess today's Terraform material.** That was a real defect found in an earlier
audit and corrected; the principle is that a quiz assesses what students have practised, not
what they heard ninety minutes ago.

---

## Common misconceptions

| Misconception | Surfaces as | Response |
|---|---|---|
| "Terraform is a deployment tool" | Constantly | It makes the world match a description. Deployment is one use. |
| "The state file is a cache" | State block | Delete it and watch it offer to build everything again. It is the only record that the world is yours. |
| "`sensitive = true` protects a secret" | Secrets block | It hides console output. State still has the value. |
| "Drift means someone did something wrong" | Drift block | It usually means someone fixed an incident at 2 a.m. The tool shows the disagreement; it does not settle it. |
| "Dev and prod differ, that's the point" | Environments block | They differ in the few ways you chose. Every other difference is a bug you have not met yet. |
| "We'll use `latest` in dev and pin in prod" | Environments block | Then dev tested something prod will never run. |
| "Two environments means two of everything" | Firestore trap | Not when the free tier is per project. Show them the table. |
| "I removed the key in the next commit" | Secrets block | It is in every clone. Rotate it. |
| "`terraform destroy` means it's gone" | Practical | It means the tool believes so. Verify independently — `operations/cleanup.md`. |

---

## Practical (60 min): Lab 6 Parts 1–3

- **Part 1 is reading, and it is worth protecting.** Fourteen resources, and every one of
  them is something they built by hand in Labs 3–5. Have them find the two Pub/Sub
  service-agent grants specifically — in Lab 5 those cost the room twenty minutes and an error
  message, and here they are four lines that will be right every time. That comparison is the
  argument for the whole week, and it lands better than any slide.
- **`terraform` is no longer in Homebrew** (it is BUSL-licensed now). `brew install opentofu`
  and `tofu` is a drop-in for everything this lab does — it is what the configuration was
  validated with. Say this at the start rather than during ten separate install failures.
- **`init` downloads a provider.** On a room's worth of laptops and one wireless network,
  start it early.
- **The service is private**, so a plain `curl` returns 403 and several students will report it
  as broken. Say once, to the room, that it is correct and that the invoker `TODO` is the fix.
- **Make everyone produce drift before they leave.** It takes two minutes — change
  `max-instances` in the console, re-run `plan` — and it is the single most memorable thing in
  the week.
- **Watch for the wrong workspace.** `terraform workspace show` before every apply. A student
  who applies prod's variables into dev's workspace will see a plan full of destroys, and the
  correct response is to read the plan and stop, which is exactly the habit the lab is for.

End by pointing at what is still missing: they have a description of an environment and they
are still typing `apply` by hand. That is week 13.

## Links

- Student notes: `weeks/week-12/student-notes.md`
- Lab: `labs/lab-06/README.md` · Rubric: `labs/lab-06/rubric.md`
- Configuration: `infra/` — read `infra/README.md` first, including its validation status
- Cost: `operations/cost-model.md` · Cleanup: `operations/cleanup.md`
- Quiz 6 key: private repo, `quiz-keys/`
