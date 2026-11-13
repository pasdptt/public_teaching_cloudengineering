#!/usr/bin/env bash
# Lab 6 Part 4 -- give the pipeline an identity without a key, and make somewhere for
# Terraform's state to live.
#
# SUPPLIED SINCE LAB 6 BECAME A ONE-WEEK LAB (decisions.md D-67). Read every block before you
# run it: Part 4's three marked questions are about what this script does, not about typing it.
#
# STATUS: NOT YET RUN AGAINST A REAL PROJECT. The commands follow Google's documented
# Workload Identity Federation setup for GitHub Actions, but nothing in this course has been
# executed against a live project yet (README.md "Status"). If a command fails, the error
# message and the current documentation decide -- not this script.
#
# What it creates, all in your one project:
#   1. a workload identity pool and an OIDC provider that trusts GitHub -- for ONE repository
#   2. a deployer service account, with the roles the pipeline needs
#   3. the binding that lets workflows from that repository act as the deployer
#   4. the Terraform state bucket, with versioning on
# What it never creates: a service-account key.
set -euo pipefail
cd "$(dirname "$0")"
[[ -f config.env ]] || { echo "ERROR: copy config.env.example to config.env and fill it in" >&2; exit 1; }
# shellcheck disable=SC1091
source config.env
[[ "$PROJECT_ID" != "your-project-id-here" ]] || { echo "ERROR: set PROJECT_ID in config.env" >&2; exit 1; }
[[ "$GITHUB_REPO" == */* && "$GITHUB_REPO" != "your-github-user/your-repo" ]] \
  || { echo "ERROR: set GITHUB_REPO to owner/name in config.env" >&2; exit 1; }

say() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
DEPLOYER="${DEPLOYER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
STATE_BUCKET="${PROJECT_ID}-tfstate"

say "Enabling the APIs federation needs (free)"
gcloud services enable iam.googleapis.com iamcredentials.googleapis.com sts.googleapis.com \
  cloudresourcemanager.googleapis.com --project="$PROJECT_ID"

say "1. The pool, and a provider that trusts GitHub's OIDC tokens"
gcloud iam workload-identity-pools create "$POOL_ID" \
  --project="$PROJECT_ID" --location=global --display-name="GitHub Actions"

# The attribute condition is the answer to Part 4's first question. Without it, ANY GitHub
# repository's workflow could present a token this provider accepts. With it, only tokens
# whose `repository` claim is exactly yours are exchanged at all.
gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_ID" \
  --project="$PROJECT_ID" --location=global --workload-identity-pool="$POOL_ID" \
  --display-name="GitHub Actions" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository == '${GITHUB_REPO}'"

say "2. The deployer service account, and its roles"
gcloud iam service-accounts create "$DEPLOYER_SA_NAME" \
  --project="$PROJECT_ID" --display-name="docapp pipeline deployer"

# Part 4 asks you to justify each of these and name the one you would most like to remove.
# Together they make this the most powerful principal in your project -- see the end of
# deploy.yml.
for role in \
  roles/run.admin \
  roles/iam.serviceAccountAdmin \
  roles/iam.serviceAccountUser \
  roles/resourcemanager.projectIamAdmin \
  roles/storage.admin \
  roles/pubsub.admin \
  roles/artifactregistry.repoAdmin
do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${DEPLOYER}" --role="$role" --condition=None --quiet >/dev/null
  echo "    granted $role"
done

say "3. Let workflows from ${GITHUB_REPO} -- and only those -- act as the deployer"
gcloud iam service-accounts add-iam-policy-binding "$DEPLOYER" \
  --project="$PROJECT_ID" --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository/${GITHUB_REPO}"

say "4. The state bucket (bootstrapping: Terraform cannot create its own state's home)"
gcloud storage buckets create "gs://${STATE_BUCKET}" \
  --project="$PROJECT_ID" --location="$REGION" \
  --uniform-bucket-level-access --public-access-prevention
gcloud storage buckets update "gs://${STATE_BUCKET}" --versioning

PROVIDER_NAME="$(gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
  --project="$PROJECT_ID" --location=global --workload-identity-pool="$POOL_ID" \
  --format='value(name)')"

say "Done. Put these three values in .github/workflows/deploy.yml"
echo "    workload_identity_provider: '${PROVIDER_NAME}'"
echo "    service_account:            '${DEPLOYER}'"
echo "    STATE_BUCKET:               '${STATE_BUCKET}'"
echo
echo "    None of them is a secret. Part 4 asks you why."
echo "    Next: uncomment the backend block in infra/versions.tf and run terraform init -migrate-state."
