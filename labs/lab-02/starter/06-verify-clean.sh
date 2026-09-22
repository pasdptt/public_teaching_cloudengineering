#!/usr/bin/env bash
# Prove that nothing billable remains. THIS IS THE GRADED STEP.
#
# Deleting is a command you ran. Verifying is evidence that it worked. They are not the
# same thing, and the gap between them is where surprise bills live.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud

fail=0
check() { # check "<label>" "<command>"
  local label="$1" out
  shift
  out="$("$@" 2>/dev/null || true)"
  if [[ -z "$out" ]]; then
    printf '  \033[32mCLEAN\033[0m  %s\n' "$label"
  else
    printf '  \033[31mLEFT\033[0m   %s\n' "$label"
    sed 's/^/           /' <<<"$out"
    fail=1
  fi
}

say "Verifying nothing remains in ${PROJECT_ID}"

check "compute instances" \
  gcloud compute instances list --project="$PROJECT_ID" --format="value(name,zone,status)"

check "firewall rules (docapp)" \
  gcloud compute firewall-rules list --project="$PROJECT_ID" \
    --filter="name~docapp" --format="value(name,sourceRanges.list())"

# TODO(lab02): add the checks that matter most -- the resources that SURVIVE a deleted VM.
#
# Three of them can cost money after the instance is gone. Work out which, then write a
# check for each. `gcloud compute --help` lists the resource types; the ones you want are
# in operations/cost-model.md section 6.
#
# Hints, not answers:
#   * something that stores your filesystem and can outlive the machine using it
#   * something scarce enough that the provider charges MORE for it when it is idle
#   * something that is a copy of the first thing, made at a point in time
#
# check "..."  gcloud compute ________ list --project="$PROJECT_ID" --format="value(name)"

check "service accounts (docapp)" \
  gcloud iam service-accounts list --project="$PROJECT_ID" \
    --filter="email~${SERVICE_ACCOUNT_NAME}" --format="value(email)"

echo
if [[ $fail -eq 0 ]]; then
  say "Everything checked is clean."
  note "Paste this whole output into your submission."
else
  say "Something is still there."
  note "Do not submit until this is clean -- and find out WHY it survived. That reason"
  note "is worth more to you than the four cents."
  exit 1
fi
