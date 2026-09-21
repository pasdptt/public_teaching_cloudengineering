# Week 1 — What makes a cloud

These notes teach the week's content. If you missed the session, read this plus the assigned
reading and you will not be behind.

**Reading:** NIST SP 800-145, *The NIST Definition of Cloud Computing* (Mell & Grance, 2011).
Three pages. <https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-145.pdf>

---

## The problem that made clouds

Before you can say what a cloud *is*, it helps to know what it replaced.

Suppose in 2003 you wanted to launch a website. You estimated your peak traffic, bought
enough servers to handle it, found somewhere to put them, and waited weeks for delivery.
Three things followed from that, and all three are uncomfortable:

- **You paid for the peak, all the time.** Your Black Friday capacity sat idle in February.
- **Being wrong was expensive in both directions.** Too few servers and you turned customers
  away. Too many and you had bought furniture.
- **The lead time was weeks.** An idea you could not test for six weeks was, in practice, an
  idea you did not test.

Now notice something about the organisations that had the most servers. Amazon's fleet was
sized for December. Google's for whatever the web threw at it. They had the same problem at
a much larger scale — and at that scale, a fourth fact appears: **the peaks of many
independent customers do not happen at the same time.** If your busy hour is 9am in Bangkok
and mine is 9am in São Paulo, one pool of machines can serve us both with far less hardware
than two private fleets.

That is called statistical multiplexing, and it is the economic engine under everything else
in this course. Everything that follows — the APIs, the elasticity, the pricing — is
machinery for selling access to a shared pool.

## Five characteristics

NIST names five. They are worth knowing not because definitions are interesting but because
each one is a *claim* the provider is making, and each claim has consequences you will meet
in a lab.

**On-demand self-service.** You can get a server without asking a human. That is why
infrastructure can be created by a script, which is why Lab 6 exists, and which is why
"I created it by clicking around in the console and now I can't remember how" is a real and
common failure.

**Broad network access.** Capacity is reached over a network by standard mechanisms. Which
means the network is now part of your application, and Lab 2 is about tracing it.

**Resource pooling.** Many customers share the same physical hardware. You do not know which
machine you are on, and that is the deal. Your "virtual machine" is a slice of something
larger — which is where week 2's virtualization material comes in.

**Rapid elasticity.** Capacity can grow and shrink quickly, and can appear unlimited. Note
*appear*. It is not unlimited, it takes real time to arrive, and the delay between "we need
more" and "more has arrived" is the source of a surprising amount of misbehaviour. Week 9.

**Measured service.** Usage is metered, and therefore billed.

That last one deserves more than a sentence, because it is the one students underestimate.

> **A resource that is provisioned is metered, whether or not anyone is using it.**

An idle virtual machine costs the same as a busy one. A disk you forgot about costs money
every hour. And — a real example you will meet in Lab 2 — a reserved IP address that is
attached to *nothing* costs **twice as much** as one attached to a running server. The
provider charges you more for wasting a scarce resource than for using it.

This is why every lab in this course ends with a teardown step, and why the teardown is
graded.

## Service models: who operates what

IaaS, PaaS, SaaS. The acronyms are less useful than the question underneath them:

> **Which parts of this stack do I operate, and which does someone else operate?**

Take a stack from the bottom up: building and power, hardware, hypervisor, operating system,
runtime, your application, your data, and who is allowed to touch it.

- **Infrastructure as a Service** — the provider operates up to the hypervisor. You get an
  operating system and everything above it. You patch it. You configure it. Lab 2.
- **Platform / container as a Service** — the provider also operates the OS and the
  scheduler. You supply a container image and a port. Lab 4.
- **Serverless / functions** — the provider operates everything up to your code. You supply
  a function.
- **Software as a Service** — you supply data and configuration. Gmail.

Moving up the list, you operate less and control less. Both at once, always. There is no
option where you hand over the work and keep the control, and a great deal of bad
architecture comes from people who believed there was.

## Shared responsibility

This is the most practically important idea in week 1, so here it is as a rule you can apply:

