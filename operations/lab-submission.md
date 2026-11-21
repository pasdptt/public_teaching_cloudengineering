# Handing in labs and the project

Every lab, and the project, is handed in the same way: **a Markdown write-up in your private GitHub repository,
and a link to one commit of it, turned in on its assignment in Microsoft Teams.** The
write-up is what is marked. The commit link is what fixes it in time.

This page is the how. *What* each lab asks for is in that lab's **What to submit** section,
and how it is marked is in its `rubric.md`. The project's differences (one repository for a
pair, a proposal first) are in [section 7](#7-the-project). If git itself is new to you, read
[GitHub 101](github-101.md) first. Section 3 of it sets up the repository this page assumes.

---

## The short version

1. Write `submissions/lab-0N/README.md` in your private repository, with one `##` section
   for each numbered item in the lab's **What to submit** list.
2. Commit it, together with the code the lab had you change, and `git push`.
3. Run `python3 operations/check_submission.py N`. Fix anything it reports, push again, and
   run it again until it prints a link.
4. In Teams, open the lab's assignment and paste that link (**+ Add work → Link**). Then
   press **Turn in** before the deadline.

---

## 1. One repository, private, for the labs and the project

All six labs are done in **one repository**: your private copy of the course, set up once in
week 1 ([GitHub 101, section 3](github-101.md#3-get-your-own-copy)). The labs build on each
other. Lab 3 changes the application Lab 1 started, and Lab 6 deploys what Lab 4 containerised,
so they belong in one history.

- **Private**, not a fork. A fork of a public repository is always public, so classmates
  could read your work while the lab is still open.
- **The instructor is a collaborator.** This is GitHub user `pasdptt`, unless the Teams class
  team says otherwise. Without access, your link opens a 404 page for the marker. That counts
  as nothing handed in.
- **Keep it, and keep the access, until final grades are out.** Do not delete the repository,
  rename it, or remove the instructor. Do not rewrite history you have already handed in
  (section 6).

## 2. Where things go

```text
cloudengineering/                      your private repository
├── application/ …                     code the labs have you change — commit it where it is
├── weeks/week-NN/lab-0N/starter/ …    starter scripts you fill in — commit them where they are
├── infra/, .github/workflows/ …       Lab 6's Terraform and pipeline — where they are
└── submissions/
    ├── TEMPLATE.md                    the course's skeleton: copy it, do not edit it
    ├── lab-01/
    │   ├── README.md                  ← your Lab 1 write-up
    │   └── ci-red-run.png             ← an image, if you use one (optional)
    ├── lab-02/
    │   └── README.md
    ├── …
    └── project/                       ← section 7
```

- **One folder per lab, and the write-up is always `README.md`.** GitHub then shows it
  automatically when the folder is opened, so the link you hand in opens on your write-up.
- **Leave code where the lab put it.** Do not copy `jobstore.py` into `submissions/`. Link to
  it from the write-up instead. A copy can drift away from the code that actually ran.
- **Do not put your name in file names.** Teams already knows who handed it in.

## 3. Writing the write-up

Start from the template:

```bash
mkdir -p submissions/lab-01
cp submissions/TEMPLATE.md submissions/lab-01/README.md
```

Then replace its headings with the lab's own **What to submit** list: one `##` heading per
numbered item, in the same order, with the same numbers. The marker reads the write-up next to
the rubric, so the order is what lets them find each item. A missing heading looks like a
missing item.

**Evidence is text, not screenshots.** Paste the command and what it printed in a fenced
block, so it can be read, searched and checked against a re-run:

````markdown
```console
$ curl -s http://127.0.0.1:8080/healthz
{"status": "ok", "instance_id": "a1b2c3"}
```
````

- **Measurements go in a table, with units and conditions.** Say what you varied, what you
  held still, and what machine or service you ran it on.
- **Link to code by its path**, relative to the write-up, rather than pasting the whole file.
  Paste only the lines you are discussing:

  ```markdown
  My `put` writes the whole file each time ([`jobstore.py`](../../application/docapp/jobstore.py),
  `FileJobStore.put`), so …
  ```

- **Images only to illustrate**, never as the only evidence. Put them in the lab's folder and
  link them relatively: `![The red run](ci-red-run.png)`. A CI run can simply be linked, since
  the marker can open runs in your repository.
- **Short beats long.** Every rubric rewards precision, not length. If a lab gives a word count,
  treat it as a ceiling.
- **The AI-assistance disclosure is the last section, every time**, as the course policy asks.

### Predictions: commit them before you run anything

Every lab asks for predictions written *before* the experiment, unedited. Git can prove the
order. As soon as they are written, commit and push:

```bash
git add submissions/lab-01/README.md
git commit -m "Lab 1 predictions, before Part 3"
git push
```

Then do not change that section again. If a prediction was wrong, the explanation section
says so. That is where the marks are. The commit is your evidence that the prediction came
first, and in the write-up you can link to it (`git log --oneline` shows its id).

## 4. What must not be in the repository

This is the same list as [GitHub 101, section 6](github-101.md#6-what-must-never-be-committed),
with two additions that are specific to write-ups:

- **No credentials, anywhere in the repository**, not only in the write-up. That covers key
  files, API keys, passwords, and **identity tokens** (the long `eyJ…` strings from Lab 4).
  A token expires, but while it is valid it works for anyone who has it, and the rubrics treat
  it as a leaked credential. Show that a request worked by its status line and response body,
  not by the token that made it.
- **No personal paths or account details** in pasted output. Replace
  `/Users/yourname/…` or `C:\Users\yourname\…` with `~/…`. The **project id** may stay. It is
  configuration, not a secret, and the marker needs it to read your teardown evidence.

A private repository is not a safe for secrets. The instructor can read it, and so can anyone
you add later, or everyone, if you ever make it public.

## 5. Check it, then hand it in

From the repository root, with the lab number:

```bash
python3 operations/check_submission.py 1
```

It checks, without changing anything:

- that `submissions/lab-01/README.md` exists;
- that it has a section for each item in the lab's **What to submit** list;
- that its relative links point at files that are committed;
- that the write-up and the code are committed, and that the commit has been **pushed**;
- that nothing in the repository looks like a credential or a token;
- that the write-up has no personal home-directory paths;
- that `origin` is your own repository rather than the course's, and (if the GitHub CLI is
  installed) that it is **private**.

When everything passes, it prints the link to hand in:

```text
https://github.com/YOUR-USERNAME/cloudengineering/tree/3f9c2a1…/submissions/lab-01
```

That link names one **commit**, not the repository's latest state. It shows exactly what was
there when you handed it in, and nothing you push afterwards changes it. That is why you hand
in this link rather than the repository's front page.

**In Teams:**

1. Open the class team → **Assignments** → the lab.
2. **+ Add work → Link**, paste the link, and give it the name `Lab 1 write-up`.
3. Press **Turn in** before the deadline shown on the assignment.

**Changing it before the deadline:** push the fix and run the check again for a new link.
In Teams, press **Undo turn in**, replace the link, and turn in again. **Only the link turned
in at the deadline is marked.** Anything pushed afterwards is not, even if it is in the same
repository.

The deadline is the one on the Teams assignment. Late work follows the course's policy as the
instructor announces it.

## 6. After you hand it in

- **Do not rewrite history you have handed in.** That means `git push --force`, a rebase over
  it, or deleting the branch. The commit must still exist when it is marked. If it has gone,
  there is nothing to mark.
- **Keep working in the same repository.** The next lab builds on this one. Handing in a
  commit does not freeze anything else.
- **Teardown evidence belongs to the lab it tears down.** If you only verify a teardown after
  handing in, add the output to the write-up and hand in again, as long as it is still before
  the deadline.

## 7. The project

The project is handed in the same way, at two points: the **proposal** at the end of week 12
and the **final submission** at the end of week 15. The [milestones](../weeks/week-11/project/milestones.md)
say what each one contains.

**Which repository.** Your lab repository. The project deploys through your Lab 6 pipeline,
and that pipeline trusts one repository by name, so the project has to live where the
pipeline does.

**Pairs share one repository: the owner's.** The owner is the student whose cloud project the
pair uses, and so whose Lab 6 pipeline deploys it.

- **The owner adds the partner as a collaborator** (Settings → Collaborators), but only
  **after Lab 6 has been handed in**, so that neither of you sees the other's open lab work.
- **The partner clones the owner's repository** into a separate folder, so their own lab
  repository stays as it was:

  ```bash
  git clone https://github.com/OWNER/cloudengineering.git cloudengineering-project
  ```

- **Each of you commits under your own name**, from your own laptop, with no shared account
  ([GitHub 101, section 2](github-101.md#2-one-time-setup-15-minutes)). The history then shows
  who built what. Link those commits from your contribution record.
- **Run `git pull` before you start, and push often.** Two people pushing to one `main` will
  meet the *fetch first* message ([GitHub 101, section 10](github-101.md#10-when-git-says-no)).

**Where things go:**

```text
submissions/project/
├── proposal.md            week 12: the template from the milestones, filled in
├── README.md              week 15: one numbered section per "What you submit" item in the brief
└── architecture.png       the diagram, if it is an image (or a Mermaid block in README.md)
```

The **architecture diagram** can be an image in the folder, linked from the write-up, or a
fenced `mermaid` block inside it, which GitHub draws as a diagram. Code, Terraform and the
pipeline stay where they are, as in the labs. Item 3 links the commits that built the
extension.

**Check and hand in:**

```bash
python3 operations/check_submission.py proposal   # week 12 → the "Project proposal" assignment
python3 operations/check_submission.py project    # week 15 → the "Project" assignment
```

The project check reads the brief's **What you submit** list. It requires item 10, the
contribution record, only from a pair.

**Pairs: both of you turn in the same link**, each on your own Teams assignment. Teams records
hand-ins per student, so if only one of you turns it in, the other has handed in nothing.

After the design review in week 13, the smallest version goes at the top of `proposal.md`,
with the date, as the milestones ask. Commit and push it. It is not handed in again. Your
teardown output from week 15 goes in item 9 of the final write-up.

## 8. When something goes wrong

| Problem | What to do |
|---|---|
| The check says the commit is **not pushed** | `git push`, then run the check again |
| `remote: Repository not found` when pushing | The `origin` address is mistyped, or git is logged in as someone else. Run `git remote -v`, then follow [GitHub 101, section 2](github-101.md#2-one-time-setup-15-minutes) |
| The check says `origin` is the **course repository** | You cloned the course but never connected your own repository. Follow [GitHub 101, section 3](github-101.md#3-get-your-own-copy), steps 3–5 |
| The check reports a **credential** | Do not just delete the line. Revoke the credential first (GitHub 101, section 6), then remove it, then tell the instructor |
| GitHub is down at the deadline | Commit anyway, and run the check. It still prints the link, marked *not pushed*. Turn that link in, then push as soon as GitHub is back. The commit id shows the content was fixed in time |
| The marker cannot open your link | Settings → Collaborators: is the instructor listed, and did they accept? Is the link to *your* repository? |

Still stuck? Post in the class issue log, with the check's full output. It contains no secrets.
