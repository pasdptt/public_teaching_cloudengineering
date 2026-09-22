#!/usr/bin/env bash
# Shared helpers. Sourced by every script in this directory.
#
# Deliberately close to labs/lab-02/starter/lib.sh. The guard rails that mattered for a VM
# still matter here, and two of them are new -- because the two ways to leave the free tier
# on managed execution are both single flags on a single command.
set -euo pipefail

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
      echo "  Cloud Run's free allowance is not regional, but Cloud Storage's is, and" >&2
      echo "  putting the service in one region and its bucket in another adds a" >&2
      echo "  cross-region hop to every request you are about to measure." >&2
      exit 1
      ;;
  esac
}

# Guard rail, and the single most important one in this lab.
#
# A Cloud Run service with min-instances=0 and no traffic costs exactly nothing: there is
# no charge for a service merely existing. Set it to 1 and you have bought an always-on
# instance, billed per second, whether or not anyone calls it -- which is request-priced
# execution converted back into a rented machine, at a worse price than the VM in Lab 2.
require_zero_min_instances() {
  if [[ "${MIN_INSTANCES:-0}" != "0" ]]; then
    echo "ERROR: MIN_INSTANCES='${MIN_INSTANCES}' but this lab requires 0." >&2
    echo "  A non-zero minimum is billed continuously. If a later exercise genuinely" >&2
    echo "  needs a warm instance, change it deliberately, for one measurement, and" >&2
    echo "  put it back -- and say so in your submission." >&2
    exit 1
  fi
}

# Guard rail. The maximum is the blast radius of a mistake in your load generator.
require_bounded_max_instances() {
  local max="${MAX_INSTANCES:-}"
  if [[ ! "$max" =~ ^[0-9]+$ ]] || (( max < 1 )); then
    echo "ERROR: MAX_INSTANCES='${max}' is not a positive whole number." >&2
    exit 1
  fi
  if (( max > 10 )); then
    echo "ERROR: MAX_INSTANCES=${max} is higher than this lab allows (10)." >&2
    echo "  Nothing in Lab 4 needs more, and an unbounded maximum means a runaway" >&2
    echo "  client can spend your allowance in the time it takes to notice." >&2
    exit 1
  fi
}

say()  { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
note() { printf '    %s\n' "$*"; }
