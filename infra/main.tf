# The docapp environment: everything one deployment needs, as a single declarative unit.
#
# Read the resource names. Every one carries var.environment, which is what lets dev and
# prod coexist in one project without colliding. That is also the limit of this approach --
# see the note at the bottom of infra/README.md about what CANNOT be separated this way.
#
# This file is the whole of Labs 2 to 5 said once, declaratively. You created every one of
# these resources by hand, from a shell script, over eight weeks. Count the lines it took
# then and the lines it takes here, and then count the number of steps you could forget.

# The project's number, needed to name Google's own service agents. Reading it rather than
# hard-coding it is what lets this configuration move to another project unchanged.
data "google_project" "this" {}

locals {
  name = "docapp-${var.environment}"

  # Google creates a service agent for Pub/Sub in every project that uses it. It is the
  # identity Pub/Sub itself acts as -- not yours, not your service's -- and two of the
  # grants below are made to it. This is the account behind the "second grant" that
  # surprises everyone in Lab 5.
  pubsub_agent = "serviceAccount:service-${data.google_project.this.number}@gcp-sa-pubsub.iam.gserviceaccount.com"

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

# --- The queue ---------------------------------------------------------------------------
# Lab 5, declared. You created these with four gcloud commands and two IAM grants you had
# to discover from an error message; here they are a dependency graph Terraform works out.

resource "google_pubsub_topic" "jobs" {
  name   = "${local.name}-jobs"
  labels = local.labels
}

# Where a message goes when it has failed too many times. A separate topic, because the
# whole point is that it is somewhere a human looks rather than somewhere work continues.
resource "google_pubsub_topic" "dead_letter" {
  name   = "${local.name}-jobs-dead"
  labels = local.labels
}

# The identity Pub/Sub calls the service with. NOT the identity the service runs as, and
# keeping them apart is the point: one may publish and process, the other may only knock on
# the door.
resource "google_service_account" "push" {
  account_id   = "${local.name}-push"
  display_name = "docapp ${var.environment} Pub/Sub push caller"
  description  = "Identity Pub/Sub authenticates as when delivering to the ${var.environment} service"
}

resource "google_pubsub_subscription" "jobs_push" {
  name   = "${local.name}-jobs-push"
  topic  = google_pubsub_topic.jobs.id
  labels = local.labels

  # Retained messages are billable storage, and a subscription nobody reads is the one way
  # this course leaves a bill behind (operations/cleanup.md). Bounded deliberately.
  message_retention_duration = "${var.message_retention_seconds}s"
  ack_deadline_seconds       = var.ack_deadline_seconds

  push_config {
    push_endpoint = "${google_cloud_run_v2_service.app.uri}/tasks/process"

    # This is what lets a private service accept a call from the broker: Pub/Sub mints an
    # OIDC token as the push account, and Cloud Run checks it like any other caller.
    oidc_token {
      service_account_email = google_service_account.push.email
      audience              = google_cloud_run_v2_service.app.uri
    }
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = var.max_delivery_attempts
  }

  retry_policy {
    # Backoff, declared. Without a retry policy Pub/Sub redelivers on a fixed schedule,
    # which is week 10's retry storm waiting to happen.
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  # One of the two dead-letter grants must exist BEFORE this subscription, and nothing in
  # the arguments says so -- the publisher grant is made on a different topic, so Terraform
  # sees no connection and is free to do them in the wrong order. Declaring it explicitly
  # is what stops a first apply failing and a second one succeeding, which is the most
  # confusing class of bug this tool produces.
  #
  # The OTHER grant cannot be listed here, and the reason is worth a minute: it is made on
  # this subscription, so requiring it first would mean the subscription depends on
  # something that depends on the subscription. Terraform rejects that as a cycle, and it
  # is right to -- the grant genuinely can only happen afterwards. Both land in a single
  # apply; the ordering constraint is real in only one direction.
  depends_on = [google_pubsub_topic_iam_member.agent_publishes_dead_letter]
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

# Scoped to THIS environment's topic, for the same reason.
resource "google_pubsub_topic_iam_member" "runtime_publishes" {
  topic  = google_pubsub_topic.jobs.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.runtime.email}"
}

# ...and here is the exception, which is the most instructive line in this file.
#
# Firestore access cannot be scoped to one database through this role: it is granted on the
# PROJECT. So the dev service can read and write the same Firestore data as prod, and no
# amount of naming resources carefully changes that. The separation you get from
# var.environment is real for buckets, topics and services, and it stops here.
#
# Lab 6 Part 3 asks what could go wrong and what you would do about it. The honest answer
# involves a second project, and a second project means a second free tier, which is a cost
# conversation rather than a technical one.
resource "google_project_iam_member" "runtime_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

# --- The service -------------------------------------------------------------------------
resource "google_cloud_run_v2_service" "app" {
  name     = local.name
  location = var.region
  labels   = local.labels

  # All ingress is permitted at the network level; the IAM binding below is what decides
  # who may actually invoke it. Two different controls, and conflating them is how services
  # end up public by accident.
  ingress = "INGRESS_TRAFFIC_ALL"

  # Terraform would otherwise try to replace the service while a subscription is pushing to
  # it. Nothing breaks permanently, but the apply is slower and the errors are confusing.
  deletion_protection = false

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
      #
      # Every other variable the application reads is set explicitly, including the ones
      # whose default would have been fine. A configuration that relies on a default is a
      # configuration that changes when somebody else edits config.py.
      env {
        name  = "DOCAPP_STORAGE"
        value = "gcs"
      }
      env {
        name  = "DOCAPP_BUCKET"
        value = google_storage_bucket.documents.name
      }
      # Lab 3's job store. Without this the service would run on the in-memory one, which
      # works perfectly on one instance and is the exact bug Lab 4 spent a week on.
      env {
        name  = "DOCAPP_JOBSTORE"
        value = "firestore"
      }
      env {
        name  = "DOCAPP_PROJECT_ID"
        value = var.project_id
      }
      # Lab 5's queue.
      env {
        name  = "DOCAPP_QUEUE"
        value = "pubsub"
      }
      env {
        name  = "DOCAPP_QUEUE_TOPIC"
        value = google_pubsub_topic.jobs.name
      }
      env {
        name  = "DOCAPP_PROCESSING_DELAY_MS"
        value = tostring(var.processing_delay_ms)
      }
      env {
        name  = "DOCAPP_LOG_LEVEL"
        value = var.log_level
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
# The service is PRIVATE. It has no allUsers binding and it will refuse an anonymous caller
# with 403, exactly as it did in Labs 4 and 5. The only principal granted invoke rights is
# the broker's push identity, and only on THIS service.
resource "google_cloud_run_v2_service_iam_member" "push_may_invoke" {
  name     = google_cloud_run_v2_service.app.name
  location = google_cloud_run_v2_service.app.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.push.email}"
}

# TODO(lab06): you cannot curl this service yet, and that is correct rather than broken.
#
# Grant yourself, or your pipeline's deployer account, the narrowest invoke permission that
# lets the smoke test in deploy.yml work. Then answer in your submission:
#
#   * which principal did you grant, and at what scope?
#   * what would change if you granted roles/run.invoker to allUsers instead -- name two
#     things, one of which is not "anyone could use it";
#   * should dev and prod have the same answer here? This is the best candidate in the file
#     for something that SHOULD differ between environments.

# --- The two grants Pub/Sub needs to make on its own behalf ------------------------------
#
# These are the ones that defeat people in Lab 5, discovered from an error message halfway
# through a session. They are not exotic: Pub/Sub is a service that acts, so it has an
# identity, and it needs permission like anything else.

# So the broker may authenticate as the push account when it calls the service.
resource "google_service_account_iam_member" "agent_mints_push_tokens" {
  service_account_id = google_service_account.push.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = local.pubsub_agent
}

# So the broker may put a failed message on the dead-letter topic...
resource "google_pubsub_topic_iam_member" "agent_publishes_dead_letter" {
  topic  = google_pubsub_topic.dead_letter.name
  role   = "roles/pubsub.publisher"
  member = local.pubsub_agent
}

# ...and may acknowledge the original once it has done so. Both are required; granting only
# the first produces a dead-letter policy that silently never fires, which is worse than
# not having one.
resource "google_pubsub_subscription_iam_member" "agent_subscribes" {
  subscription = google_pubsub_subscription.jobs_push.name
  role         = "roles/pubsub.subscriber"
  member       = local.pubsub_agent
}
