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
note "  Cloud Build staging     gs://${PROJECT_ID}_cloudbuild (made by gcloud builds submit)"
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

say "Deleting the Cloud Build staging bucket"
# gcloud builds submit created gs://${PROJECT_ID}_cloudbuild to upload your source, without
# asking. It is not a lab resource you chose, which is exactly why it is easy to leave behind
# -- and it is multi-region, so Always Free does not cover it. The next build recreates it.
gcloud storage rm -r "gs://${PROJECT_ID}_cloudbuild" --project="$PROJECT_ID" 2>/dev/null \
  || note "(already gone)"

say "Deleting the service account"
gcloud iam service-accounts delete "$SA_EMAIL" \
  --project="$PROJECT_ID" --quiet || note "(already gone)"

say "Done. Now run ./07-verify-clean.sh -- claiming cleanup is not the same as verifying it."
