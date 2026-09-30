# Quiz 7 — Delivery, environments, and what you are committed to

**Covers weeks 11–13**, including Lab 6. Taken in week 14 — the architecture-synthesis
material taught earlier in that session is **not** assessed here; the questions draw on the
system you built in Labs 5 and 6. Outcomes: CLO-6, CLO-7, CLO-8, CLO-9.

**15 marks · about 13 minutes · closed book · individual.** Short answers are fine. Where a
question asks about *your* system, answer about the one you actually built.

This is the only quiz that assesses CLO-8, so Questions 5 and 6 carry more weight than their
length suggests.

---

## Question 1 — Same source, same image? (2 marks)

A team's pipeline builds `docapp:latest` on every merge and deploys it to `dev`. On Thursday
a separate job builds `docapp:latest` again **from the same commit** and deploys it to `prod`.
On Friday `prod` misbehaves in a way `dev` never did.

1. Why is "it was the same commit" not evidence that `dev` tested what `prod` is running?
   *(1 mark)*
2. What can the team now not establish, and what change to the pipeline would have made it
   establishable? *(1 mark)*

## Question 2 — The forked workflow (2 marks)

Your `deploy.yml` is in a public repository and names your federation pool and your deployer
account. Someone forks the repository and runs the workflow in their fork.

1. What stops their run from deploying into your project? *(1 mark)*
2. Suppose instead the workflow had authenticated with a service-account key stored as a
   repository secret. Name **one** property of that key that makes its eventual leak worse
   than a leak of the pool name. *(1 mark)*

## Question 3 — State (3 marks)

1. A teammate deletes a bucket's block from the configuration and applies. Explain how the
   tool knows to **destroy** the bucket rather than simply do nothing. *(1 mark)*
2. A pipeline with no backend configured deploys successfully on its first run and fails on
   its second with "already exists". Explain why. *(1 mark)*
3. The fix stores state in a bucket. Why must that bucket be created by hand rather than by
   the configuration that uses it — and in teardown, when is it deleted? *(1 mark)*

## Question 4 — An error budget (2 marks)

Your service has an SLO with a 30-day error budget. With **two weeks** of the window left, the
budget is fully spent. A product owner wants to ship a large, risky change tomorrow.

What should the team do, and what is the error budget *for* — beyond being a number that ran
out?

## Question 5 — What would leaving cost? (4 marks)

Your organisation asks what it would take to move the system you built in Labs 5 and 6 to a
different cloud provider next year.

1. Name **two** design ideas in your system that would transfer unchanged, and say why each
   one does. *(2 marks)*
2. Name **two** things in your system that are commitments to *this* provider — be specific
   to what you built, not general. *(1 mark)*
3. Which single migration step would you expect to be hardest, and why? *(1 mark)*

## Question 6 — Defend a decision (2 marks)

A reviewer looks at your Lab 6 configuration and says:

> "`dev` and `prod` share one database. That is a design flaw."

In three to four sentences, respond: say whether you agree, what the compromise actually is
and what it risks, why it was made, and what you would change given more budget.
