#!/usr/bin/env bash
# Build v2 of the image -- the one with your Pub/Sub backend in it -- and push it.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud
require_free_tier_region

APP_SRC="$(cd "$(dirname "$0")/../../../application" && pwd)"
[[ -d "$APP_SRC" ]] || { echo "ERROR: cannot find application/ at $APP_SRC" >&2; exit 1; }

IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}"

say "Creating the registry repository if Lab 4's teardown removed it"
if ! gcloud artifacts repositories describe "$REPO_NAME" \
      --location="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud artifacts repositories create "$REPO_NAME" \
    --repository-format=docker --location="$REGION" \
    --description="Course application images" --project="$PROJECT_ID"
  note "Recreated. It should have been gone -- Lab 4's teardown deletes it."
fi

say "Building ${IMAGE}"
gcloud builds submit "$APP_SRC" --tag="$IMAGE" --project="$PROJECT_ID"

say "Pushed. The digest of what was actually built:"
gcloud artifacts docker images describe "$IMAGE" \
  --project="$PROJECT_ID" --format="value(image_summary.digest)"
