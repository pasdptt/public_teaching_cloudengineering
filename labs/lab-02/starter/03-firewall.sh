#!/usr/bin/env bash
# Create or update the rule that decides who may reach port 8080.
#
#   ./03-firewall.sh                                  # uses the TODO default below
#   ./03-firewall.sh --source-range 203.0.113.4/32    # only that address
source "$(dirname "$0")/lib.sh"
load_config

SOURCE_RANGE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-range) SOURCE_RANGE="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$SOURCE_RANGE" ]]; then
  # TODO(lab02): choose the default source range.
  #
  # 0.0.0.0/0 means the entire internet. It is the fastest way to make the lab work and it
  # is a standing invitation. Your own address (curl -sS https://api.ipify.org) is narrow
  # and breaks when your address changes -- which, on a home or campus network, it will.
  #
  # Pick one. Then justify it in your submission, including what you would choose for a
  # service that real users had to reach, and why that is a different question.
  SOURCE_RANGE="CHOOSE_ME"
fi

if [[ "$SOURCE_RANGE" == "CHOOSE_ME" ]]; then
  echo "ERROR: edit 03-firewall.sh and choose a default source range (see the TODO)," >&2
  echo "       or pass --source-range explicitly." >&2
  exit 1
fi

require_gcloud

say "Allowing tcp:${APP_PORT} from ${SOURCE_RANGE} to instances tagged 'docapp'"

if gcloud compute firewall-rules describe "$FIREWALL_RULE_NAME" \
     --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud compute firewall-rules update "$FIREWALL_RULE_NAME" \
    --project="$PROJECT_ID" --source-ranges="$SOURCE_RANGE"
else
  gcloud compute firewall-rules create "$FIREWALL_RULE_NAME" \
    --project="$PROJECT_ID" \
    --direction=INGRESS \
    --action=ALLOW \
    --rules="tcp:${APP_PORT}" \
    --source-ranges="$SOURCE_RANGE" \
    `# The rule applies only to instances carrying this tag, not to the whole network.` \
    `# Scoping by target is the difference between "a door" and "a door in every wall".` \
    --target-tags="docapp" \
    --description="Lab 2: reach docapp on ${APP_PORT}"
fi

gcloud compute firewall-rules describe "$FIREWALL_RULE_NAME" --project="$PROJECT_ID" \
  --format="yaml(name, direction, sourceRanges, targetTags, allowed)"
