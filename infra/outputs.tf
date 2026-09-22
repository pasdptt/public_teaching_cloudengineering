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

output "environment" {
  description = "Which environment this state represents. Check it before you destroy anything."
  value       = var.environment
}
