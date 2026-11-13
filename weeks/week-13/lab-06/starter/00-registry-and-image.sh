#!/usr/bin/env bash
# Lab 6 Part 2 -- a registry, and one image to deploy.
#
# Labs 4 and 5 deleted their Artifact Registry repository at teardown, as they should have.
# So at the start of Lab 6 there is nothing to deploy. This script creates the repository that
# Lab 6, its pipeline and your project all use, and builds ONE image from your current tree.
#
# The image is built from application/ AS IT IS NOW. infra/ runs the service on Cloud Storage,
# Firestore and Pub/Sub, so your Lab 3 and Lab 5 implementations must be in the tree: an image
# built from the stubs fails its first request, from Iowa. The check below refuses to build
# while any of the three stubs is still in place.
#
# What it prints is the image by DIGEST, not by tag. Use that one value for dev in Part 2 and
# for prod in Part 3 -- the same bytes, named in a way that cannot move.
#
# The repository is not in Terraform state. It is shared by both environments and by the
# pipeline, and it is removed by hand at the very end (operations/cleanup.md).
#
# STATUS: NOT YET RUN AGAINST A REAL PROJECT (README.md "Status"). If a command fails, the
# error message and the current documentation decide -- not this script.
set -euo pipefail
cd "$(dirname "$0")"
[[ -f config.env ]] || { echo "ERROR: copy config.env.example to config.env and fill it in" >&2; exit 1; }
# shellcheck disable=SC1091
source config.env
[[ "$PROJECT_ID" != "your-project-id-here" ]] || { echo "ERROR: set PROJECT_ID in config.env" >&2; exit 1; }

say() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
REPOSITORY="${REPOSITORY:-docapp}"
APP_SRC="$(cd ../../../../application && pwd)"

say "Checking your Lab 3 and Lab 5 code is in the tree"
stubs="$(grep -l 'is your Lab [35] exercise and is not implemented yet' \
  "$APP_SRC/docapp/gcs_storage.py" "$APP_SRC/docapp/firestore_jobstore.py" \
  "$APP_SRC/docapp/pubsub_queue.py" 2>/dev/null || true)"
if [[ -n "$stubs" ]]; then
  echo "ERROR: these files are still the unimplemented stubs:" >&2
  printf '         %s\n' $stubs >&2
  echo "       Copy your Lab 3 and Lab 5 implementations into application/ first." >&2
  exit 1
fi

say "Enabling the APIs this lab uses (free; most are already on from Labs 3-5)"
gcloud services enable artifactregistry.googleapis.com cloudbuild.googleapis.com \
  run.googleapis.com pubsub.googleapis.com firestore.googleapis.com storage.googleapis.com \
  iam.googleapis.com --project="$PROJECT_ID"

say "The Artifact Registry repository '${REPOSITORY}' in ${REGION}"
if gcloud artifacts repositories describe "$REPOSITORY" \
     --location="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
  echo "    already exists -- reusing it"
else
  gcloud artifacts repositories create "$REPOSITORY" \
    --repository-format=docker --location="$REGION" --project="$PROJECT_ID" \
    --description="docapp images: Lab 6 and the project"
fi

# Tagged with the commit it came from, prefixed so it can never be confused with a pipeline
# build (which tags with the full sha).
TAG="manual-$(git -C "$APP_SRC" rev-parse --short=12 HEAD)"
TAGGED="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/docapp:${TAG}"

say "Building ${TAGGED}"
# Cloud Build stages your source in gs://${PROJECT_ID}_cloudbuild. That bucket is created for
# you, is not in Terraform state, and is on the teardown list in Part 6.
gcloud builds submit "$APP_SRC" --tag="$TAGGED" --project="$PROJECT_ID"

DIGEST="$(gcloud artifacts docker images describe "$TAGGED" \
  --project="$PROJECT_ID" --format='value(image_summary.digest)')"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/docapp@${DIGEST}"

say "Done. Use this exact value for dev AND for prod:"
echo
echo "    export IMAGE='${IMAGE}'"
echo
echo "    The tag ${TAG} may be moved or deleted. The digest names these bytes and nothing else."
