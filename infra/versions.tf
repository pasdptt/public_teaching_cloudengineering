# Provider and version pinning.
#
# Pinned deliberately. An infrastructure configuration that silently picks up a new major
# provider version is not reproducible, and "it worked last week" is the worst possible
# thing to discover during a deployment.
#
# hashicorp/google is on the 8.x line as of 2026-09 (course/references.md R-03). Version
# 8.0.0 contained breaking changes, so ~> 8.0 is a real constraint, not decoration.

terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 8.0"
    }
  }

  # State is local for this course. That is fine for one student on one machine and wrong
  # for a team -- two people applying against separate local state files will fight, and
  # neither will know. Lab 6 asks you what a shared backend would change.
  #
  # backend "gcs" {
  #   bucket = "your-tfstate-bucket"
  #   prefix = "docapp"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
