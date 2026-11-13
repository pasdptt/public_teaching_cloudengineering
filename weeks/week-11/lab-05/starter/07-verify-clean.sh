#!/usr/bin/env bash
# Prove the project is clean. Save this output; band C of the rubric wants it.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud

BUCKET_NAME="${BUCKET_NAME:-${PROJECT_ID}-docapp-lab5}"
problems=0

check() {
  local label="$1"; shift
  local output
  if output="$("$@" 2>&1)" && [[ -n "${output// }" ]]; then
    printf '  LEFT BEHIND  %s\n' "$label"
    printf '%s\n' "$output" | sed 's/^/               /'
    problems=$((problems + 1))
  else
    printf '  clean        %s\n' "$label"
  fi
}

say "Verifying project ${PROJECT_ID}"

check "Pub/Sub subscriptions" \
  gcloud pubsub subscriptions list --project="$PROJECT_ID" --format="value(name)"

check "Pub/Sub topics" \
  gcloud pubsub topics list --project="$PROJECT_ID" --format="value(name)"

check "Cloud Run services (${REGION})" \
  gcloud run services list --region="$REGION" --project="$PROJECT_ID" --format="value(metadata.name)"

check "Artifact Registry repositories (${REGION})" \
  gcloud artifacts repositories list --location="$REGION" --project="$PROJECT_ID" --format="value(name)"

check "Buckets" \
  gcloud storage ls --project="$PROJECT_ID"

check "Lab service accounts" \
  gcloud iam service-accounts list --project="$PROJECT_ID" \
    --filter="email:(${RUNTIME_SA_NAME} OR ${PUSH_SA_NAME})" --format="value(email)"

if (( problems > 0 )); then
  say "${problems} thing(s) left behind. Not clean."
  exit 1
fi
say "Nothing left behind."
note "The subscription is the line to read twice. It is the only resource in this course"
note "that bills for doing nothing but holding on to data you stopped collecting."
