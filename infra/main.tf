# The docapp environment: everything one deployment needs, as a single declarative unit.
#
# Read the resource names. Every one carries var.environment, which is what lets dev and
# prod coexist in one project without colliding. That is also the limit of this approach --
# see the note at the bottom of infra/README.md about what CANNOT be separated this way.

locals {
  name = "docapp-${var.environment}"

  # Labels are how you answer "what is this, and who is it for?" three months later, and
  # how a billing report can be split by environment. Cheap to add now, impossible to
  # backfill onto resources that have already been deleted.
  labels = {
    application = "docapp"
    environment = var.environment
    managed-by  = "terraform"
    course      = "cloud-computing"
  }
}

# --- Where document bytes live -----------------------------------------------------------
# Regional, in a free-tier region, inside the 5 GB-month allowance.
resource "google_storage_bucket" "documents" {
  name     = "${var.project_id}-${local.name}-documents"
  location = upper(var.region)
  labels   = local.labels

  # Applies to a BUCKET, not to the objects -- deleting a bucket with objects in it fails
  # unless force_destroy is set. In dev that is a convenience. In prod it is a loaded gun,
  # which is exactly why it is wired to the environment rather than hard-coded.
  force_destroy = var.environment == "dev"

  uniform_bucket_level_access = true

  # Public access is off by default; this makes it explicit and unmissable in review.
  public_access_prevention = "enforced"

  lifecycle_rule {
    condition {
      age = 7
    }
    action {
      type = "Delete"
    }
  }
}

# --- The identity the service runs as ----------------------------------------------------
resource "google_service_account" "runtime" {
  account_id   = "${local.name}-run"
  display_name = "docapp ${var.environment} runtime"
  description  = "Least-privilege identity for the ${var.environment} Cloud Run service"
}

# Scoped to THIS environment's bucket, not to the project. A dev service that could read
# prod's bucket would make the environment separation decorative.
resource "google_storage_bucket_iam_member" "runtime_documents" {
  bucket = google_storage_bucket.documents.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.runtime.email}"
}

# --- The service -------------------------------------------------------------------------
resource "google_cloud_run_v2_service" "app" {
  name     = local.name
  location = var.region
  labels   = local.labels

  # Cloud Run v2 requires this to be set explicitly for public services; the IAM binding
  # below is what actually decides who may invoke it.
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.runtime.email

    scaling {
      # min_instance_count = 0 is what keeps this free. Above zero and you are buying an
      # always-on instance whether or not anyone calls it (course/references.md R-12).
      min_instance_count = 0
      max_instance_count = var.max_instances
    }

    containers {
      # Built once, promoted unchanged. Never rebuilt per environment -- rebuild and you
      # are deploying something you did not test.
      image = var.image

      # PORT is injected by Cloud Run itself, so it is deliberately absent here.
      env {
        name  = "DOCAPP_STORAGE"
        value = "gcs"
      }
      env {
        name  = "DOCAPP_BUCKET"
        value = google_storage_bucket.documents.name
      }
      env {
        name  = "DOCAPP_PROCESSING_DELAY_MS"
        value = tostring(var.processing_delay_ms)
      }
      env {
        name  = "DOCAPP_LOG_LEVEL"
        value = var.log_level
      }
      env {
        name  = "DOCAPP_INSTANCE_ID"
        value = "" # Cloud Run gives each instance its own; the app falls back to a generated id
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      startup_probe {
        http_get {
          path = "/healthz"
        }
        initial_delay_seconds = 2
        timeout_seconds       = 3
        period_seconds        = 3
        failure_threshold     = 5
      }
    }
  }

  # TODO(lab06): nothing here distinguishes how much this environment is allowed to cost
  # beyond max_instances. Add the variable you invented in variables.tf, wire it in, and
  # explain in your submission what it protects.
}

# --- Who may call it ---------------------------------------------------------------------
# TODO(lab06): this makes the service PUBLIC. That is right for a course lab you need to
# curl from your laptop, and it is a decision, not a default.
#
# Answer in your submission: what would you change for a prod service that only your own
# pipeline and a known front end should reach? Name the member you would use instead of
# "allUsers", and say what breaks when you do.
resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.app.name
  location = google_cloud_run_v2_service.app.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
