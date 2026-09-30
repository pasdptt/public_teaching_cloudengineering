# Quiz 1 — What makes a cloud

**Covers week 1 only.** Taken in week 2, in the discussion block. Outcomes: CLO-1, CLO-2
(introductory).

**12 marks · about 12 minutes · closed book · individual.** Answer in your own words; short
is fine. Every question asks you to *reason* about a situation — none asks you to recall a
definition, a product name or a price, and a recited definition on its own earns little.

---

## Question 1 — Whose problem is it? (4 marks)

A small company runs its customer portal on **one virtual machine** that it rents from a
cloud provider (infrastructure as a service). In one month, two things happen.

**(a)** An attacker gets in through a known vulnerability in a package installed in the VM's
operating system. A fix for that package had been available for six weeks.

**(b)** A hardware failure in the provider's datacentre stops the VM for 40 minutes. The
portal is unreachable for the whole time.

For **each** incident, say which side of the shared-responsibility boundary it falls on, and
why. If you think the answer is not a single side, say which part belongs to whom.

*(2 marks each)*

## Question 2 — Same incident, different choice (3 marks)

Suppose the company had instead deployed the same portal on a **managed platform**, where
the provider maintains the operating system and runtime and the company supplies only its
application.

1. Would incident (a) from Question 1 land on the same side of the boundary? Explain in one
   or two sentences.
2. Name **one** thing the company gives up by making that choice.

## Question 3 — Correct the colleague (3 marks)

A colleague writes in the team chat:

> "No need to tear down the test server over the holiday. Nobody will be using it, so it
> won't cost anything. And if we ever need more servers, that's what elasticity is for —
> cloud capacity is unlimited."

There are **two** mistaken claims in that message. Identify each one and correct it in a
sentence, saying what the true situation is.

## Question 4 — Why sharing needs less (2 marks)

A cloud provider serves thousands of unrelated customers from one pool of machines.

1. Explain why that pool can be much smaller than the total of what every customer would
   need if each bought machines for its own peak.
2. Describe **one** situation in which that saving would largely disappear.
