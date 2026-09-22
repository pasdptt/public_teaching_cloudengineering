#!/usr/bin/env bash
# Remove everything this lab created.
#
# Four resources, and only one of them is obvious. The image in Artifact Registry is the
# one students forget, because it is the only one that is not a running thing -- and it is
# also the only one with a storage allowance small enough to matter.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud

BUCKET_NAME="${BUCKET_NAME:-${PROJECT_ID}-docapp-lab4}"
SA_EMAIL="${RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

say "This will delete, from project ${PROJECT_ID}:"
note "  Cloud Run service       ${SERVICE_NAME} (${REGION})"
note "  Artifact Registry repo  ${REPO_NAME} and every image in it"
note "  Bucket                  gs://${BUCKET_NAME} and its contents"
note "  Service account         ${SA_EMAIL}"
note ""
note "The Firestore (default) database is NOT deleted. Empty its collection instead, and"
note "say in your submission why keeping an empty one costs nothing."
read -r -p "    Type the project id to confirm: " confirm
[[ "$confirm" == "$PROJECT_ID" ]] || { echo "Not confirmed. Nothing deleted." >&2; exit 1; }

say "Deleting the Cloud Run service"
gcloud run services delete "$SERVICE_NAME" \
  --region="$REGION" --project="$PROJECT_ID" --quiet || note "(already gone)"

say "Deleting the Artifact Registry repository"
gcloud artifacts repositories delete "$REPO_NAME" \
  --location="$REGION" --project="$PROJECT_ID" --quiet || note "(already gone)"

say "Deleting the bucket and its contents"
gcloud storage rm -r "gs://${BUCKET_NAME}" --project="$PROJECT_ID" || note "(already gone)"

say "Deleting the service account"
gcloud iam service-accounts delete "$SA_EMAIL" \
  --project="$PROJECT_ID" --quiet || note "(already gone)"

say "Done. Now run ./07-verify-clean.sh -- claiming cleanup is not the same as verifying it."
