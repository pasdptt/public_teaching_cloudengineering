output "service_url" {
  description = "Public URL of the deployed service."
  value       = google_cloud_run_v2_service.app.uri
}

output "bucket_name" {
  description = "Document storage bucket for this environment."
  value       = google_storage_bucket.documents.name
}

output "runtime_service_account" {
  description = "The identity the service runs as."
  value       = google_service_account.runtime.email
}

output "topic_name" {
  description = "The work topic this environment publishes to."
  value       = google_pubsub_topic.jobs.name
}

output "subscription_name" {
  description = "The push subscription. The resource to check twice before you walk away."
  value       = google_pubsub_subscription.jobs_push.name
}

output "push_service_account" {
  description = "The identity Pub/Sub calls the service as. Not the one the service runs as."
  value       = google_service_account.push.email
}

output "environment" {
  description = "Which environment this state represents. Check it before you destroy anything."
  value       = var.environment
}
