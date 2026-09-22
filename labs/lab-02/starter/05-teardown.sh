#!/usr/bin/env bash
# Remove everything this lab created.
#
# Deleting the instance, not stopping it. A stopped instance still has a disk, and if its
# address were static it would still have that too.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud

say "Deleting instance ${INSTANCE_NAME} (and its boot disk)"
gcloud compute instances delete "$INSTANCE_NAME" \
  --project="$PROJECT_ID" --zone="$ZONE" --quiet 2>/dev/null \
  || note "not found, continuing"

say "Deleting firewall rule ${FIREWALL_RULE_NAME}"
gcloud compute firewall-rules delete "$FIREWALL_RULE_NAME" \
  --project="$PROJECT_ID" --quiet 2>/dev/null || note "not found, continuing"

say "Deleting service account ${SERVICE_ACCOUNT_NAME}"
gcloud iam service-accounts delete \
  "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --project="$PROJECT_ID" --quiet 2>/dev/null || note "not found, continuing"

say "Teardown commands issued."
note "Issued is not verified. Run ./06-verify-clean.sh -- that is the graded part."
