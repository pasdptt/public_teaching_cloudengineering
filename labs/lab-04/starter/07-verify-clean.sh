#!/usr/bin/env bash
# Prove the project is clean. Save this output; band C of the rubric wants it.
#
# Note what this script does NOT do: it does not trust the teardown script. Every check
# here asks the provider what exists, which is the only answer worth having.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud

BUCKET_NAME="${BUCKET_NAME:-${PROJECT_ID}-docapp-lab4}"
SA_EMAIL="${RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
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

check "Cloud Run services (${REGION})" \
  gcloud run services list --region="$REGION" --project="$PROJECT_ID" --format="value(metadata.name)"

check "Artifact Registry repositories (${REGION})" \
  gcloud artifacts repositories list --location="$REGION" --project="$PROJECT_ID" --format="value(name)"

check "Buckets" \
  gcloud storage ls --project="$PROJECT_ID"

check "Lab service account" \
  gcloud iam service-accounts list --project="$PROJECT_ID" \
    --filter="email:${SA_EMAIL}" --format="value(email)"

say "Still present on purpose, and not a failure:"
gcloud firestore databases list --project="$PROJECT_ID" \
  --format="value(name)" 2>/dev/null || note "(no Firestore database)"
note "An empty (default) Firestore database costs nothing. Your submission must say so"
note "with evidence rather than as an assertion."

if (( problems > 0 )); then
  say "${problems} thing(s) left behind. Not clean."
  exit 1
fi
say "Nothing left behind."
