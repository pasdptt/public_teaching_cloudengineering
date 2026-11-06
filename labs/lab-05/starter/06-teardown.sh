#!/usr/bin/env bash
# Remove everything Labs 4 and 5 created.
#
# Six resources now. The subscription is the one that matters most: it is the only thing in
# this course that costs money by SITTING there holding data nobody asked for.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud

BUCKET_NAME="${BUCKET_NAME:-${PROJECT_ID}-docapp-lab5}"
SA_EMAIL="${RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
PUSH_SA_EMAIL="${PUSH_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
# Default for a config.env made before this variable existed.
DEAD_LETTER_SUBSCRIPTION="${DEAD_LETTER_SUBSCRIPTION:-docapp-jobs-dead-sub}"

say "This will delete, from project ${PROJECT_ID}:"
note "  Push subscription       ${SUBSCRIPTION_NAME}  <-- delete this FIRST"
note "  Dead-letter subscription ${DEAD_LETTER_SUBSCRIPTION}"
note "  Topics                  ${TOPIC_NAME}, ${DEAD_LETTER_TOPIC}"
note "  Cloud Run service       ${SERVICE_NAME} (${REGION})"
note "  Artifact Registry repo  ${REPO_NAME} and every image in it"
note "  Bucket                  gs://${BUCKET_NAME} and its contents"
note "  Cloud Build staging     gs://${PROJECT_ID}_cloudbuild (made by gcloud builds submit)"
note "  Service accounts        ${SA_EMAIL}"
note "                          ${PUSH_SA_EMAIL}"
read -r -p "    Type the project id to confirm: " confirm
[[ "$confirm" == "$PROJECT_ID" ]] || { echo "Not confirmed. Nothing deleted." >&2; exit 1; }

# Subscription first, deliberately. Deleting the service while the subscription is live
# means every retained message is redelivered to an endpoint returning 404 until it gives
# up -- harmless, noisy, and a good illustration of why teardown has an order.
say "Deleting the subscriptions"
for s in "$SUBSCRIPTION_NAME" "$DEAD_LETTER_SUBSCRIPTION"; do
  gcloud pubsub subscriptions delete "$s" --project="$PROJECT_ID" --quiet || note "($s already gone)"
done

say "Deleting the topics"
for t in "$TOPIC_NAME" "$DEAD_LETTER_TOPIC"; do
  gcloud pubsub topics delete "$t" --project="$PROJECT_ID" --quiet || note "($t already gone)"
done

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

say "Deleting the service accounts"
for sa in "$SA_EMAIL" "$PUSH_SA_EMAIL"; do
  gcloud iam service-accounts delete "$sa" --project="$PROJECT_ID" --quiet \
    || note "($sa already gone)"
done

say "Done. Now run ./07-verify-clean.sh."
