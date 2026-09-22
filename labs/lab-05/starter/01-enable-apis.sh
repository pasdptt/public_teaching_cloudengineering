#!/usr/bin/env bash
# Turn on the services this lab adds to Lab 4's set.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud

say "Enabling APIs on ${PROJECT_ID}"
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  pubsub.googleapis.com \
  --project="$PROJECT_ID"

say "Done."
note "Only pubsub.googleapis.com is new; the rest were already on from Lab 4 and"
note "enabling something twice is harmless."
