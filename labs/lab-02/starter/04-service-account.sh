#!/usr/bin/env bash
# Replace the instance's over-privileged default identity with one that can do almost nothing.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud

SA_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

say "Creating service account ${SERVICE_ACCOUNT_NAME}"
gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
  --project="$PROJECT_ID" \
  --display-name="docapp runtime (Lab 2)" \
  --description="Least-privilege identity for the course application" 2>/dev/null \
  || note "already exists, continuing"

# TODO(lab02): grant the roles this identity needs -- and no more.
#
# The application, at this point in the course, reads and writes nothing in Google Cloud.
# It needs to write logs, and that is all. The role for that is roles/logging.logWriter.
#
# Add the binding below. Then, in your submission, answer: why attach an identity with
# almost no permissions rather than no identity at all?
#
#   gcloud projects add-iam-policy-binding "$PROJECT_ID" \
#     --member="serviceAccount:${SA_EMAIL}" \
#     --role="roles/________________"
#
# NOTE what this script never does: create a service-account KEY. No JSON file is
# downloaded, and none should be. The instance gets its identity from the metadata
# service because the identity is ATTACHED to it. Lab 6 does the same thing for a
# pipeline, with Workload Identity Federation.

say "Attaching it to ${INSTANCE_NAME} (the instance must be stopped to change this)"
gcloud compute instances stop "$INSTANCE_NAME" --project="$PROJECT_ID" --zone="$ZONE" --quiet
gcloud compute instances set-service-account "$INSTANCE_NAME" \
  --project="$PROJECT_ID" --zone="$ZONE" \
  --service-account="$SA_EMAIL" \
  --scopes="https://www.googleapis.com/auth/cloud-platform"
gcloud compute instances start "$INSTANCE_NAME" --project="$PROJECT_ID" --zone="$ZONE" --quiet

note "The instance was stopped and started. Its EPHEMERAL external IP has changed."
note "Get the new one from: gcloud compute instances list"
note "Ask yourself why a static address is tempting here -- then re-read Part 6."
