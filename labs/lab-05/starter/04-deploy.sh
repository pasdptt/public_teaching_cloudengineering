#!/usr/bin/env bash
# Deploy the service with the Pub/Sub queue behind it.
#
# Same service as Lab 4, three environment variables different. That is the claim the seam
# has been making since week 2, and this is the last lab that gets to test it.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud
require_free_tier_region
require_zero_min_instances
require_bounded_max_instances

BUCKET_NAME="${BUCKET_NAME:-${PROJECT_ID}-docapp-lab5}"
SA_EMAIL="${RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}"

say "Creating the runtime service account if Lab 4's teardown removed it"
if ! gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud iam service-accounts create "$RUNTIME_SA_NAME" \
    --display-name="docapp runtime (Lab 5)" --project="$PROJECT_ID"
fi

# ---------------------------------------------------------------------------------------
# TODO(lab05): the runtime identity needs one permission it did not need in Lab 4.
#
# In Lab 4 this service read and wrote a bucket, read and wrote Firestore, and wrote logs.
# It now does one more thing. Work out what, find the smallest role that covers it, grant
# it, and record the one sentence of justification.
#
# Re-grant the Lab 4 roles too -- your teardown removed the account, and the bindings went
# with it. Your Lab 4 submission has the list.
# ---------------------------------------------------------------------------------------

say "Deploying ${SERVICE_NAME}"
note "queue        pubsub -> ${TOPIC_NAME}"
note "concurrency  ${CONCURRENCY}   min ${MIN_INSTANCES}   max ${MAX_INSTANCES}"

gcloud run deploy "$SERVICE_NAME" \
  --image="$IMAGE" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --service-account="$SA_EMAIL" \
  --no-allow-unauthenticated \
  --min-instances="$MIN_INSTANCES" \
  --max-instances="$MAX_INSTANCES" \
  --concurrency="$CONCURRENCY" \
  --cpu=1 \
  --memory=512Mi \
  --timeout=60s \
  --set-env-vars="DOCAPP_STORAGE=gcs,DOCAPP_BUCKET=${BUCKET_NAME},DOCAPP_JOBSTORE=firestore,DOCAPP_PROJECT_ID=${PROJECT_ID},DOCAPP_QUEUE=pubsub,DOCAPP_QUEUE_TOPIC=${TOPIC_NAME},DOCAPP_PROCESSING_DELAY_MS=${PROCESSING_DELAY_MS},DOCAPP_LOG_LEVEL=info"

say "Deployed. The service URL:"
gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" --project="$PROJECT_ID" --format="value(status.url)"

note "Nothing is consuming yet. Submit a job now and watch it stay PENDING forever --"
note "that is Part 2, and it is the most useful broken state in this lab."
