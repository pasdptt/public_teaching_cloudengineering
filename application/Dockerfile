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

# requirements.txt is empty today. Copying and installing it anyway means Labs 3 and 5 add
# a dependency without restructuring this file — and the layer cache keeps rebuilds fast.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY docapp/ ./docapp/
COPY samples/ ./samples/
COPY tools/ ./tools/

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

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request,os,sys; \
      sys.exit(0 if urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\",\"8080\")}/healthz', timeout=2).status==200 else 1)"

CMD ["python3", "-m", "docapp"]
