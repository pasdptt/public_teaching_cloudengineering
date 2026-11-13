---
marp: true
theme: cloudcourse
paginate: true
footer: 'Week 8 · Midterm'
---

<!--
Logistics deck for week 8. No lecture this week. Derived from course/teaching-guides/week-08.md,
which is authoritative.

Render:  bash course/slides/render.sh 08
-->

<!-- _class: lead -->

# Midterm

## Week 8

Cloud Computing: Principles and Practice

<!--
TIMING: 180 min total — 120 exam · 10 break · 20 trial check · 30 lab clinic. No new material.
Guide: course/teaching-guides/week-08.md
Before you start: papers counted, the room's clock visible, this deck on the wall during the exam showing the rules slide.
-->

---

## Today

| | | |
|---|---|---|
| **Midterm** | 120 min | weeks 1–7 · Labs 1–3 |
| Break | 10 min | |
| **Trial and cost check** | 20 min | your own billing page |
| **Lab clinic** | 30 min | Lab 3 left-overs · Lab 4 pre-flight |

No new material this week.

---

<!-- _class: block -->

<span class="min">120 minutes</span><span class="clock">0:00 – 2:00</span>

# Midterm examination

Weeks 1–7 · Labs 1–3 · 60 marks

---

## The rules

- **120 minutes.** Papers are collected at 2:00, exactly.
- **Allowed:** one A4 sheet of your own handwritten notes, both sides.
- **No devices.** Phones and laptops closed and away.
- Where a question asks about **your** system, answer about the one you actually built.
- **A wrong prediction with a sound mechanism earns most of the marks.** Show the mechanism.

<!--
Leave this slide on the wall for the whole exam. Call 30 minutes and 10 minutes remaining.
-->

---

## Roughly a mark a minute

60 marks in 120 minutes leaves time to **read every question first**.

If a question seems to need a service name, a price or a console path, you are reading it wrong — none of them does.

---

<!-- _class: block -->

<span class="min">Break — 10 minutes</span><span class="clock">2:00 – 2:10</span>

# Break

Then laptops out

---

<!-- _class: block -->

<span class="min">20 minutes</span><span class="clock">2:10 – 2:30</span>

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

<span class="min">30 minutes</span><span class="clock">2:30 – 3:00</span>

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

**Quiz 4** · **Lab 4 starts**
