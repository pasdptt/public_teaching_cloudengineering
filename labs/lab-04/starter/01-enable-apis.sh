#!/usr/bin/env bash
# Turn on the three services this lab uses.
#
# Enabling an API costs nothing and bills nothing. It grants your project the ability to
# call a service; charges start when you create something. Worth knowing, because the
# console's language around this makes students nervous, and nervousness in the wrong
# place means they are not nervous in the right one.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud

say "Enabling APIs on ${PROJECT_ID}"
note "run            -- managed execution"
note "artifactregistry -- where the image lives"
note "cloudbuild     -- what turns your Dockerfile into that image"

gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  --project="$PROJECT_ID"

say "Done."
note "This can take a minute to propagate. If the next script reports that an API is"
note "not enabled, wait thirty seconds and run it again rather than enabling it twice."
