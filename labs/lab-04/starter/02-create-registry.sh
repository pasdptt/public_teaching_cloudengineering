#!/usr/bin/env bash
# Create the image repository and the bucket this lab's service will use for documents.
#
# Two resources, both of which cost nothing at this size and both of which you will have
# to remember in the teardown. Notice that the registry is storage like any other: 0.5 GiB
# free, and every build you push consumes some of it.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud
require_free_tier_region

BUCKET_NAME="${BUCKET_NAME:-${PROJECT_ID}-docapp-lab4}"

say "Creating Artifact Registry repository '${REPO_NAME}' in ${REGION}"
if gcloud artifacts repositories describe "$REPO_NAME" \
     --location="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
  note "Already exists. Reusing it."
else
  gcloud artifacts repositories create "$REPO_NAME" \
    --repository-format=docker \
    --location="$REGION" \
    --description="Course application images" \
    --project="$PROJECT_ID"
fi

say "Creating bucket gs://${BUCKET_NAME}"
if gcloud storage buckets describe "gs://${BUCKET_NAME}" --project="$PROJECT_ID" >/dev/null 2>&1; then
  note "Already exists. Reusing it."
else
  # The same two flags as Lab 3, for the same two reasons. If you cannot still say what
  # each one prevents, re-read your own Lab 3 submission before continuing.
  # tr, not ${REGION^^}: macOS still ships bash 3.2 as /bin/bash, and uppercase parameter
  # expansion is a bash 4 feature. A script that only runs on the author's machine is not
  # a script, it is a note.
  gcloud storage buckets create "gs://${BUCKET_NAME}" \
    --project="$PROJECT_ID" \
    --location="$(printf '%s' "$REGION" | tr '[:lower:]' '[:upper:]')" \
    --uniform-bucket-level-access \
    --public-access-prevention
fi

say "Both exist."
note "BUCKET_NAME=${BUCKET_NAME}"
note "Add that line to config.env so the later scripts agree with this one."
