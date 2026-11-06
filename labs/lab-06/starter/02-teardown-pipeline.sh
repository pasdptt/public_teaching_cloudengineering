#!/usr/bin/env bash
# The last rows of the teardown order: remove what 01-bootstrap-pipeline.sh created.
#
# RUN THIS IN WEEK 15, NOT AT THE END OF LAB 6. Your project deploys through this pipeline in
# weeks 14-15, and a deleted pool's id cannot be reused for 30 days -- so removing it after Lab
# 6 would break the project. Run it last of all: after `terraform destroy` for both
# environments and after the Artifact Registry images are gone. Deleting the state bucket while
# Terraform still owns resources leaves you cleaning up from memory, in a console.
#
# STATUS: NOT YET RUN AGAINST A REAL PROJECT (see 01-bootstrap-pipeline.sh).
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck disable=SC1091
source config.env
say() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
DEPLOYER="${DEPLOYER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
STATE_BUCKET="${PROJECT_ID}-tfstate"

read -r -p "Is this week 15, with BOTH environments destroyed and the registry images deleted? [y/N] " ok
[[ "$ok" == "y" ]] || { echo "Stopping. Destroy them first: the state bucket goes last." >&2; exit 1; }

say "Removing the deployer's project roles, then the deployer itself"
for role in roles/run.admin roles/iam.serviceAccountAdmin roles/iam.serviceAccountUser \
            roles/resourcemanager.projectIamAdmin roles/storage.admin roles/pubsub.admin \
            roles/artifactregistry.repoAdmin; do
  gcloud projects remove-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${DEPLOYER}" --role="$role" --condition=None --quiet >/dev/null || true
done
gcloud iam service-accounts delete "$DEPLOYER" --project="$PROJECT_ID" --quiet

say "Removing the federation pool (its provider goes with it)"
# A deleted pool is kept, recoverable, for 30 days and its id cannot be reused in that time.
gcloud iam workload-identity-pools delete "$POOL_ID" --project="$PROJECT_ID" --location=global --quiet

say "Removing the state bucket -- last, and including old object versions"
gcloud storage rm --recursive --all-versions "gs://${STATE_BUCKET}/**" || true
gcloud storage buckets delete "gs://${STATE_BUCKET}"

say "Now verify independently, with operations/cleanup.md. This script deleting a thing is a claim, not proof."
