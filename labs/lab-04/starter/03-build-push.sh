#!/usr/bin/env bash
# Build the container image from application/Dockerfile and push it to Artifact Registry.
#
# The build happens on Google's infrastructure, not your laptop. That is convenient, and it
# is also the first time in this course that something is built somewhere other than where
# it was written -- which is the whole subject of week 13.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud
require_free_tier_region

APP_SRC="$(cd "$(dirname "$0")/../../../application" && pwd)"
[[ -d "$APP_SRC" ]] || { echo "ERROR: cannot find application/ at $APP_SRC" >&2; exit 1; }

IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}"

say "Building ${IMAGE}"
note "Source: ${APP_SRC}"
note "Tag '${IMAGE_TAG}', not 'latest'. A tag that moves is a tag that cannot tell you"
note "what is deployed. Part 1 asks you what a digest gives you that a tag does not."

gcloud builds submit "$APP_SRC" \
  --tag="$IMAGE" \
  --project="$PROJECT_ID"

say "Pushed. Recording what was actually built:"
gcloud artifacts docker images describe "$IMAGE" \
  --project="$PROJECT_ID" \
  --format="value(image_summary.digest)"

note "Copy that digest into your submission. It, not the tag, identifies these bytes."