> The provider is responsible for the security **of** the cloud. You are responsible for
> security **in** the cloud.

Concretely, at IaaS level: the provider is responsible for the datacentre, the hardware, the
hypervisor, and for the *availability* of the service as described. You are responsible for
your operating system patches, your firewall rules, your access policies, your application,
and your data.

The line moves as you move up the service models. At PaaS the provider takes over OS
patching. At SaaS they take nearly everything — but never your data, and never who you gave
access to.

Three cases to reason about — these are the kind you will see in Quiz 1:

1. *A storage bucket with confidential files was readable by anyone on the internet.* Whose
   responsibility? **Yours.** The provider gave you a permissions system and you configured
   it to allow that. This is the single most common cloud data breach, and it is never the
   provider's fault.
2. *A whole datacentre lost power and services in that zone stopped.* The **provider's**
   responsibility for the outage. But if your design assumed one zone would never fail, the
   consequences to your users are **yours**. Both statements are true at once, and being
   able to hold both is the actual skill.
3. *An unpatched vulnerability in your virtual machine's operating system was exploited.*
   **Yours** on IaaS. On a managed platform where the provider maintains the runtime, theirs.
   The same incident lands on different sides of the line depending on a choice you made
   earlier.

Notice what case 3 really says: **the service model you pick decides what you are on the
hook for.** That is an engineering decision with a security consequence, not a procurement
detail.

## What the trial gives you, and what it does not

You will activate a Google Cloud Free Trial in **week 4**, not before. $300 of credit, valid
for 90 days from *your* signup — which is precisely why activating early is a bad idea. The
window has to reach week 15.

Two things to hold onto now:

- **This course is designed to cost you nothing.** Every lab fits inside Google's *Always
  Free* tier. Expected total spend for the whole course is under a dollar, and the only item
  that reliably costs anything is an IP address in Lab 2, at half a cent an hour. The $300 is
  a buffer against mistakes, not a budget.
- **A free tier is a discount, not a cap.** Going over an allowance does not stop anything;
  it starts billing, quietly, at the normal rate. This is why you will be asked, in every
  cloud lab, to say *which* allowance covers what you built and *what would take you outside
  it*. "It's free" is not an answer.

If you cannot get a trial — no eligibility, no suitable payment method, or you have used one
before — **say so in week 1**. There is a documented local path that covers the same
assessed material, and you are not disadvantaged in grading. Do not create a second account
to regain eligibility; that breaches Google's terms and is not something this course asks of
anyone.

## The application you will build on

One application, all semester. It stores a text document, runs a small operation on it, and
reports the result. Today it runs on your laptop and keeps everything locally. By week 12 it
will be containerised, deployed, scaled, asynchronous, reproducible from code, and
completely removable — and you will have measured it at each step.

Start it:

```bash
cd application
python3 -m docapp
curl http://127.0.0.1:8080/healthz
```

There is nothing to install. See `application/README.md` for why that was a deliberate
choice, and what it buys.

## This week's work (~180 minutes)

| | |
|---|---|
| Read NIST SP 800-145 | 30 min |
| Run the environment check and fix what it reports | 30 min |
| Run the application, try each endpoint, read `application/README.md` | 60 min |
| Read `course/syllabus.md` properly, including the cost section | 30 min |
| Skim `labs/lab-01/README.md` so you know what is coming | 30 min |

Nothing is graded this week. The environment check is not optional anyway: it is how we find
out, while it is still cheap, whether your machine can do what the course needs.

## Check yourself

1. Why do many customers sharing one pool of machines need less hardware than each owning
   their own?
2. "Rapid elasticity means capacity is unlimited." What is wrong with that sentence?
3. Your colleague says an idle VM is free because nobody is using it. Correct them in one
   sentence.
4. At IaaS level, who patches the guest operating system? At PaaS?
5. A misconfigured bucket exposes customer data. Whose responsibility, and why?
6. Why are you told not to activate the cloud trial before week 4?

## Next week

Week 2 opens the box: what a process actually is, what isolates one from another, and how
virtual machines and containers differ. Lab 1 starts, and Quiz 1 covers this week's material.
