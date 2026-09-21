# Student setup

What you need on your own machine, and how to get it there. Separate verified paths for
Windows and macOS.

**Do this before week 1.** The week 1 session includes an environment check, and its purpose
is to find problems while there is still time to fix them. A setup problem discovered in
week 4 costs you a lab.

> **Validation status.** The environment-check script and the application have been
> **executed** on Linux with Python 3.10. The Windows and macOS instructions below have been
> **reviewed but not executed** on those platforms — no Windows or macOS machine was
> available during authoring. Report anything that does not match what you see; that
> feedback is how this file becomes trustworthy.

---

## What you need

| | Why |
|---|---|
| **Python 3.10 or newer** | The course application. No packages needed to run it. |
| **A container runtime** | From Lab 1 onwards, to see the process boundary; in Lab 4 to build an image. |
| **`git`** | To get this repository and keep it up to date. |
| **A terminal you are comfortable in** | Every lab is command-line work. |
| **~10 GB free disk** | Container images in Lab 4. |

You do **not** need: a cloud account (not until week 4), a paid IDE, a database, or any
Python package beyond `pytest` for the Lab 1 tests.

---

## macOS

### Python

macOS ships with a Python that is best left alone. Install your own:

```bash
# with Homebrew, if you have it
brew install python@3.12

# or download the installer from python.org
```

Check it:

```bash
python3 --version     # expect 3.10 or newer
```

### Container runtime

Either works. Pick one.

- **Docker Desktop** — <https://www.docker.com/products/docker-desktop/>. The most widely
  documented, which matters when you are searching for an error message. Note that Docker
  Desktop's licence terms depend on the size of the organisation you use it for; for
  coursework as an individual student it is free. Check the current terms yourself — they
  have changed before.
- **Podman Desktop** — <https://podman-desktop.io/>. Free and open source, no licence
  question. Commands are the same: `podman build`, `podman run`. Everywhere the labs say
  `docker`, `podman` works.

**Apple Silicon (M1/M2/M3/M4):** your machine is `arm64`. Most images have an `arm64`
variant and this is invisible most of the time. It stops being invisible in **Lab 4**, where
the image you build locally is deployed to a cloud service running `amd64`. Lab 4 tells you
exactly what to do; just know now that the architecture question exists.

Check which you have:

```bash
uname -m      # arm64 = Apple Silicon, x86_64 = Intel
```

### Verify

```bash
git clone <this repository> && cd cloudengineering
python3 operations/check_environment.py
```

---

## Windows

You have two routes. **We recommend WSL2**, and the reason is concrete rather than
ideological: every lab command in this course is written for a Unix-style shell, and with
WSL2 you run exactly the commands in the lab instead of translating them. Translation errors
are a real and avoidable way to lose an evening.

### Route A — WSL2 (recommended)

In PowerShell, as Administrator:

```powershell
wsl --install
```

Restart when asked. You get Ubuntu. Open it and work **inside** it from then on:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
python3 --version     # expect 3.10 or newer
```

Then install **Docker Desktop for Windows** and enable its WSL2 integration
(Settings → Resources → WSL Integration → enable for your distribution). Your `docker`
commands then work from inside Ubuntu.

**Keep the repository inside the Linux filesystem**, not on `/mnt/c/`. Working across the
Windows/Linux filesystem boundary is noticeably slow and causes file-permission oddities:

```bash
cd ~                      # your Linux home, e.g. /home/you
git clone <this repository>
```

### Route B — native Windows

Workable, with more friction.

- Python from <https://www.python.org/downloads/> — **tick "Add python.exe to PATH"** during
  installation. Forgetting this is the most common Windows problem in week 1.
- Docker Desktop for Windows.
- Git for Windows, which brings Git Bash — use that rather than `cmd.exe`.

**The `curl` trap.** PowerShell aliases `curl` to `Invoke-WebRequest`, which takes completely
different arguments. Every `curl` command in the labs will fail in confusing ways. Either:

```powershell
curl.exe -sS http://127.0.0.1:8080/healthz    # note the .exe
```

or use Git Bash, or use WSL2 and stop thinking about it.

**Line endings.** Git on Windows may convert line endings on checkout, which breaks shell
scripts. This repository ships a `.gitattributes` that prevents it. If you see
`bad interpreter: /bin/bash^M`, that is what happened — re-clone with the `.gitattributes`
in place.

### Verify

```bash
python3 operations/check_environment.py
```

(On native Windows: `python operations\check_environment.py`.)

---

## The environment check

```bash
python3 operations/check_environment.py
```

It installs nothing, changes nothing, and contacts no cloud service. It checks your Python
version, disk space and outbound network; starts the real application on a spare port and
drives a document and a job through it; runs the test suite; and looks for a container
runtime.

Every result is `PASS`, `WARN` or `FAIL`.

- **All PASS** — you are ready.
- **WARN** — nothing is blocking you. Read them before Lab 1. A missing container runtime is
  a WARN, because the application itself runs without one.
- **FAIL** — bring the output to the week 1 session. **Do not spend an evening on it alone.**
  Diagnosing host setup problems is not what this course assesses, and it is not a good use
  of your 180 minutes.

Example of a healthy run:

```text
  PASS  Python 3.12.3
  PASS  Free disk space: 87.4 GB
  PASS  Application starts and answers /healthz
  PASS  Can store a document
  PASS  Can create and complete a job
  PASS  The application test suite passes
  PASS  Container runtime available: docker
```

## Running the application by hand

```bash
cd application
python3 -m docapp
# then, in another terminal:
curl http://127.0.0.1:8080/healthz
```

`application/README.md` has the full API and the configuration variables.

## Installing pytest (needed from Lab 1)

```bash
pip3 install -r application/requirements-dev.txt
```

That is one package, `pytest`. If `pip3` complains about an externally-managed environment
(common on recent Linux and on Homebrew Python), use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r application/requirements-dev.txt
```

## If you get stuck

1. Read the error. This application tries hard to tell you what to fix — a configuration
   error names the variable and what it accepts.
2. Check the troubleshooting section of the lab you are on.
3. **Post it in the class issue log.** One person's solved problem is everyone's solved
   problem, and with one instructor and no teaching assistant that shared log is the only
   scaling mechanism this course has. Posting early is helpful to everyone, not an admission
   of anything.
4. Bring it to the next session.

## What is deliberately not here

No IDE is prescribed — use what you like. No virtual environment is required to *run* the
application, because it has no dependencies. No cloud SDK yet: `gcloud` is installed in
week 4, with the trial, and not before.
