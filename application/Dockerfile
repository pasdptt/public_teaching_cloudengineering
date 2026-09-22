# The course application as a container image.
#
# Used first in Lab 1 to make the process boundary visible, and again in Lab 4 where this
# same image is pushed to Artifact Registry and deployed to managed execution.
#
# It is deliberately small. Artifact Registry's free allowance is 0.5 GiB, every rebuild
# pushes new layers, and a small image is also a fast build and fewer build minutes. Having
# no dependencies to install is what makes that easy — see application/README.md.

# Pinned to a minor version, not to :latest. An image tag that changes under you is a
# reproducibility bug waiting for the worst possible moment.
FROM python:3.12-slim

# Do not run as root. The application needs no privileges, and a container that runs as
# root has one fewer barrier between a bug and the host.
RUN useradd --create-home --uid 10001 appuser
WORKDIR /app

# Dependencies in their own layer, before the source. The two Google client libraries that
# Lab 3 added are ~63 MB and change about once a year; the source changes every push. Built
# in this order, a rebuild after an edit reuses the cached dependency layer and pushes only
# the small source layer on top — which is what keeps Artifact Registry's 0.5 GiB free
# allowance comfortable across a term of rebuilds.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY docapp/ ./docapp/
COPY samples/ ./samples/
COPY tools/ ./tools/

# /app is owned by root, and the application is not. Without this line the local storage
# backend cannot create its data directory and the container exits at startup with a
# permission error — on a laptop, and equally on Cloud Run in Lab 4, where the failure is
# much harder to read. Creating the directory here and handing it to the unprivileged user
# is the whole fix; it does not weaken anything, because nothing else lives under /app/data.
RUN mkdir -p /app/data && chown appuser:appuser /app/data

USER appuser

# 0.0.0.0, not 127.0.0.1. Inside a container, 127.0.0.1 means "this container only", so a
# published port would reach nothing. Lab 1 Part 2 asks you to explain this, and Lab 2 asks
# what the same setting means on a machine with a public address.
ENV DOCAPP_HOST=0.0.0.0 \
    PORT=8080 \
    DOCAPP_DATA_DIR=/app/data \
    PYTHONUNBUFFERED=1

# Documentation, not configuration: EXPOSE publishes nothing by itself. The port actually
# comes from $PORT, which managed platforms set for you.
EXPOSE 8080

# No volume is declared, deliberately. Anything written to /app/data dies with the
# container, which is exactly the lesson Lab 1 Part 3 asks you to observe and Lab 3 fixes
# by moving state to a storage service.
#
# On managed execution in Lab 4 it is worse than disposable: the container filesystem there
# is held in memory and counted against the instance's memory limit. "Writing to disk" is
# then a phrase with no disk in it, and filling that directory does not run out of space —
# it gets the instance killed.

# HEALTHCHECK is honoured by a local container runtime and ignored by Cloud Run, which
# decides an instance is ready when it accepts a connection on $PORT. Kept because Lab 1
# runs this image locally, and because the difference is worth noticing: who performs the
# health check, and what they do about a failure, changes with the platform.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request,os,sys; \
      sys.exit(0 if urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\",\"8080\")}/healthz', timeout=2).status==200 else 1)"

CMD ["python3", "-m", "docapp"]
