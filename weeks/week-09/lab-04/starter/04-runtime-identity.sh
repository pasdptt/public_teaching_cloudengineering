#!/usr/bin/env bash
# Create the identity the deployed service runs as, and grant it what it needs.
#
# Lab 2 gave a VM a service account. This does the same for managed execution, and the
# reasoning is identical: the thing that runs is a principal, and a principal with no
# stated permissions can do nothing -- which is the correct place to start from.
#
# There is a default service account you could use instead. Look up what it is granted by
# default before you decide that would have been fine.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud

BUCKET_NAME="${BUCKET_NAME:-${PROJECT_ID}-docapp-lab4}"
SA_EMAIL="${RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

say "Creating service account ${SA_EMAIL}"
if gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" >/dev/null 2>&1; then
  note "Already exists. Reusing it."
else
  gcloud iam service-accounts create "$RUNTIME_SA_NAME" \
    --display-name="docapp runtime (Lab 4)" \
    --project="$PROJECT_ID"
fi

# ---------------------------------------------------------------------------------------
# TODO(lab04): grant this identity the permissions the application actually needs.
#
# The application does exactly three things that touch a Google service:
#   * writes and reads objects in gs://${BUCKET_NAME}
#   * reads and writes documents in the project's (default) Firestore database
#   * writes log entries
#
# For each one, work out the smallest role that covers it, and grant it at the smallest
# scope that works. Two of these can be granted on the bucket rather than on the project;
# one cannot, and part of the exercise is finding out which and saying why.
#
# Fill in the commands below. Some starting points, none of which are the answer:
#
#   gcloud storage buckets add-iam-policy-binding "gs://${BUCKET_NAME}" \
#     --member="serviceAccount:${SA_EMAIL}" \
#     --role="roles/REPLACE_ME" \
#     --project="$PROJECT_ID"
#
#   gcloud projects add-iam-policy-binding "$PROJECT_ID" \
#     --member="serviceAccount:${SA_EMAIL}" \
#     --role="roles/REPLACE_ME"
#
# Do NOT reach for roles/editor or roles/owner. They will work. Band C of the rubric is
# about the difference between "it worked" and "I can say what it can do", and a wildcard
# role means you cannot say.
#
# Record, in your submission, every role you granted and the one sentence of justification
# each one needs.
# ---------------------------------------------------------------------------------------

say "Current bindings for this identity (should be empty until you fill in the TODO):"
gcloud projects get-iam-policy "$PROJECT_ID" \
  --flatten="bindings[].members" \
  --filter="bindings.members:${SA_EMAIL}" \
  --format="table(bindings.role)" || true

note "No key file was created, and none is needed. The service account is ATTACHED to the"
note "service; the platform supplies short-lived credentials at runtime. A downloaded key"
note "would be a permanent credential in your filesystem, and is an automatic zero in"
note "band C of every rubric in this course."
