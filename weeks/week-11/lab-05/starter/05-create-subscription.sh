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
# Default for a config.env made before this variable existed.
DEAD_LETTER_SUBSCRIPTION="${DEAD_LETTER_SUBSCRIPTION:-docapp-jobs-dead-sub}"

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
    --message-retention-duration="${MESSAGE_RETENTION_SECONDS}s" \
    --dead-letter-topic="$DEAD_LETTER_TOPIC" \
    --max-delivery-attempts="$MAX_DELIVERY_ATTEMPTS"
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

# ---------------------------------------------------------------------------------------
# Dead-lettering, made to actually work. SUPPLIED, not a TODO: Part 5 is about what a
# dead-letter destination is FOR, and it needs something to look at.
#
# Two things the subscription's --dead-letter-topic flag does not do on its own:
#
#   1. Pub/Sub moves a failed message as ITSELF -- its service agent, not you -- so that
#      agent must be allowed to publish to the dead-letter topic, and to acknowledge the
#      original on this subscription. Without both, the policy is configured and never fires.
#   2. The dead-letter topic is a topic, and a topic with no subscription discards what it
#      receives (Part 3 showed you that). So it gets a subscription of its own, or every
#      dead-lettered message is lost the moment it arrives.
# ---------------------------------------------------------------------------------------
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
PUBSUB_AGENT="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-pubsub.iam.gserviceaccount.com"

say "Letting Pub/Sub's service agent move failed messages"
gcloud pubsub topics add-iam-policy-binding "$DEAD_LETTER_TOPIC" --project="$PROJECT_ID" \
  --member="$PUBSUB_AGENT" --role="roles/pubsub.publisher" >/dev/null
note "publisher  on ${DEAD_LETTER_TOPIC}"
gcloud pubsub subscriptions add-iam-policy-binding "$SUBSCRIPTION_NAME" --project="$PROJECT_ID" \
  --member="$PUBSUB_AGENT" --role="roles/pubsub.subscriber" >/dev/null
note "subscriber on ${SUBSCRIPTION_NAME}"

say "Giving the dead-letter topic a subscription, so dead letters are kept"
if ! gcloud pubsub subscriptions describe "$DEAD_LETTER_SUBSCRIPTION" --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud pubsub subscriptions create "$DEAD_LETTER_SUBSCRIPTION" \
    --project="$PROJECT_ID" \
    --topic="$DEAD_LETTER_TOPIC" \
    --message-retention-duration="${MESSAGE_RETENTION_SECONDS}s"
fi
note "A PULL subscription: nothing consumes it automatically. A human reads it, which is the"
note "whole point -- and it retains what it holds, so 06-teardown.sh deletes it."

say "Subscribed."
note "Any job you submitted before this moment is gone -- a topic with no subscription"
note "discards what it receives. Jobs submitted from now on will be delivered."
