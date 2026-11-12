# Publishing checklist

This repository is **public**. Its git remote is a public GitHub repository. Everything in
its history is visible, permanently, including files that were deleted in a later commit.

Decision D-01: instructor material lives in a **separate private repository**,
`../cloudengineering-instructor`. This file is how that separation stays true over time.

---

## The rule that matters

> **Deleting a secret in a new commit does not remove it.** It remains in the object
> history and in every clone and fork. A leaked answer key is leaked for the life of the
> repository; a leaked credential must be **rotated**, not deleted.

An `instructor/` folder inside a public repo is not protection. It is a label.

---

## Never in this repository

- Quiz answer keys, expected answers, or partial-credit guidance
- Lab reference solutions, or starter code with the answer left in a comment or a stub body
- Grading guidance that reveals expected answers
- Service-account keys, API keys, tokens, `.tfvars`, `.env`, or any credential
- Terraform state files (they can contain resource identifiers and occasionally secrets)
- Real project IDs, billing account IDs, or account email addresses
- Student names, IDs, submissions, grades, or any personal information
- Fabricated deployment evidence, invented measurements, or example costs presented as real

## Fine in this repository

- Lab briefs, rubrics, and starter code with clearly marked student-authored sections
- Weekly teaching guides (D-12) — they contain no assessable answers, and publishing them
  helps other instructors
- Quiz **student versions**
- Terraform configurations with placeholder variables and a `.tfvars.example`
- Cost estimates labelled as estimates, with region and retrieval date
- Illustrative data explicitly labelled `ILLUSTRATIVE — NOT MEASURED`

---

## The automatic gate

Run this **once per clone**. Git does not copy hook settings when a repository is cloned:

```bash
git config core.hooksPath .githooks
```

After that, every commit and every push runs `planning/leakcheck.py` and is refused if it
finds private material. The check has three parts:

1. **Paths.** It refuses `exam-papers/`, `quiz-keys/`, `lab-solutions/`, `midterm*.md`,
   `exams/final.md` and `*-key.*`.
2. **Content.** It refuses answer-key, solution and marking-key headings, and credentials.
3. **Fingerprint.** It compares this repository against the private one beside it:
   - any line of 40 or more characters from a key, paper or set of notes is refused;
   - any file holding most of a reference solution's code is refused.

`audit.py` runs the same check as check 4.

