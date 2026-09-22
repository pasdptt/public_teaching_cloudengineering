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

  # State is local, and stays local for week 12. That is fine for one student on one
  # machine and wrong for a team -- two people applying against separate local state files
  # will fight, and neither will be told.
  #
  # In week 13 it stops being a matter of taste. A pipeline runs on a fresh machine every
  # time, so local state is EMPTY on every run: the second deploy tries to create
  # everything again and fails on resources that already exist. The pipeline is the second
  # actor the paragraph above was warning about, and it arrives whether you invited it or
  # not.
  #
  # Lab 6 Part 4 has you uncomment this and migrate. Note what is deliberately absent from
  # it: the bucket name. It is supplied with `-backend-config` at init time, because a
  # backend block may not use variables at all -- which is itself a consequence of the
  # chicken-and-egg problem below.
  #
  # And the chicken and egg: this bucket CANNOT be created by this configuration. Terraform
  # needs somewhere to put state before it can create anything, including the somewhere.
  # So it is made by hand, once, with a gcloud command, and that is not a workaround -- it
  # is what every team does, and the usual name for it is bootstrapping.
  #
  # backend "gcs" {
  #   prefix = "docapp"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
