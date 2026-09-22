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

say "This will delete, from project ${PROJECT_ID}:"
note "  Push subscription       ${SUBSCRIPTION_NAME}  <-- delete this FIRST"
note "  Topics                  ${TOPIC_NAME}, ${DEAD_LETTER_TOPIC}"
note "  Cloud Run service       ${SERVICE_NAME} (${REGION})"
note "  Artifact Registry repo  ${REPO_NAME} and every image in it"
note "  Bucket                  gs://${BUCKET_NAME} and its contents"
note "  Service accounts        ${SA_EMAIL}"
note "                          ${PUSH_SA_EMAIL}"
read -r -p "    Type the project id to confirm: " confirm
[[ "$confirm" == "$PROJECT_ID" ]] || { echo "Not confirmed. Nothing deleted." >&2; exit 1; }

# Subscription first, deliberately. Deleting the service while the subscription is live
# means every retained message is redelivered to an endpoint returning 404 until it gives
# up -- harmless, noisy, and a good illustration of why teardown has an order.
say "Deleting the subscription"
gcloud pubsub subscriptions delete "$SUBSCRIPTION_NAME" \
  --project="$PROJECT_ID" --quiet || note "(already gone)"

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

say "Deleting the service accounts"
for sa in "$SA_EMAIL" "$PUSH_SA_EMAIL"; do
  gcloud iam service-accounts delete "$sa" --project="$PROJECT_ID" --quiet \
    || note "($sa already gone)"
done

say "Done. Now run ./07-verify-clean.sh."
