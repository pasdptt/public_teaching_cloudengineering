---
marp: true
theme: cloudcourse
paginate: true
footer: 'Week 8 · Consolidation'
---

<!--
Logistics deck for week 8. No lecture this week. Derived from course/teaching-guides/week-08.md,
which is authoritative.

Render:  bash course/slides/render.sh 08
-->

<!-- _class: lead -->

# Consolidation

## Week 8

Cloud Computing: Principles and Practice

<!--
TIMING: 180 min total — 15 Quiz 4 · 15 answers · 50 practice · 10 break · 20 trial check · 70 lab clinic. No new material.
Guide: course/teaching-guides/week-08.md
Before you start: Quiz 4 printed. The four practice questions printed, one set per pair (private, exam-papers/). There is no midterm (D-74).
-->

---

## Today

| | | |
|---|---|---|
| **Quiz 4** | 15 min | weeks 5–7 |
| Quiz 4, the answers | 15 min | together, straight afterwards |
| **Practice questions** | 50 min | weeks 1–7, in pairs, not marked |
| Break | 10 min | |
| **Trial and cost check** | 20 min | your own billing page |
| **Lab clinic** | 70 min | Lab 3 left-overs · Lab 4 pre-flight |

No new material this week, and **no midterm**. The final in week 14 covers the whole course.

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:00 – 0:15</span>

# Quiz 4

Weeks 5–7

<!--
CLO-1, CLO-2, CLO-4. Storage, consistency, and what a machine commits you to — including Labs 2 and 3. Moved here from week 9 (D-74); the paper is unchanged. Key in the private repository.
-->

---

<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:15 – 0:30</span>

# Quiz 4, the answers

The mechanism for each question, not the marks

<!--
Collect every paper first. Go question by question and ask for the mechanism. Marked scripts come back in week 9.
-->

---

<!-- _class: block -->

<span class="min">50 minutes</span><span class="clock">0:30 – 1:20</span>

# Practice questions

Weeks 1–7 · the final's four kinds · in pairs · not marked

---

## Four questions, twelve minutes each

**Trace** · **Interpret** · **Predict and explain** · **Choose and defend**

- Answer in pairs, in writing. Then two minutes of answers from the room.
- **A wrong prediction with a sound mechanism is a good answer.** That is how the final marks it.
- At least one is about **your own** system: your Lab 2 VM, or your Lab 3 decision record.

<!--
Different scenarios from the real final. Press for mechanism every time. Twelve minutes, then the room, then the next question.
-->

---

<!-- _class: punch -->

## Before the break, one line: the one thing from weeks 1–7 I could not explain today.

<!--
It goes at the top of their revision sheet for the final. That is what this week's reading budget is for.
-->

---

<!-- _class: block -->

<span class="min">Break — 10 minutes</span><span class="clock">1:20 – 1:30</span>

# Break

Then laptops out

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">1:30 – 1:50</span>

# Trial and cost check

About a third of the way through 90 days

---

## Your own billing page. Three things, out loud.

1. **Credit remaining.**
2. **Days remaining** — and the date your trial ends.
3. **Anything running right now, and why.**

The expected answer to the third is **"nothing"**.

<!--
Record each student's trial end date and check it against planning/calendar-worksheet.md: it must still be alive in week 15. Week 15's guide relies on these dates.
-->

---

<!-- _class: punch -->

## Found something still running? Good. How did it survive the teardown?

<!--
Same treatment as week 15 (D-53): a success, not an embarrassment. Then delete it together and verify with operations/cleanup.md.
-->

---

<!-- _class: block -->

<span class="min">70 minutes</span><span class="clock">1:50 – 3:00</span>

# Lab clinic

No new material

---

## Two lists

**Lab 3 left-overs** — anything your submission recorded that you could not solve. The class issue log first, then one to one.

**Lab 4 pre-flight** — build and run the application in a container, **locally**:

```bash
cd application
docker build -t docapp:local .          # or: podman build
docker run --rm -p 8080:8080 docapp:local
```

A container runtime that stopped working is a week-9 disaster and a week-8 five-minute fix.

<!--
Students with neither may leave. Say so: the session ends when they are ready for week 9.
-->

---

<!-- _class: lead -->

# Next week

Managed containers and serverless

**Lab 4 starts**