The fingerprint catches text **copied** across, not the same fact **reworded**. In November
2026 it found Lab 1's reference measurements in `progress.md`. The same numbers, worded
differently, were also in the week 10 speaker notes, and only a manual grep found those. So
when you summarise private material here, describe it ("the reference run is in the private
repository"); do not quote it.

The fingerprint step is skipped, with a note saying so, on any machine without the private
repository beside this one. The path and content checks still run.

## Before every push

```bash
# 1. What is actually staged?
git status
git diff --cached --stat

# 2. Nothing that looks like an answer or a credential
git diff --cached -G'(?i)(answer|solution|marking scheme|expected answer)' --stat
git diff --cached -G'(BEGIN [A-Z ]*PRIVATE KEY|"private_key"|AIza[0-9A-Za-z_-]{20,}|ya29\.)' --stat

# 3. No credential-shaped files
git diff --cached --name-only | grep -Ei '\.(tfstate|tfvars)$|credential|service-account|\.env$|\.pem$|\.key$' || echo "clean"

# 4. The ignore rules are still doing their job
git check-ignore -v instructor/ 2>/dev/null || echo "WARNING: instructor/ is not ignored"
```

A grep is a safety net, not a substitute for knowing what you are committing.

## Confirm the repository's actual visibility

Do not infer it from the name, and do not infer it from whether a page loads for you — a
fetch can 404 for reasons that have nothing to do with the repository. Ask the API:

```bash
gh repo view pasdptt/public_teaching_cloudengineering --json visibility,pushedAt
```

`PUBLIC` means every rule in this file is live right now. `PRIVATE` means the rules still
apply, because the day it flips public the whole history flips with it — but it also means
students cannot clone it yet, which is worth knowing before you hand out the URL.

Check this at the start of each offering. It takes one command and it is the assumption
everything else here rests on.

## Before the repository is first made public, or before a new offering

- [ ] Visibility confirmed with `gh repo view ... --json visibility` (above), not assumed
- [ ] `git log --all --name-only | sort -u` reviewed for anything that should never have
      been added — **including files deleted later**
- [ ] No quiz key, solution or credential appears anywhere in history
- [ ] `application/` and `infra/` contain no real project IDs or account identifiers
- [ ] Every cost figure carries a retrieval date and is labelled an estimate
- [ ] Every measurement is either real and attributed, or labelled `ILLUSTRATIVE — NOT MEASURED`
- [ ] Starter code stubs contain a `TODO`, not a commented-out solution
- [ ] `planning/progress.md` reflects reality, including what has *not* been validated
- [ ] The private instructor repository is still **private**, visible to its owner only:
      `gh repo view pasdptt/private_teaching_cloudengineering_int --json visibility` says `PRIVATE`,
      and `gh api repos/pasdptt/private_teaching_cloudengineering_int/collaborators --jq '.[].login'`
      lists only the owner. Its own pre-push hook refuses any push to a repository that is
      not private (enable it per clone: `git config core.hooksPath .githooks`).

## If something sensitive was committed

1. **If it is a credential: rotate it first.** Immediately. Before anything else. Removing
   it from history does not un-expose it.
2. Rewrite history with a tool built for it (`git filter-repo`, or BFG). `git rm` does not
   remove the object.
3. Force-push, and tell everyone with a clone that they must re-clone — an old clone still
   contains the object.
4. If the repository was public and the content was an answer key, **treat the affected
   assessment as compromised** and replace it. Rewriting history does not retract what was
   already downloaded, indexed or forked.
5. Record what happened in `planning/decisions.md`, so the next person understands why a
   quiz was replaced.

---

## Pushing workflow files needs an extra permission

A token that can push code **cannot** push `.github/workflows/` unless it is told so
separately. The push is rejected with:

```text
! [remote rejected] main -> main (refusing to allow a Personal Access Token to create or
  update workflow `.github/workflows/ci.yml` without `workflow` scope)
```

Nothing is written when this happens — fix the credential and push again.

| Credential | What to do |
|---|---|
| Classic token | Add the **`workflow`** scope alongside `repo`. Scopes are editable on an existing token; no need to regenerate. |
| Fine-grained token | Set the **Workflows** repository permission to *Read and write*, alongside Contents. |
| SSH key | Nothing. SSH has no scopes, so workflow files push normally. |
| `gh auth login` | Recent versions request the workflow scope during login. |

Worth pointing out to students when it happens to them, because it is the course's own
lesson arriving uninvited: a credential scoped to exactly what it was asked for refused to
do something adjacent. That is least privilege working, not failing — and it is the same
reasoning behind Lab 6 giving its pipeline a federated identity with narrow roles instead of
a key that can do anything.

## Producing a clean student package

Students normally just clone this repository — it is already student-safe by construction,
which is the point of the two-repo split. If a snapshot is needed for an LMS or an offline
distribution:

```bash
# Snapshot of the current commit, no git history at all
git archive --format=zip --prefix=cloud-course/ HEAD -o cloud-course-student.zip

# Verify the archive contains nothing unexpected
unzip -l cloud-course-student.zip | grep -Ei 'instructor|solution|key|answer|tfstate|tfvars|\.env' \
  || echo "archive clean"
```

`git archive` exports only the tree at that commit, with no history — which is what makes
it safe as a distribution format even though this repository's history is clean anyway.

## Keeping the two repositories in step

| Change | Where it goes |
|---|---|
| Lab brief, rubric, starter code | public |
| Lab reference solution and teaching notes | private, `lab-solutions/lab-NN/` |
| Quiz paper (what students sit) | private, `quizzes/` — printed for the room (D-71) |
| Quiz key with reasoning and partial credit | private, `quiz-keys/` |
| Exam papers, keys, and the final practice set | private, `exam-papers/` |
| Weekly teaching guide | public, `weeks/week-NN/` (D-12) |
| Delivery notes, prep and grading time estimates | private, `delivery-guide.md` |
| Real measurements from a pilot run | private, `pilot-evidence/` |
| Cost estimates | public — they are estimates, and students need them |
| Observed actual spend from a pilot | private |

When a lab changes, its solution usually changes too. Update both in the same working
session, and note it in `planning/progress.md`. A solution that has drifted from its lab is
how an instructor ends up marking against the wrong expectations.
