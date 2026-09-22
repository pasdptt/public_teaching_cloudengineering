#!/usr/bin/env bash
# Create the topic, the dead-letter topic, and the bucket. NOT the subscription --
# that needs the service URL, so it comes after the deploy, in 05.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud
require_free_tier_region
require_short_retention

BUCKET_NAME="${BUCKET_NAME:-${PROJECT_ID}-docapp-lab5}"

create_topic() {
  local name="$1"
  if gcloud pubsub topics describe "$name" --project="$PROJECT_ID" >/dev/null 2>&1; then
    note "Topic ${name} already exists. Reusing it."
  else
    gcloud pubsub topics create "$name" --project="$PROJECT_ID"
  fi
}

say "Creating the work topic"
create_topic "$TOPIC_NAME"

say "Creating the dead-letter topic"
create_topic "$DEAD_LETTER_TOPIC"
note "A message that fails ${MAX_DELIVERY_ATTEMPTS} deliveries ends up here instead of"
note "being retried forever. Part 4 asks what you would do with the ones that arrive."

say "Creating bucket gs://${BUCKET_NAME}"
if gcloud storage buckets describe "gs://${BUCKET_NAME}" --project="$PROJECT_ID" >/dev/null 2>&1; then
  note "Already exists. Reusing it."
else
  gcloud storage buckets create "gs://${BUCKET_NAME}" \
    --project="$PROJECT_ID" \
    --location="$(printf '%s' "$REGION" | tr '[:lower:]' '[:upper:]')" \
    --uniform-bucket-level-access \
    --public-access-prevention
fi

say "Done."
note "BUCKET_NAME=${BUCKET_NAME}"
note "Add that line to config.env so the later scripts agree with this one."
note ""
note "Notice what does NOT exist yet: a subscription. A topic with no subscription"
note "discards everything published to it. Predict what that means for a message you"
note "publish in the next ten minutes, then check whether you were right in Part 2."
