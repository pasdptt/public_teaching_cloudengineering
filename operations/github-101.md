# GitHub 101 — just enough git for this course

**Self-reading. It is not taught in a session and it is not assessed.** Read it if git is new
to you, or if you have only ever used it by clicking buttons. If you already push to GitHub
every week, do [section 3](#3-get-your-own-copy) anyway, because this course uses a private
copy rather than a fork. Then skim the [never commit](#6-what-must-never-be-committed) and
[course-specific traps](#9-traps-specific-to-this-course) sections and stop there.

**Time:** about 45 minutes, best done in week 1 alongside the environment check, and in any
case before Lab 1 starts in week 2. Every lab is written up and handed in from the repository
you set up in section 3.

**What you will be able to do afterwards:** get your own private copy of the course on GitHub,
save and upload your work, watch the tests run on every push, pick up corrections to the course
material, look over your own change before anyone else sees it, and undo the common mistakes
without making them worse.

---

## 1. Two words: git and GitHub

- **git** is a program on your laptop. It records snapshots of a folder (*commits*), so you
  can see what changed, when, and go back. It works offline.
- **GitHub** is a website that stores a copy of a git folder (a *repository*, or *repo*) and
  adds things around it: a web view, pull requests, and **GitHub Actions**, which runs this
  course's tests every time you push.

The course uses them for three things: Lab 1 Part 6 makes the test suite run on every push
(week 3), Lab 6 deploys your service from a pipeline that runs on GitHub (week 13), and your
project lives in the same repository.

## 2. One-time setup (15 minutes)

**Check git is installed.** It is part of the environment check, or:

```bash
git --version          # any 2.x is fine
```

**Tell git who you are.** These two values are stamped on every commit you make. Use the
private address GitHub gives you rather than your personal email: on GitHub, open
*Settings → Emails*, tick *Keep my email addresses private*, and copy the address that looks
like `12345678+yourname@users.noreply.github.com`.

```bash
git config --global user.name "Your Name"
git config --global user.email "12345678+yourname@users.noreply.github.com"
```

**Let git log in to GitHub.** GitHub does not accept your account password from git. The
simplest route is the GitHub CLI (<https://cli.github.com>), which sets up a login that git
then reuses:

```bash
gh auth login          # choose GitHub.com, then HTTPS, then "Login with a web browser"
```

Answer **yes** when it asks whether to authenticate git with your GitHub credentials. On
Windows, Git for Windows ships a credential manager that pops up a browser login the first
time you push, and that works too. SSH keys also work if you already use them; you do not
need them for this course.

## 3. Get your own copy

The course repository is read-only for you. You work in your **own private copy** of it, under
your GitHub account. It holds all six labs, it is what you push to, and it is what you hand in
([lab submission guide](lab-submission.md)).

**Do not press Fork.** A fork of a public repository is always public, so anyone, including
your classmates, could read your lab work while the lab is still open. Make a private copy
instead. It takes five steps.

1. Clone the course repository:

   ```bash
   git clone https://github.com/pasdptt/public_teaching_cloudengineering.git cloudengineering
   cd cloudengineering
   ```

2. Rename that remote to `upstream`. It stays connected to the course, so you can pick up
   corrections later (section 7):

   ```bash
   git remote rename origin upstream
   ```

3. **Create an empty private repository on GitHub.** Press **+** (top right), then
   **New repository**:
   - name it `cloudengineering`;
   - choose **Private**;
   - leave *Add a README*, *.gitignore* and *license* all **off**. The repository must start
     empty, or the next step is refused.

4. Connect your clone to it and push:

   ```bash
   git remote add origin https://github.com/YOUR-USERNAME/cloudengineering.git
   git push -u origin main
   git remote -v          # origin = your private copy, upstream = the course
   ```

   With the GitHub CLI, steps 3 and 4 are one command, run inside the folder:
   `gh repo create cloudengineering --private --source=. --remote=origin --push`

5. **Give the instructor access.** In your repository, open **Settings → Collaborators →
   Add people** and add `pasdptt`, unless the Teams class team names a different account.
   Without this, the marker cannot open what you hand in.

Actions are already on in a repository you created yourself. Open the **Actions** tab after
the push in step 4, and a CI run should be there.

> **A private repository is still not a safe.** The instructor can read it, and so can anyone
> you add later, or everyone, if you ever make it public. Section 6 applies just the same.

## 4. The everyday loop

Almost all of the course is these five commands, in this order:

```bash
git status                     # 1. what has changed? (run this constantly — it is free)
git diff                       # 2. read the actual changes, line by line
git add path/to/file.py        # 3. choose what goes into the next snapshot
git commit -m "Store jobs in a file so they survive a restart"   # 4. take the snapshot
git push                       # 5. upload it to GitHub (and start the tests)
```

- **Add files by name.** `git add .` adds everything in the folder, including things you did
  not mean to share. Name the files.
- **Commit small and often.** One commit per working step is easier to understand, to review
  and to undo than one commit at the end of the week.
- **Write the message for a reader.** Say what the change does and, if it is not obvious,
  why: *"Release the idempotency key when a job is deleted"*, not *"fix"* or *"update"*.
- **`git log --oneline`** shows your history, newest first. Press `q` to leave it.

## 5. Review your own change before you push

Nobody reviews your code before you submit it, so you are the reviewer. This takes two
minutes and catches most of what would otherwise cost you marks.

```bash
git status          # anything listed that you did not expect? config.env? a data/ folder?
git diff --staged   # exactly what the commit will contain, after `git add`
```

Read the diff as if someone else wrote it and ask:

1. **Is every change on purpose?** Delete leftover debug prints and commented-out code.
2. **Is there anything secret in it?** A project id is fine; a key, a token or a password
   never is (section 6).
3. **Do the tests still pass locally?** `cd application && python3 -m pytest` — pushing a
   red build to find out is slower than running it here.
4. **Would the message make sense to you in five weeks?** That is when you will be reading it,
   at the midterm or in Lab 6.

After pushing, open the **Actions** tab. A **green tick** means every test passed on both
Python versions; a **red cross** means something failed — click into the run, open the failed
step, and read the bottom of its log first. Lab 1 Part 6 asks you to make one go red on
purpose, so you will have seen both before it matters.

## 6. What must never be committed

The repository's `.gitignore` keeps most of these out automatically, as long as you leave it
alone and add files by name. **It cannot catch a key file**: Google names a downloaded key
after your project (`my-project-1a2b3c4d5e6f.json`), and no rule can tell that apart from an
ordinary file. So the rule for keys is simpler: never create one.

| Never commit | Why |
|---|---|
| Service-account key files, tokens, passwords | They are credentials. Nothing in this course needs a key file at all |
| `config.env` in a lab's `starter/` folder | Holds your project id and settings; it is yours, not the course's |
| `.venv/` | Your local Python environment — large, and specific to your laptop |
| `*.tfstate`, `.terraform/` | Terraform state can contain secrets (week 13) |
| Lab run output folders, `application/data/` | Results are submitted, not committed |

**If you commit a secret anyway, deleting the file is not enough.** It stays in your history,
and anyone who can read the repository can read it. In this order: **revoke or rotate it first** (in the Google Cloud
console, delete the key), then tell the instructor, then clean up. A revoked key in your
history is harmless; a live one in a deleted file is not.

## 7. Picking up corrections to the course

The instructor will fix and add things during the term. Your copy does not update itself.

Pull them from the `upstream` remote you set up in section 3:

```bash
git fetch upstream
git merge upstream/main
git push
```

Do this at the start of each lab, with your own work committed first (`git status` should
say *nothing to commit*). If git reports a **conflict**, it means the course changed a line
that you also changed. Open the file it names, find the block between `<<<<<<<` and
`>>>>>>>`, keep the version you want, delete the marker lines, then `git add` the file and
`git commit`. If it is a file you never meant to edit, keep the course's version.

## 8. Undoing things safely

| You want to… | Do this | Safe? |
|---|---|---|
| Take a file back out of the next commit (after `git add`) | `git restore --staged FILE` | Yes — your edits are kept |
| Throw away your edits to a file since the last commit | `git restore FILE` | **No** — the edits are gone for good |
| Fix the message or add a forgotten file to the last commit, **not yet pushed** | `git add FILE` then `git commit --amend` | Yes, before pushing |
| Undo a commit you **already pushed** | `git revert COMMIT-ID` then `git push` | Yes — it adds a new commit that reverses the old one |
| See an old version of a file without changing anything | `git show COMMIT-ID:path/to/file` | Yes |

Two commands to **avoid** unless you know exactly why you need them: `git reset --hard`
(silently deletes uncommitted work) and `git push --force` (overwrites what is on GitHub).
If you think you need either, ask in the class issue log first. Almost everything a beginner
breaks in git is recoverable *until* one of those two is used to "fix" it.

## 9. Traps specific to this course

- **Actions minutes come from a free allowance.** In a private repository, GitHub Free
  includes enough usage each month for about 2,000 minutes of Linux runs. One CI run is two
  short jobs, and GitHub rounds each one up to a minute, so it costs 2 minutes. If the
  allowance ever runs out, runs are blocked, not billed, as long as you have not added a
  payment method. Pushing a few times a day uses a small fraction of it.
- **The tests only run on `main`, or on a pull request into `main`.** That is what
  `.github/workflows/ci.yml` says. A push to some other branch with no pull request runs
  nothing — by design, not a fault.
- **Never push to `upstream`.** It is the course repository, and you cannot write to it.
  If `git push` says *permission denied* and names `pasdptt/public_teaching_cloudengineering`,
  your `origin` still points at the course. Redo section 3, steps 2 and 4.
- **Run git commands from inside the repository folder.** `fatal: not a git repository`
  means you are somewhere else — `cd` back to the folder you cloned.
- **Lab 6 depends on your repository's name.** The keyless login it sets up trusts one
  repository by name. Do not rename your repository after Lab 6 Part 4, or the pipeline stops
  being able to deploy.

## 10. When git says no

| Message | What it means | What to do |
|---|---|---|
| `Authentication failed` / `Permission denied` | git cannot log in, or `origin` is still the course repository | Redo section 2's login. Check that `git remote -v` shows *your* username for `origin` |
| `remote: Repository not found` | The `origin` address is mistyped, or the repository is private and git is logged in as someone else | Check `git remote -v`, then section 2's login |
| `rejected … (fetch first)` | GitHub has commits you do not have, usually from an edit on the website | `git pull`, then `git push` again |
| `Your branch is ahead of 'origin/main' by N commits` | You committed but have not pushed | `git push` |
| `CONFLICT (content): Merge conflict in …` | You and the course changed the same lines | Section 7 |
| `You are in 'detached HEAD' state` | You checked out an old commit, not a branch | `git switch main` to get back |
| `nothing added to commit but untracked files present` | You committed before `git add` | `git add` the files, then commit |

Still stuck after ten minutes? Post the exact command and the full message in the class issue
log. Copy the text, not a screenshot, and leave out any key or token.

## 11. Check yourself

You are ready for Lab 1 Part 6 if you can, without looking:

- [ ] say what `origin` and `upstream` point to in your clone;
- [ ] make a one-line change, see it with `git diff`, commit it with a useful message, and
      push it;
- [ ] find that push's run in your repository's **Actions** tab and say whether it is green;
- [ ] name three things that must never be committed, and what to do first if one is;
- [ ] undo a commit you have already pushed, without `--force`;
- [ ] say where a lab write-up goes and which link you hand in on Teams
      ([lab submission guide](lab-submission.md)).

## Words you will meet

| Word | Meaning here |
|---|---|
| Repository (repo) | A folder git tracks, with its whole history |
| Commit | One saved snapshot, with a message and an id like `8e165e3` |
| Branch | A named line of commits. This course mostly needs only `main` |
| Remote | Another copy of the repo that you push to or pull from: `origin`, `upstream` |
| Fork | A GitHub copy of someone else's repository, public if theirs is. This course uses a private copy instead (section 3) |
| Clone | Your laptop's copy of a GitHub repository |
| Push / pull | Upload your commits / download and merge commits from GitHub |
| Pull request (PR) | A proposal to merge one branch into another, with a place to review it |
| Workflow / run | GitHub Actions' recipe (`.github/workflows/ci.yml`) and one execution of it |
