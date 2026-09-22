#!/usr/bin/env bash
# Deploy the image to managed execution.
#
# One command, and about eight decisions hidden inside it. The guard rails below refuse two
# of those decisions outright; the rest are yours, and the rubric asks you to defend them.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud
require_free_tier_region
require_zero_min_instances
require_bounded_max_instances

BUCKET_NAME="${BUCKET_NAME:-${PROJECT_ID}-docapp-lab4}"
SA_EMAIL="${RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}"

say "Deploying ${SERVICE_NAME} to ${REGION}"
note "image        ${IMAGE}"
note "identity     ${SA_EMAIL}"
note "concurrency  ${CONCURRENCY}   min ${MIN_INSTANCES}   max ${MAX_INSTANCES}"

# --no-allow-unauthenticated: the service refuses callers with no identity.
#
# It would be one flag to make this public, and every tutorial you find will do exactly
# that. Part 2 asks you to leave it closed and carry a token instead, because "who may call
# this" is a question you should have to answer on purpose rather than by default.
#
# The environment below is deliberately HALF right, and the half that is wrong is the
# subject of Part 3.
#
# Documents go to the bucket, so they are shared by every instance. Job records stay in a
# dictionary inside each instance, which is how the application has shipped since week 2.
# Run it this way first: two kinds of state, identical code paths, and only one of them
# survives contact with a second instance. Do not skip ahead -- the broken run is the
# evidence, and it is much more convincing than being told.
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
  --set-env-vars="DOCAPP_STORAGE=gcs,DOCAPP_BUCKET=${BUCKET_NAME},DOCAPP_JOBSTORE=memory,DOCAPP_PROJECT_ID=${PROJECT_ID},DOCAPP_PROCESSING_DELAY_MS=${PROCESSING_DELAY_MS},DOCAPP_LOG_LEVEL=info"

say "Deployed. The service URL:"
gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" --project="$PROJECT_ID" \
  --format="value(status.url)"

note "Calling it without a token will return 403. That is the deployment working, not"
note "failing. To call it as yourself:"
note '  curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$SERVICE_URL/healthz"'
