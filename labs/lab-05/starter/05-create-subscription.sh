#!/usr/bin/env bash
# Point the broker at the service. This is the step that makes work actually happen.
#
# A push subscription needs an identity of its own: Pub/Sub calls your service, your service
# refuses anonymous callers, so Pub/Sub must be able to prove who it is. That identity is
# NOT the one the service runs as, and Part 3 asks you to say why keeping them separate
# matters.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud
require_short_retention

PUSH_SA_EMAIL="${PUSH_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

SERVICE_URL="$(gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" --project="$PROJECT_ID" --format='value(status.url)')"
[[ -n "$SERVICE_URL" ]] || { echo "ERROR: ${SERVICE_NAME} is not deployed. Run 04 first." >&2; exit 1; }

say "Creating the push identity ${PUSH_SA_EMAIL}"
if ! gcloud iam service-accounts describe "$PUSH_SA_EMAIL" --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud iam service-accounts create "$PUSH_SA_NAME" \
    --display-name="Pub/Sub push caller (Lab 5)" --project="$PROJECT_ID"
fi

# ---------------------------------------------------------------------------------------
# TODO(lab05): this identity needs exactly one permission, on exactly one resource.
#
# It must be allowed to invoke ONE Cloud Run service. Not the project, not every service in
# it. Find the role, and grant it with `gcloud run services add-iam-policy-binding` rather
# than at the project level -- the difference is the whole exercise, and the rubric asks you
# to say what a project-level grant would additionally have permitted.
#
# There is a second grant you will probably need and will not expect: Pub/Sub's own service
# agent needs permission to mint tokens for this account. The error message names it when
# you hit it. Read the error rather than searching -- being able to act on one of these is
# worth more than remembering it.
# ---------------------------------------------------------------------------------------

say "Creating the push subscription"
note "endpoint     ${SERVICE_URL}/tasks/process"
note "retention    ${MESSAGE_RETENTION_SECONDS}s"
note "ack deadline ${ACK_DEADLINE_SECONDS}s"
note "dead letter  ${DEAD_LETTER_TOPIC} after ${MAX_DELIVERY_ATTEMPTS} attempts"

if gcloud pubsub subscriptions describe "$SUBSCRIPTION_NAME" --project="$PROJECT_ID" >/dev/null 2>&1; then
  note "Subscription already exists -- updating it instead of creating it."
  gcloud pubsub subscriptions update "$SUBSCRIPTION_NAME" \
    --project="$PROJECT_ID" \
    --push-endpoint="${SERVICE_URL}/tasks/process" \
    --push-auth-service-account="$PUSH_SA_EMAIL" \
    --ack-deadline="$ACK_DEADLINE_SECONDS" \
    --message-retention-duration="${MESSAGE_RETENTION_SECONDS}s"
else
  gcloud pubsub subscriptions create "$SUBSCRIPTION_NAME" \
    --project="$PROJECT_ID" \
    --topic="$TOPIC_NAME" \
    --push-endpoint="${SERVICE_URL}/tasks/process" \
    --push-auth-service-account="$PUSH_SA_EMAIL" \
    --ack-deadline="$ACK_DEADLINE_SECONDS" \
    --message-retention-duration="${MESSAGE_RETENTION_SECONDS}s" \
    --dead-letter-topic="$DEAD_LETTER_TOPIC" \
    --max-delivery-attempts="$MAX_DELIVERY_ATTEMPTS"
fi

say "Subscribed."
note "Any job you submitted before this moment is gone -- a topic with no subscription"
note "discards what it receives. Jobs submitted from now on will be delivered."
