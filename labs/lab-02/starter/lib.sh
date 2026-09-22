#!/usr/bin/env bash
# Shared helpers. Sourced by every script in this directory.
set -euo pipefail

here() { cd "$(dirname "${BASH_SOURCE[1]}")" && pwd; }

load_config() {
  local dir; dir="$(cd "$(dirname "${BASH_SOURCE[1]}")" && pwd)"
  if [[ ! -f "$dir/config.env" ]]; then
    echo "ERROR: $dir/config.env not found." >&2
    echo "  cp config.env.example config.env    # then edit PROJECT_ID" >&2
    exit 1
  fi
  # shellcheck disable=SC1090
  source "$dir/config.env"
  : "${PROJECT_ID:?PROJECT_ID must be set in config.env}"
  if [[ "$PROJECT_ID" == "your-project-id-here" ]]; then
    echo "ERROR: edit config.env and set your real PROJECT_ID." >&2
    exit 1
  fi
}

require_gcloud() {
  command -v gcloud >/dev/null 2>&1 || {
    echo "ERROR: gcloud is not installed or not on PATH. See Lab 2 Part 0." >&2
    exit 1
  }
}

# Guard rail. Everything in this course must stay in a free-tier region.
require_free_tier_region() {
  case "${REGION:-}" in
    us-west1|us-central1|us-east1) : ;;
    *)
      echo "ERROR: REGION='${REGION:-unset}' is outside the Always Free regions." >&2
      echo "  The free e2-micro and Cloud Storage allowances exist only in" >&2
      echo "  us-west1, us-central1 and us-east1. Running here would bill." >&2
      exit 1
      ;;
  esac
}

say()  { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
note() { printf '    %s\n' "$*"; }
